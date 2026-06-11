import os
import django
import sys

# Add project root to sys.path
sys.path.append('c:/Users/VICTUS/Desktop/A.RISK ERM')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from liquidity_risk.models import LiqTermDeposit

products = LiqTermDeposit.objects.values_list('product', flat=True).distinct()
for p in list(products)[:20]:
    print(f"Product: '{p}'")
