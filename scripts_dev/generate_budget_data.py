import json
from django.apps import apps
from django.http import HttpRequest

FinancialPlan = apps.get_model('financial_planning', 'FinancialPlan')
User = apps.get_model('users', 'User')

plan = FinancialPlan.objects.get(id=8)
user = User.objects.first()

request = HttpRequest()
request.method = 'POST'
request.user = user
payload = {
    "plan_id": 8,
    "periods": [
        "2023-12", "2024-12", "2025-01", "2025-02", "2025-03", "2025-04", 
        "2025-05", "2025-06", "2025-07", "2025-08", "2025-09", "2025-10", 
        "2025-11", "2025-12"
    ],
    "currency": "MN"
}
request._body = json.dumps(payload).encode('utf-8')

# Call the view directly by importing from the app module?
# Wait, let me import the view directly but I must not re-import models!
import sys
from financial_planning.views import assign_institutional_budget_to_plan

response = assign_institutional_budget_to_plan(request)
print("Response Status Code:", response.status_code)
