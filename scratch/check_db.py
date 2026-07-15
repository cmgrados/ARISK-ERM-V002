import os
import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from liquidity_risk.models import LiqBalanceDetail
from django.db.models.functions import Length

print("Frecuencia de longitudes de código contable:")

all_codes = list(LiqBalanceDetail.objects.values_list('account_code', flat=True).distinct())
len_counts = {}
for code in all_codes:
    l = len(code.strip())
    len_counts[l] = len_counts.get(l, 0) + 1

for l in sorted(len_counts.keys()):
    print(f"Longitud {l} dígitos: {len_counts[l]} cuentas únicas")

print("\nEjemplos de cuentas con 10 o más dígitos:")
long_codes = [c for c in all_codes if len(c.strip()) >= 10][:10]
for c in long_codes:
    acc = LiqBalanceDetail.objects.filter(account_code=c).first()
    print(f"{c}: {acc.account_name}")
