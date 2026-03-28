# Checklist de Execução: Backend TaskApp MVP
Este checklist dita a cadência de construção do backend (Django + DRF) priorizando a dependência estrutural dos domínios, isolando o Workspace (como Muro de Contenção) primeiro.

## Fase 1: Fundação & Identidade (Setup Core)
A base para qualquer regra existir.
- [ ] Navegar para `backend/app/` e checar `settings.py`.
- [ ] Configurar PostgreSQL (`DATABASES`).
- [ ] Criar/configurar app `users`.
- [ ] Substituir o modelo padrão por um Custom User Model (`AUTH_USER_MODEL = 'users.User'`) focado em login por e-mail.
- [ ] Configurar DRF e instalar/configurar Autenticação JWT (`djangorestframework-simplejwt`).
- [ ] **Checagem de Qualidade:** Conseguir disparar `python manage.py makemigrations` e `migrate` originais; criar um superuser e bater no Token Endpoint.

## Fase 2: O Muro de Contenção (App Workspaces)
Tranca o isolamento antes de nascerem as tarefas.
- [ ] Criar app `workspaces`.
- [ ] Modelar `Workspace` (nome, timestamps).
- [ ] Modelar `WorkspaceMembership` (FK User, FK Workspace, choices de Role: Owner/Admin/Member).
- [ ] Desenvolver `workspaces/services.py` contendo a transação explícita de `create_workspace` (atribuindo *Owner*).
- [ ] Criar DRF Serializers & ViewSets p/ listar/criar Workspaces restritos ao User logado.

## Fase 3: Domínio Central de Produtividade (App Tasks)
As entidades agora nascem blindadas.
- [ ] Criar app `tasks`.
- [ ] Modelar estritamente com amarras lógicas: `Tag`, `Bucket`, `Task`, `Subtask`. NENHUMA dependência reversa de Gamificação!
- [ ] Criar a blindagem principal do projeto em `tasks/permissions.py`: Classe `IsWorkspaceMember`.
- [ ] Configurar URLs utilizando Nested Routers (pacote `drf-nested-routers`) com rotas do tipo `/api/workspaces/{id}/tasks/`.
- [ ] Criar Serializers (`tasks/serializers.py`) 100% livres de *Fat Logic*.

## Fase 4: A Mágica do Isolamento (Service Layer de Tasks)
- [ ] Desenvolver `tasks/services.py` definindo explicitamente `complete_task()`.
- [ ] Desenvolver serviço para validade "Assignee Boundary" (`assign_task_to_member`).
- [ ] Criar Action Decorators no ViewSet (DRF) que absorvem requisições limpas e delegam para o Service (Ex: `POST /{id}/complete/`).

## Fase 5: Domínio de Engajamento (App Gamification)
Listener agnóstico (User-centric) sem conhecimento prévio do Workspace.
- [ ] Criar app `gamification`.
- [ ] Modelar a entidade `Profile` contendo o O2O para User, `total_xp`, `current_streak`.
- [ ] Escrever o handler transacional puro `gamification/handlers.py` -> `award_task_completion(user)`.
- [ ] Plugar o *handler* de gamificação **explicitamente** na chamada de serviço do final da fase 4.
- [ ] **Checagem de Qualidade:** O ato de concluir task adiciona XP instantaneamente com 1 query otimizada.

## Fase 6: Sistema Cego de Foco (App Focus)
Registro efêmero do que aconteceu nos clientes (frontend/mobile).
- [ ] Criar app `focus`.
- [ ] Modelar `FocusSession` com timestamps enriquecidos, sources e relação nula com Tasks e Workspace.
- [ ] Expor o endpoint DRF `POST /api/focus/sessions/` para clientes enviarem "Sessões salvas".
- [ ] Aplicar no serviço de Foco a mesma estrutura de *handler* explícito da Gamificação.
