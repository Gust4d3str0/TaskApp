import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from django.test import Client

c = Client()
response = c.post('/api/token/', {'email': 'admin@test.com', 'password': 'admin123'})
print("STATUS_CODE:", response.status_code)
if response.status_code == 200:
    print("SUCCESS")
else:
    print(response.content[:500])
