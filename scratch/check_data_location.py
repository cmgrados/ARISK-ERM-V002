import sys
import os
import django

sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'apps'))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from liquidity_risk.models import LiqTermDeposit, LiqSavingsAccount

print(f"Savings count: {LiqSavingsAccount.objects.count()}")
print(f"DPF count: {LiqTermDeposit.objects.count()}")

savings_in_dpf = LiqTermDeposit.objects.filter(product__icontains="AHORRO")
print(f"Savings found in DPF table: {savings_in_dpf.count()}")

if savings_in_dpf.exists():
    print("Example products in DPF that look like savings:")
    for p in savings_in_dpf.values('product').distinct()[:10]:
        print(f"- {p['product']}")
