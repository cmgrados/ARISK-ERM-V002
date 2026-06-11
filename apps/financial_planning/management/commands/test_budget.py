from django.core.management.base import BaseCommand
from apps.financial_planning.models import FinancialPlan
from apps.financial_planning.views import assign_institutional_budget_to_plan
from django.test import RequestFactory
import json

class Command(BaseCommand):
    def handle(self, *args, **options):
        plans = FinancialPlan.objects.filter(plan_type='INSTITUTIONAL')
        print(f"Found {plans.count()} institutional plans")
        for p in plans:
            print(f"Plan ID {p.id} Name {p.name} HasBudget: {bool(p.budget_data)}")
            
        plan = plans.first()
        if plan:
            print(f"Testing assignment to {plan.id}...")
            factory = RequestFactory()
            request = factory.post('/api/test', data=json.dumps({'plan_id': plan.id, 'periods': ['2025-01'], 'currency': 'MN'}), content_type='application/json')
            from django.contrib.auth.models import User
            request.user = User.objects.first()
            resp = assign_institutional_budget_to_plan(request)
            print("Response:", resp.content)
            
            plan.refresh_from_db()
            print("Has budget data after assignment:", bool(plan.budget_data))
            if plan.budget_data:
                print("Budget Data Keys:", plan.budget_data.keys())
