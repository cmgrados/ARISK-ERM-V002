import os
import django
import json

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.http import HttpRequest
from django.contrib.auth.models import User
from apps.financial_planning.views import assign_institutional_budget_to_plan
from apps.financial_planning.models import FinancialPlan

plan = FinancialPlan.objects.get(id=8)
user = User.objects.first()

request = HttpRequest()
request.method = 'POST'
request.user = user
# The payload is json
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

response = assign_institutional_budget_to_plan(request)
print("Response Status Code:", response.status_code)
print("Response Content:", response.content.decode('utf-8'))
