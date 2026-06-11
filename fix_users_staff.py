import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import User

# Update all users to have is_staff=True so they can log in via /admin/login/
updated = User.objects.filter(is_staff=False).update(is_staff=True)
print(f"Updated {updated} users to have is_staff=True.")
