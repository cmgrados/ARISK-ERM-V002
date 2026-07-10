import time
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from financial_planning.models import PlanFinanciero

User = get_user_model()
user = User.objects.first()
c = Client()
c.force_login(user)
plan = PlanFinanciero.objects.get(id=3)

import cProfile
cProfile.run(f'c.get("/planificacion-financiera/plan/{plan.id}/api/api_get_projected_balance_data/")', sort='tottime')
