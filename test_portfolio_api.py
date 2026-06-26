import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arisk_project.settings')
django.setup()
from django.test import RequestFactory
from apps.financial_planning.views import api_historical_portfolio_data
import json

req = RequestFactory().get('/api_historical_portfolio_data/?dates=2025-01,2025-02')
req.user = type('User', (), {'is_authenticated': True, 'tenant_id': 1})()
res = api_historical_portfolio_data(req)
print(json.dumps(json.loads(res.content), indent=2))
