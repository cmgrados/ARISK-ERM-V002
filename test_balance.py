import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'risksystem.settings')
django.setup()
from django.test import Client
from django.contrib.auth import get_user_model
from apps.financial_planning.models import PlanFinanciero
user = get_user_model().objects.get(username='cmgrados')
plan = PlanFinanciero.objects.last()
c = Client()
c.force_login(user)
r = c.get(f'/planificacion-financiera/plan/{plan.id}/api/api_get_projected_balance_data/?scenario=BASE')
print('Status:', r.status_code)
if r.status_code == 500:
    print(r.content.decode('utf-8'))
