from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Workspace
from .serializers import WorkspaceSerializer
from . import services

class WorkspaceViewSet(viewsets.ModelViewSet):
    serializer_class = WorkspaceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Users can only see workspaces they are members of
        return Workspace.objects.filter(members__user=self.request.user)

    def perform_create(self, serializer):
        name = serializer.validated_data.get('name')
        workspace = services.create_workspace(user=self.request.user, name=name)
        serializer.instance = workspace
