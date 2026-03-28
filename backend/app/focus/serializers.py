from rest_framework import serializers
from .models import FocusSession

class FocusSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FocusSession
        fields = ['id', 'user', 'task', 'start_time', 'end_time', 'duration_seconds', 'source', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
