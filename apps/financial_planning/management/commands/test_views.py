from django.core.management.base import BaseCommand
from django.test import RequestFactory
from financial_planning.views import api_get_projected_balance_data
from financial_planning.models import PlanFinanciero
from django.contrib.auth import get_user_model
import json

class Command(BaseCommand):
    def handle(self, *args, **options):
        User = get_user_model()
        plan = PlanFinanciero.objects.get(id=3)
        user = User.objects.first()
        factory = RequestFactory()
        request = factory.get(f'/plan/{plan.id}/api/api_get_projected_balance_data/?scenario=OPTIMISTIC')
        request.user = user

        response = api_get_projected_balance_data(request, plan.id)
        data = json.loads(response.content)
        total = 0
        for a in data['accounts']:
            if a['code'].startswith('21'):
                print(f"{a['code']}: base={a['base']}, m1={a['m1_12'][0]}")
