import os
import sys
import django
from pathlib import Path
import time

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from users.models import User, Organization
from financial_planning.models import PlanFinanciero

org = Organization.objects.first()
user = User.objects.filter(organization=org).first()
plan = PlanFinanciero.objects.filter(organization=org).first()

c = Client()
c.force_login(user)

try:
    start = time.time()
    response = c.get(f'/planificacion-financiera/plan/{plan.id}/api/api_get_budget_data/?scenario=BASE')
    end = time.time()
    print("STATUS:", response.status_code)
    print("TIME:", end - start)
except Exception as e:
    import traceback
    traceback.print_exc()
