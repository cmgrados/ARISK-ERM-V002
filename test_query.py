import os
import django
import json
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.test import Client
from users.models import User
import urllib.parse

c = Client()
u = User.objects.first()
c.force_login(u)
periods = urllib.parse.quote('["2023-12","2024-12","2025-01"]')
res = c.get('/planificacion-financiera/api/api_trial_balance_data/?periods=' + periods)
print(res.status_code)
print(json.dumps(res.json(), indent=2))
