import os
import sys
import django
from pathlib import Path
import time

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from financial_planning.services.budget_engine import BudgetEngine
from financial_planning.models import PlanFinanciero
from users.models import Organization

org = Organization.objects.first()
plan = PlanFinanciero.objects.filter(organization=org).first()

engine = BudgetEngine(plan, org, None)

start = time.time()
engine._get_historical_er_totals()
print("engine._get_historical_er_totals:", time.time() - start)
