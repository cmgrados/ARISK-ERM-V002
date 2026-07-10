import json
from django.test import RequestFactory
from django.contrib.auth import get_user_model
from apps.financial_planning.views import api_get_projected_balance_data

User = get_user_model()
user = User.objects.first()
factory = RequestFactory()
request = factory.get('/?scenario=PESSIMISTIC')
request.user = user
res = api_get_projected_balance_data(request, 3)
data = json.loads(res.content)
accounts = [a for a in data['accounts'] if str(a['code']).startswith('14')]
print(json.dumps(accounts, indent=2))
