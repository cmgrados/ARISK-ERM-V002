import os
import sys
import django

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'apps'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.liquidity_risk.models import LiqLiabilityDetail
from apps.utilities.models import Socio

from django.db.models import Sum, Count

print("Pasivos by funding_type:")
for row in LiqLiabilityDetail.objects.values('funding_type').annotate(s=Sum('balance')):
    print(row)

print("Pasivos by product:")
for row in LiqLiabilityDetail.objects.values('product').annotate(s=Sum('balance')):
    print(row)

print("Socio count by corte:")
for row in Socio.objects.values('corte').annotate(c=Count('id'), s=Sum('aportes')):
    print(row)
