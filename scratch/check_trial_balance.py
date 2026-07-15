import sys
import os
import django
from decimal import Decimal

sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'apps'))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from liquidity_risk.models import LiqBalanceDetail, LiqBalanceUpload
from datetime import date

# Find March 2026 upload
uploads = LiqBalanceUpload.objects.filter(period__year=2026, period__month=3)
print(f"Found {uploads.count()} balance uploads for March 2026")

for u in uploads:
    print(f"\nUpload for period {u.period} (Currency: {u.currency})")
    details = LiqBalanceDetail.objects.filter(upload=u)
    
    # Check for accounts that might be savings
    # In trial balances, these are usually 2101... or similar
    for d in details:
        if "AHORRO" in d.account_name.upper():
            print(f"{d.account_code} - {d.account_name}: {d.balance:,.2f}")

# Check totals for specific values
# MN: 8,828,902.29
# ME: 684,301.98
print("\nChecking for specific total balances in Trial Balance...")
total_mn = sum(d.balance for d in LiqBalanceDetail.objects.filter(upload__period=date(2026, 3, 31), upload__currency='MN'))
total_me = sum(d.balance for d in LiqBalanceDetail.objects.filter(upload__period=date(2026, 3, 31), upload__currency='ME'))
print(f"Total MN Balance (all accounts): {total_mn:,.2f}")
print(f"Total ME Balance (all accounts): {total_me:,.2f}")
