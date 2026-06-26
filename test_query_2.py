from django.test import RequestFactory
from apps.financial_planning.views import api_trial_balance_data
import json

req = RequestFactory().get('/api/trial_balance_data/?periods=["2025-12"]')
req.user = type('User', (), {'organization': None, 'is_authenticated': True})()
res = api_trial_balance_data(req)
print(json.dumps(json.loads(res.content), indent=2))
