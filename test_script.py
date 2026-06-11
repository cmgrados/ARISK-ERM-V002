import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.financial_planning.models import FinancialPlan
plan = FinancialPlan.objects.filter(plan_type='INSTITUTIONAL').first()
data = plan.budget_data
assumptions = data.get('account_assumptions', {})
print('ASSUMPTIONS KEYS:', len(assumptions))
