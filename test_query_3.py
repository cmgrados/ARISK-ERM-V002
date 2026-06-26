import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arisk_erm.settings')
django.setup()

from apps.financial_planning.views import api_available_historical_dates
from django.test import RequestFactory
import json

req = RequestFactory().get('/api/available_historical_dates/')
req.user = type('User', (), {'organization': None, 'is_authenticated': True})()
res = api_available_historical_dates(req)
print(json.dumps(json.loads(res.content), indent=2))
