from django.db import models
from django.conf import settings
from workspaces.models import Workspace

class Tag(models.Model):
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='tags')
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=7, default="#808080")

    class Meta:
        unique_together = ('workspace', 'name')

    def __str__(self):
        return f"{self.name} ({self.workspace.name})"

class Bucket(models.Model):
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='buckets')
    name = models.CharField(max_length=255)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.name} ({self.workspace.name})"

class Task(models.Model):
    class Status(models.TextChoices):
        TODO = 'TODO', 'To Do'
        DOING = 'DOING', 'Doing'
        DONE = 'DONE', 'Done'

    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='tasks')
    bucket = models.ForeignKey(Bucket, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    assignee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    tags = models.ManyToManyField(Tag, blank=True, related_name='tasks')
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.TODO)
    
    due_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

class Subtask(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='subtasks')
    title = models.CharField(max_length=255)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
