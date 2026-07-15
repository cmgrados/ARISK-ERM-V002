import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.liquidity_risk.models import LiqLiabilityDetail
from apps.utilities.models import Socio

print("LiqLiabilityDetail Products:")
products = LiqLiabilityDetail.objects.values_list('product', flat=True).distinct()
print(list(products))

print("\nLiqLiabilityDetail Agencies:")
agencies = LiqLiabilityDetail.objects.values_list('agency', flat=True).distinct()
print(list(agencies))

print("\nSocio count:", Socio.objects.count())
if Socio.objects.exists():
    s = Socio.objects.first()
    print("Socio example:", s.aportes, s.oficina, s.corte)
