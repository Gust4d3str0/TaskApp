from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import FocusSession
from .serializers import FocusSessionSerializer
from . import services

class FocusSessionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = FocusSessionSerializer

    def get_queryset(self):
        return FocusSession.objects.filter(user=self.request.user).order_by('-created_at')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        start_time = serializer.validated_data.get('start_time')
        end_time = serializer.validated_data.get('end_time')
        duration_seconds = serializer.validated_data.get('duration_seconds')
        source = serializer.validated_data.get('source', 'WEB')
        task = serializer.validated_data.get('task')

        session = services.save_focus_session(
            user=request.user,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration_seconds,
            source=source,
            task=task
        )
        
        return Response(self.get_serializer(session).data, status=status.HTTP_201_CREATED)

