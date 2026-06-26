import os
import sys
import django
from django.conf import settings

# Setup Django environment
sys.path.append(os.path.abspath('c:/Users/VICTUS/Desktop/A.RISK ERM - V2'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arisk_project.settings')
django.setup()

from apps.financial_planning.models import PlanFinanciero
from apps.financial_planning.views import api_get_trend_data
from django.http import HttpRequest

plan = PlanFinanciero.objects.first()
if not plan:
    print("No plan found.")
    sys.exit(0)

request = HttpRequest()
response = api_get_trend_data(request, plan_id=plan.id)

print(response.content.decode('utf-8')[:500])
