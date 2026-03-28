# Modelagem Detalhada: App de Tarefas (MVP)

Esta arquitetura detalha a modelagem do app `tasks` focando no padrão "Service Layer" integrado ao Django REST Framework, com ênfase absoluta nas regras de negócio estritas de `Workspace`.

## 1. Regras de Domínio Consolidadas
1. **Workspace como Isolamento Absoluto:** Todo dado da API de produtividade está sob a barreira de um Workspace.
2. **Assignee Boundary (Regra Explícita):** Um usuário só pode ser `assignee` de uma tarefa se possuir um `WorkspaceMembership` ativo no workspace da referida tarefa.
3. **Eventos Explícitos (No Magic):** Ao finalizar uma tarefa ou sessão de foco, o Service Layer invocará um *Handler* público do app `gamification`, em vez de depender de sinais implícitos do Django. A transação unificada garante atomicidade.
4. **Tags Nativas:** Tags pertencem ao Workspace para manter consistência de relatórios, filtros e paleta de cores da empresa/usuário.
5. **Focus Sessions:** Enriquecido para suportar analytics futuras (`started_at`, `ended_at`, `source`, `workspace_id`).

---

## 2. Models (`tasks/models.py` e `focus/models.py`)

A modelagem de dados estipula dependências rígidas para garantir o roteamento correto e isolado.

```python
# tasks/models.py

class Tag(models.Model):
    workspace = models.ForeignKey('workspaces.Workspace', on_delete=models.CASCADE, related_name='tags')
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=7) # Hex code

class Bucket(models.Model):
    workspace = models.ForeignKey('workspaces.Workspace', on_delete=models.CASCADE, related_name='buckets')
    name = models.CharField(max_length=100)
    order_index = models.PositiveIntegerField(default=0)

class Task(models.Model):
    class Status(models.TextChoices):
        TODO = 'TODO', 'To Do'
        DOING = 'DOING', 'Doing'
        DONE = 'DONE', 'Done'

    bucket = models.ForeignKey(Bucket, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.TODO)
    due_date = models.DateField(null=True, blank=True)
    
    # Assignee pode ser nulo (tarefa não atribuída)
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks'
    )
    tags = models.ManyToManyField(Tag, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

class Subtask(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='subtasks')
    title = models.CharField(max_length=255)
    is_done = models.BooleanField(default=False)
```

```python
# focus/models.py

class FocusSession(models.Model):
    class Source(models.TextChoices):
        WEB = 'WEB', 'Web App'
        MOBILE = 'MOBILE', 'Mobile App'
        LOCAL_AGENT = 'AGENT', 'Local Blocker Agent'

    class Status(models.TextChoices):
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='focus_sessions')
    workspace = models.ForeignKey('workspaces.Workspace', on_delete=models.SET_NULL, null=True, blank=True)
    task = models.ForeignKey('tasks.Task', on_delete=models.SET_NULL, null=True, blank=True)
    
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField()
    duration_seconds = models.PositiveIntegerField()
    
    source = models.CharField(max_length=20, choices=Source.choices, default=Source.WEB)
    status_result = models.CharField(max_length=20, choices=Status.choices)
    
    created_at = models.DateTimeField(auto_now_add=True)
```

---

## 3. Permissões DRF (`tasks/permissions.py`)

Para evitar *Tenant Leakage* (vazamento de dados) proativamente.

```python
from rest_framework.permissions import BasePermission

class IsWorkspaceMember(BasePermission):
    """
    Verifica se o usuário requisitante possui um WorkspaceMembership
    valido e ativo para o Workspace em questão.
    """
    def has_permission(self, request, view):
        # Usaremos Nested Routers, então o workspace_pk estará sempre na URL
        workspace_id = view.kwargs.get('workspace_pk')
        if not workspace_id:
            return False
            
        return WorkspaceMembership.objects.filter(
            workspace_id=workspace_id, 
            user=request.user
        ).exists()
        
    def has_object_permission(self, request, view, obj):
        # Garante que o objeto manipulado enforca o acesso correto
        # (Ideal quando obj tem propriedade ou relação com workspace)
        workspace = getattr(obj, 'workspace', None) or obj.bucket.workspace
        return WorkspaceMembership.objects.filter(
            workspace=workspace,
            user=request.user
        ).exists()
```

