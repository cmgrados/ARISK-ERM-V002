from financial_planning.views import api_get_trend_data
from financial_planning.models import FinancialPlan
from django.test import RequestFactory
from django.contrib.auth import get_user_model

plan = FinancialPlan.objects.first()
if not plan:
    print("No plan found.")
    exit()

factory = RequestFactory()
request = factory.get(f'/financial_planning/api_get_trend_data/{plan.id}/')
request.user = get_user_model().objects.first()

try:
    response = api_get_trend_data(request, plan.id)
    print(f"Status Code: {response.status_code}")
    print(f"Content length: {len(response.content)}")
    if response.status_code != 200:
        import json
        print(json.loads(response.content))
except Exception as e:
    import traceback
    traceback.print_exc()
