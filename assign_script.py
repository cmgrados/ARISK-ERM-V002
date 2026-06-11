import os
import django
import json
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.financial_planning.models import FinancialPlan
from apps.financial_planning.views import assign_institutional_budget_to_plan
from django.test import RequestFactory
from django.contrib.auth.models import User

# Check if there is an institutional budget
plan = FinancialPlan.objects.filter(plan_type='INSTITUTIONAL').first()
if not plan:
    print('No institutional plan found.')
else:
    print('Plan found:', plan.id, plan.name)
    print('Initial budget_data:', bool(plan.budget_data))
    
    # Let's perform the assignment programmatically
    # Simulating what happens in institutional_budget_viewer
    factory = RequestFactory()
    request = factory.post('/api/test', data=json.dumps({
        'plan_id': plan.id,
        'periods': ['2025-01'],
        'currency': 'MN'
    }), content_type='application/json')
    request.user = User.objects.first()
    
    response = assign_institutional_budget_to_plan(request)
    print('Response status code:', response.status_code)
    print('Response content:', response.content.decode('utf-8'))
    
    plan.refresh_from_db()
    print('budget_data after assignment:', bool(plan.budget_data))
    if plan.budget_data:
        print('budget_data periods:', plan.budget_data.get('selected_periods'))
