from django.test import RequestFactory
from financial_planning.views import api_get_budget_data
from users.models import User
import json

request = RequestFactory().get('/api_get_budget_data?scenario=BASE')
request.user = User.objects.first()

response = api_get_budget_data(request, 2)
data = json.loads(response.content)
for item in data.get('data', []):
    if item['historical_total'] > 0 or item['y1_total'] > 0:
        print(f"{item['name']} | calc: {item['calc_type']} | hist: {item['historical_total']} | Y1: {item['y1_total']}")
