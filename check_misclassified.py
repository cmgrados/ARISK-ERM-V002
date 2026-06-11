import os
import django
import sys

# Add project root to sys.path
sys.path.append('c:/Users/VICTUS/Desktop/A.RISK ERM')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from liquidity_risk.models import LiqTermDeposit

products = LiqTermDeposit.objects.values_list('product', flat=True).distinct()
savings_prods = [p for p in products if 'AHORRO' in p.upper()]
print(f"Total distinct products in DPF table: {len(products)}")
print(f"Total 'AHORRO' products in DPF table: {len(savings_prods)}")
if savings_prods:
    print("Example savings products found in DPF table:")
    for p in savings_prods[:10]:
        print(f" - '{p}'")
else:
    print("No products with 'AHORRO' found in DPF table.")
