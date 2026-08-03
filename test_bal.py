import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.test import RequestFactory
from django.contrib.auth import get_user_model
from financial_planning.views import api_get_projected_balance_data
import json
user = get_user_model().objects.get(username='cmgrados')
req = RequestFactory().get('/?scenario=BASE')
req.user = user
res = api_get_projected_balance_data(req, 3)
data = json.loads(res.content)
for acc in data['accounts']:
  if acc['code'] in ['1', '14']:
    print(acc['code'], acc['is_locked'], acc['base'], acc['m1_12'][:2])
