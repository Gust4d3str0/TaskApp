from rest_framework import permissions
from workspaces.models import WorkspaceMembership

class IsWorkspaceMember(permissions.BasePermission):
    """
    Custom permission to only allow members of a workspace to access its objects.
    Assumes the view receives `workspace_pk` in kwargs, or the object has a `workspace` attribute.
    """

    def has_permission(self, request, view):
        workspace_id = view.kwargs.get('workspace_pk')
        if not workspace_id:
            return True
        
        return WorkspaceMembership.objects.filter(
            user=request.user,
            workspace_id=workspace_id
        ).exists()

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'workspace'):
            return WorkspaceMembership.objects.filter(
                user=request.user,
                workspace=obj.workspace
            ).exists()
        return False
