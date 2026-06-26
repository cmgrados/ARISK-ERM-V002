import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "arisk_erm.settings")
django.setup()

from liquidity_risk.models import LiqBalanceDetail

# Let's see what periods are available
periods = LiqBalanceDetail.objects.values_list('period', flat=True).distinct()
print("Available periods:", list(periods))

# Let's check an income statement account (e.g., 5 or 4) for one of the periods
details = LiqBalanceDetail.objects.filter(account_code__startswith='5')[:5]
for d in details:
    print(d.period, d.account_code, d.account_name, d.balance)

details4 = LiqBalanceDetail.objects.filter(account_code__startswith='4')[:5]
for d in details4:
    print(d.period, d.account_code, d.account_name, d.balance)
