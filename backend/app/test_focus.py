import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from gamification.models import Profile
import django.utils.timezone as tz

User = get_user_model()
c = Client()
response = c.post('/api/token/', {'email': 'admin@test.com', 'password': 'admin123'})
token = response.json()['access']
headers = {'HTTP_AUTHORIZATION': f'Bearer {token}'}

user = User.objects.get(email='admin@test.com')
xp_before = Profile.objects.get(user=user).total_xp

now = tz.now()
start = now - tz.timedelta(minutes=25)
end = now
duration = 25 * 60

focus_data = {
    'start_time': start.isoformat(),
    'end_time': end.isoformat(),
    'duration_seconds': duration,
    'source': 'WEB'
}

focus_resp = c.post('/api/focus/sessions/', focus_data, **headers, content_type='application/json')
print("Focus API Status:", focus_resp.status_code)

xp_after = Profile.objects.get(user=user).total_xp
print(f"XP Before: {xp_before} | XP After: {xp_after} | Gained: {xp_after - xp_before}")
