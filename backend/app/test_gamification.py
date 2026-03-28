import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from gamification.models import Profile

User = get_user_model()
c = Client()

response = c.post('/api/token/', {'email': 'admin@test.com', 'password': 'admin123'})
token = response.json()['access']
headers = {'HTTP_AUTHORIZATION': f'Bearer {token}'}

ws_resp = c.get('/api/workspaces/', **headers)
ws_id = ws_resp.json()[0]['id']

task_data = {'title': 'Finish Gamification Phase', 'description': 'Testing XP award'}
task_resp = c.post(f'/api/workspaces/{ws_id}/tasks/', task_data, **headers, content_type='application/json')
task_id = task_resp.json()['id']
print(f"Task created: {task_id}")

user = User.objects.get(email='admin@test.com')
profile_before = Profile.objects.filter(user=user).first()
xp_before = profile_before.total_xp if profile_before else 0
print(f"XP Before complete: {xp_before}")

comp_resp = c.post(f'/api/workspaces/{ws_id}/tasks/{task_id}/complete/', **headers)
print("Complete task API status:", comp_resp.status_code)

profile_after = Profile.objects.get(user=user)
print(f"XP After complete: {profile_after.total_xp}")
print(f"Streak After complete: {profile_after.current_streak}")
