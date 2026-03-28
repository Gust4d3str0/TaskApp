import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from django.test import Client

c = Client()
# First login
response = c.post('/api/token/', {'email': 'admin@test.com', 'password': 'admin123'})
token = response.json()['access']

# Create a workspace
response2 = c.post('/api/workspaces/', {'name': 'Workspace Pessoal'}, HTTP_AUTHORIZATION=f'Bearer {token}')
print("Create:", response2.status_code, response2.json())

# List workspaces
response3 = c.get('/api/workspaces/', HTTP_AUTHORIZATION=f'Bearer {token}')
print("List:", response3.status_code, response3.json())
