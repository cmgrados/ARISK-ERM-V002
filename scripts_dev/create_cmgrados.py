import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
try:
    user = User.objects.get(username='cmgrados')
    user.set_password('123456')
    user.is_staff = True
    user.is_superuser = True
    user.save()
    print("User updated: cmgrados / 123456")
except User.DoesNotExist:
    User.objects.create_superuser('cmgrados', 'cmgrados@example.com', '123456')
    print("User created: cmgrados / 123456")
