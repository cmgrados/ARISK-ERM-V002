import sys
import os
import django
from decimal import Decimal

sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'apps'))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from liquidity_risk.models import LiqTermDeposit
from datetime import date

dpf_march = LiqTermDeposit.objects.filter(period=date(2026, 3, 31))

# Group by product name and sum balance
products = {}
for d in dpf_march:
    key = (d.product, d.currency)
    products[key] = products.get(key, Decimal('0')) + d.balance

print("Products in DPF for March 31, 2026:")
for (name, curr), bal in sorted(products.items()):
    print(f"{curr} - {name}: {bal:,.2f}")
