# Checklist de Execução: Backend TaskApp MVP
Este checklist dita a cadência de construção do backend (Django + DRF) priorizando a dependência estrutural dos domínios, isolando o Workspace (como Muro de Contenção) primeiro.

## Fase 1: Fundação & Identidade (Setup Core)
A base para qualquer regra existir.
- [x] Navegar para `backend/app/` e checar `settings.py`.
- [x] Configurar PostgreSQL (`DATABASES`).
- [x] Criar/configurar app `users`.
- [x] Substituir o modelo padrão por um Custom User Model (`AUTH_USER_MODEL = 'users.User'`) focado em login por e-mail.
- [x] Configurar DRF e instalar/configurar Autenticação JWT (`djangorestframework-simplejwt`).
- [x] **Checagem de Qualidade:** Conseguir disparar `python manage.py makemigrations` e `migrate` originais; criar um superuser e bater no Token Endpoint.

## Fase 2: O Muro de Contenção (App Workspaces)
Tranca o isolamento antes de nascerem as tarefas.
- [x] Criar app `workspaces`.
- [x] Modelar `Workspace` (nome, timestamps).
- [x] Modelar `WorkspaceMembership` (FK User, FK Workspace, choices de Role: Owner/Admin/Member).
- [x] Desenvolver `workspaces/services.py` contendo a transação explícita de `create_workspace` (atribuindo *Owner*).
- [x] Criar DRF Serializers & ViewSets p/ listar/criar Workspaces restritos ao User logado.

## Fase 3: Domínio Central de Produtividade (App Tasks)
As entidades agora nascem blindadas.
- [x] Criar app `tasks`.
- [x] Modelar estritamente com amarras lógicas: `Tag`, `Bucket`, `Task`, `Subtask`. NENHUMA dependência reversa de Gamificação!
- [x] Criar a blindagem principal do projeto em `tasks/permissions.py`: Classe `IsWorkspaceMember`.
- [x] Configurar URLs utilizando Nested Routers (pacote `drf-nested-routers`) com rotas do tipo `/api/workspaces/{id}/tasks/`.
- [x] Criar Serializers (`tasks/serializers.py`) 100% livres de *Fat Logic*.

## Fase 4: A Mágica do Isolamento (Service Layer de Tasks)
- [x] Desenvolver `tasks/services.py` definindo explicitamente `complete_task()`.
- [x] Desenvolver serviço para validade "Assignee Boundary" (`assign_task_to_member`).
- [x] Criar Action Decorators no ViewSet (DRF) que absorvem requisições limpas e delegam para o Service (Ex: `POST /{id}/complete/`).

## Fase 5: Domínio de Engajamento (App Gamification)
Listener agnóstico (User-centric) sem conhecimento prévio do Workspace.
- [x] Criar app `gamification`.
- [x] Modelar a entidade `Profile` contendo o O2O para User, `total_xp`, `current_streak`.
- [x] Escrever o handler transacional puro `gamification/handlers.py` -> `award_task_completion(user)`.
- [x] Plugar o *handler* de gamificação **explicitamente** na chamada de serviço do final da fase 4.
- [x] **Checagem de Qualidade:** O ato de concluir task adiciona XP instantaneamente com 1 query otimizada.

## Fase 6: Sistema Cego de Foco (App Focus)
Registro efêmero do que aconteceu nos clientes (frontend/mobile).
- [x] Criar app `focus`.
- [x] Modelar `FocusSession` com timestamps enriquecidos, sources e relação nula com Tasks e Workspace.
- [x] Expor o endpoint DRF `POST /api/focus/sessions/` para clientes enviarem "Sessões salvas".
- [x] Aplicar no serviço de Foco a mesma estrutura de *handler* explícito da Gamificação.
