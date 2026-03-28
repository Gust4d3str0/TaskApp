from django.db import transaction
from django.contrib.auth import get_user_model
from .models import Workspace, WorkspaceMembership

User = get_user_model()

@transaction.atomic
def create_workspace(user: User, name: str) -> Workspace:
    """
    Creates a new Workspace and assigns the creating user as its OWNER.
    """
    workspace = Workspace.objects.create(name=name)
    WorkspaceMembership.objects.create(
        user=user,
        workspace=workspace,
        role=WorkspaceMembership.Role.OWNER
    )
    return workspace
