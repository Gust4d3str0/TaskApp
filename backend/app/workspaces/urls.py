from django.urls import path, include
from rest_framework_nested import routers
from .views import WorkspaceViewSet
from tasks.views import TaskViewSet, BucketViewSet, TagViewSet, SubtaskViewSet

router = routers.DefaultRouter()
router.register(r'', WorkspaceViewSet, basename='workspace')

workspaces_router = routers.NestedDefaultRouter(router, r'', lookup='workspace')
workspaces_router.register(r'tasks', TaskViewSet, basename='workspace-tasks')
workspaces_router.register(r'buckets', BucketViewSet, basename='workspace-buckets')
workspaces_router.register(r'tags', TagViewSet, basename='workspace-tags')

tasks_router = routers.NestedDefaultRouter(workspaces_router, r'tasks', lookup='task')
tasks_router.register(r'subtasks', SubtaskViewSet, basename='task-subtasks')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(workspaces_router.urls)),
    path('', include(tasks_router.urls)),
]
