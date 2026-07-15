from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.auth.models import User
import json
import os, django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.financial_planning.views import assign_institutional_budget_to_plan
from apps.financial_planning.models import FinancialPlan

plan = FinancialPlan.objects.filter(plan_type='INSTITUTIONAL').first()
if not plan:
    print("NO INSTITUTIONAL PLAN FOUND")
else:
    factory = RequestFactory()
    request = factory.post(
        '/api/test', 
        data=json.dumps({'plan_id': plan.id, 'periods': ['2025-01'], 'currency': 'MN'}),
        content_type='application/json'
    )
    user = User.objects.first()
    request.user = user

    try:
        response = assign_institutional_budget_to_plan(request)
        print(response.status_code)
        print(response.content)
        
        plan.refresh_from_db()
        print("BUDGET DATA AFTER:")
        print(bool(plan.budget_data))
    except Exception as e:
        print("ERROR:", e)
