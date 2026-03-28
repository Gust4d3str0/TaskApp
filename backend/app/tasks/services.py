from django.utils import timezone
from .models import Task
from workspaces.models import WorkspaceMembership

def complete_task(task: Task, user):
    """
    Marks a task as completed and triggers any necessary downstream logic (e.g., Gamification).
    """
    if task.status != Task.Status.DONE:
        task.status = Task.Status.DONE
        task.completed_at = timezone.now()
        task.save(update_fields=['status', 'completed_at'])
        
        # TODO: Hook for Gamification
    
    return task

def assign_task_to_member(task: Task, user):
    """
    Assigns a task to a user, ensuring the user is a member of the task's workspace.
    """
    if not WorkspaceMembership.objects.filter(workspace=task.workspace, user=user).exists():
        raise ValueError("User must be a member of the workspace to be assigned to this task.")
    
    task.assignee = user
    task.save(update_fields=['assignee'])
    return task
