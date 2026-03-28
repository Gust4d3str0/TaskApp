from .models import FocusSession
from gamification.handlers import award_focus_session

def save_focus_session(user, start_time, end_time, duration_seconds, source='WEB', task=None) -> FocusSession:
    """
    Saves a focus session submitted by the client and triggers gamification.
    """
    session = FocusSession.objects.create(
        user=user,
        task=task,
        start_time=start_time,
        end_time=end_time,
        duration_seconds=duration_seconds,
        source=source
    )
    
    award_focus_session(user, duration_seconds)
    
    return session
