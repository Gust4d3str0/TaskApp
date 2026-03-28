from django.utils import timezone
from .models import Profile

def award_task_completion(user):
    """
    Awards XP and updates the user's streak for completing a task.
    """
    profile, _ = Profile.objects.get_or_create(user=user)
    
    today = timezone.now().date()
    
    if profile.last_activity_date == today:
        profile.total_xp += 10
    else:
        # Check streak
        if profile.last_activity_date == today - timezone.timedelta(days=1):
            profile.current_streak += 1
        else:
            profile.current_streak = 1
        
        profile.last_activity_date = today
        profile.total_xp += 10

    profile.save(update_fields=['total_xp', 'current_streak', 'last_activity_date'])
    return profile

def award_focus_session(user, duration_seconds: int):
    """
    Awards XP for a focus session (e.g. 1 XP per minute) and updates streak.
    """
    profile, _ = Profile.objects.get_or_create(user=user)
    
    today = timezone.now().date()
    xp_gained = duration_seconds // 60
    
    if profile.last_activity_date == today:
        profile.total_xp += xp_gained
    else:
        if profile.last_activity_date == today - timezone.timedelta(days=1):
            profile.current_streak += 1
        else:
            profile.current_streak = 1
            
        profile.last_activity_date = today
        profile.total_xp += xp_gained

    profile.save(update_fields=['total_xp', 'current_streak', 'last_activity_date'])
    return profile