---

## 4. DRF Serializers (`tasks/serializers.py`)

Garantindo nosso objetivo de **Anti-Fat Serializers**. Eles servem estritamente para conversão DTO (Data Transfer Object) e validações básicas de tipo e required fields.

```python
class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            'id', 'bucket', 'title', 'description', 'status', 
            'due_date', 'assignee', 'tags', 'created_at', 'completed_at'
        ]
        read_only_fields = ['id', 'created_at', 'completed_at']
```

---

## 5. Service Layer (`tasks/services.py`)

Isolamento da transação e garantia explícita das regras. Nenhuma "mágica", tudo pode ser lido de cima a baixo ("Explicit is better than implicit").

```python
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from gamification.handlers import handle_task_completion_rewards

def assign_task(user_assigning, task: Task, assignee_id: int) -> Task:
    """ Regra de Domínio #3 (Assignee Boundary) """
    is_member = WorkspaceMembership.objects.filter(
        workspace=task.bucket.workspace,
        user_id=assignee_id
    ).exists()
    
    if not is_member:
        raise ValidationError("O usuário atribuído deve pertencer ao Workspace da tarefa.")
        
    task.assignee_id = assignee_id
    task.save(update_fields=['assignee'])
    return task

@transaction.atomic
def complete_task(user, task_id: int) -> Task:
    task = Task.objects.select_related('bucket__workspace').get(id=task_id)
    
    if task.status == Task.Status.DONE:
        return task # Idempotência

    task.status = Task.Status.DONE
    task.completed_at = timezone.now()
    task.save(update_fields=['status', 'completed_at', 'updated_at'])
    
    # [Regra de Domínio #5] Controle explícito em vez de Signals "mágicos"
    # Chamada clara do handler. Pode ser em background via Celery no futuro.
    handle_task_completion_rewards(user=user, task=task)
    
    return task
```

---

## 6. Endpoints Principais (Nested Routing)

A arquitetura de injeção direta via URL bloqueia erros e facilita muito a listagem natural. Uso da library `drf-nested-routers`.

**Rotas Designadas:**
* `GET/POST  /api/workspaces/{workspace_pk}/buckets/`
* `GET/POST  /api/workspaces/{workspace_pk}/tasks/` 
* `POST      /api/workspaces/{workspace_pk}/tasks/{id}/complete/`
* `POST      /api/workspaces/{workspace_pk}/tasks/{id}/assign/`

### Visualização de Referência (`tasks/views.py`):
```python
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsWorkspaceMember]

    def get_queryset(self):
        # Tenant Leakage Mitigation (Regra #1)
        workspace_id = self.kwargs.get('workspace_pk')
        return Task.objects.filter(bucket__workspace_id=workspace_id)

    @action(detail=True, methods=['post'])
    def complete(self, request, workspace_pk=None, pk=None):
        task = self.get_object() # Valida 404 e permissions nativamente
        
        # O poder do DRF + Service Layer:
        updated_task = services.complete_task(user=request.user, task_id=task.id)
        
        return Response(TaskSerializer(updated_task).data)

    @action(detail=True, methods=['post'])
    def assign(self, request, workspace_pk=None, pk=None):
        task = self.get_object()
        assignee_id = request.data.get('assignee_id')
        
        try:
            updated_task = services.assign_task(request.user, task, assignee_id)
            return Response(TaskSerializer(updated_task).data)
        except ValidationError as e:
            return Response({"error": str(e)}, status=400)
```

## User Review Required
Revise as regras em `models.py` e a camada de delegação na view. Essa estrutura representa o molde exato do projeto em termos de fronteira. Você está de acordo em avançarmos com esse padrão de *Service Layer + Handlers Explícitos*? Se sim, podemos fechar esse laboratório arquitetural.
