from rest_framework import serializers
from .models import Tag, Bucket, Task, Subtask

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'workspace', 'name', 'color']
        read_only_fields = ['id', 'workspace']

class BucketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bucket
        fields = ['id', 'workspace', 'name', 'order']
        read_only_fields = ['id', 'workspace']

class SubtaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subtask
        fields = ['id', 'task', 'title', 'is_completed', 'created_at']
        read_only_fields = ['id', 'task', 'created_at']

class TaskSerializer(serializers.ModelSerializer):
    subtasks = SubtaskSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'workspace', 'bucket', 'assignee', 'tags',
            'title', 'description', 'status', 'due_date',
            'created_at', 'updated_at', 'completed_at',
            'subtasks'
        ]
        read_only_fields = ['id', 'workspace', 'created_at', 'updated_at', 'completed_at']
