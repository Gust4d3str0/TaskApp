from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Task, Bucket, Tag, Subtask
from .serializers import TaskSerializer, BucketSerializer, TagSerializer, SubtaskSerializer
from .permissions import IsWorkspaceMember
from . import services

class BaseWorkspaceViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsWorkspaceMember]

    def get_queryset(self):
        return self.queryset.filter(workspace_id=self.kwargs['workspace_pk'])

    def perform_create(self, serializer):
        serializer.save(workspace_id=self.kwargs['workspace_pk'])

class TagViewSet(BaseWorkspaceViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

class BucketViewSet(BaseWorkspaceViewSet):
    queryset = Bucket.objects.all()
    serializer_class = BucketSerializer

class TaskViewSet(BaseWorkspaceViewSet):
    queryset = Task.objects.prefetch_related('subtasks', 'tags')
    serializer_class = TaskSerializer

    @action(detail=True, methods=['post'])
    def complete(self, request, workspace_pk=None, pk=None):
        task = self.get_object()
        task = services.complete_task(task, request.user)
        serializer = self.get_serializer(task)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def assign(self, request, workspace_pk=None, pk=None):
        task = self.get_object()
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({"error": "user_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        try:
            target_user = User.objects.get(pk=user_id)
            task = services.assign_task_to_member(task, target_user)
            serializer = self.get_serializer(task)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({"error": "User does not exist."}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class SubtaskViewSet(viewsets.ModelViewSet):
    queryset = Subtask.objects.all()
    serializer_class = SubtaskSerializer
    permission_classes = [IsAuthenticated, IsWorkspaceMember]

    def get_queryset(self):
        return Subtask.objects.filter(task_id=self.kwargs['task_pk'], task__workspace_id=self.kwargs['workspace_pk'])

    def perform_create(self, serializer):
        from rest_framework.generics import get_object_or_404
        task = get_object_or_404(Task, pk=self.kwargs['task_pk'], workspace_id=self.kwargs['workspace_pk'])
        serializer.save(task=task)
