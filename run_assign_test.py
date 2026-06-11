import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from apps.financial_planning.views import assign_institutional_budget_to_plan
from apps.financial_planning.models import FinancialPlan

plan = FinancialPlan.objects.filter(plan_type='INSTITUTIONAL').first()
if plan:
    factory = RequestFactory()
    request = factory.post('/api/test', data=json.dumps({
        'plan_id': plan.id,
        'periods': ['2025-01'],
        'currency': 'MN'
    }), content_type='application/json')
    request.user = User.objects.first()
    
    resp = assign_institutional_budget_to_plan(request)
    print("STATUS CODE:", resp.status_code)
    print("RESPONSE:", resp.content.decode('utf-8'))
    
    plan.refresh_from_db()
    if plan.budget_data:
        print("KEYS:", plan.budget_data.keys())
        print("PERIODS:", plan.budget_data['selected_periods'])
    else:
        print("BUDGET DATA IS EMPTY")
