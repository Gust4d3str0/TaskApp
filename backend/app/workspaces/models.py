from django.db import models
from django.conf import settings

class Workspace(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class WorkspaceMembership(models.Model):
    class Role(models.TextChoices):
        OWNER = 'OWNER', 'Owner'
        ADMIN = 'ADMIN', 'Admin'
        MEMBER = 'MEMBER', 'Member'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='memberships')
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='members')
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.MEMBER)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'workspace')

    def __str__(self):
        return f"{self.user} - {self.workspace.name} ({self.role})"
