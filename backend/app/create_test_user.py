import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
if not User.objects.filter(email='admin@test.com').exists():
    User.objects.create_superuser('username_here', 'admin@test.com', 'admin123')
    print("Superuser created")
else:
    print("Superuser already exists")
