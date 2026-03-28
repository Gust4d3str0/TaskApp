from rest_framework import serializers
from .models import Workspace, WorkspaceMembership

class WorkspaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workspace
        fields = ['id', 'name', 'created_at']
        read_only_fields = ['id', 'created_at']

class WorkspaceMembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkspaceMembership
        fields = ['id', 'user', 'workspace', 'role', 'joined_at']
        read_only_fields = ['id', 'joined_at']
