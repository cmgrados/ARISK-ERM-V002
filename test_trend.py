import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import RequestFactory
from funcs import api_generate_cf_trend
from users.models import User

user = User.objects.first()
factory = RequestFactory()
request = factory.post('/api/', data='{"scenario": "BASE"}', content_type='application/json')
request.user = user

response = api_generate_cf_trend(request, 3)
print(response.content)
