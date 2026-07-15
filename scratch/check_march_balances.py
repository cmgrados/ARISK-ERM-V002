import sys
import os
import django
from decimal import Decimal

# Add the project root to sys.path
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'apps'))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from liquidity_risk.models import LiqSavingsAccount, LiqTermDeposit
from datetime import date

target_date = date(2026, 3, 1) # User mentioned "corte de marzo"
# Usually cut-off is end of month, but let's check both or see what's in DB

periods = LiqSavingsAccount.objects.values_list('period', flat=True).distinct()
print(f"Available periods in Savings: {list(periods)}")

periods_dpf = LiqTermDeposit.objects.values_list('period', flat=True).distinct()
print(f"Available periods in DPF: {list(periods_dpf)}")

# Check March 2026 (assuming last day of month if it's March)
from calendar import monthrange
_, last_day = monthrange(2026, 3)
march_date = date(2026, 3, last_day)

def print_summary(d):
    print(f"\n--- Summary for {d} ---")
    
    savings_mn = LiqSavingsAccount.objects.filter(period=d, currency='MN')
    savings_me = LiqSavingsAccount.objects.filter(period=d, currency='ME')
    
    sum_mn = sum(s.balance for s in savings_mn)
    sum_me = sum(s.balance for s in savings_me)
    
    print(f"Savings MN: {sum_mn:,.2f}")
    print(f"Savings ME: {sum_me:,.2f}")
    print(f"Total Savings: {sum_mn + sum_me:,.2f}")
    
    dpf_mn = LiqTermDeposit.objects.filter(period=d, currency='MN')
    dpf_me = LiqTermDeposit.objects.filter(period=d, currency='ME')
    
    sum_dpf_mn = sum(d.balance for d in dpf_mn)
    sum_dpf_me = sum(d.balance for d in dpf_me)
    
    print(f"DPF MN: {sum_dpf_mn:,.2f}")
    print(f"DPF ME: {sum_dpf_me:,.2f}")
    print(f"Total DPF: {sum_dpf_mn + sum_dpf_me:,.2f}")

for p in sorted(periods_dpf):
    if p.year == 2026 and p.month == 3:
        print_summary(p)

# Also check for specific balance values from the screenshot
# MN: 8,828,902.29
# ME: 684,301.98
print("\nChecking for specific balances in DPF...")
dpf_march = LiqTermDeposit.objects.filter(period=date(2026, 3, 31))
mn_bal = sum(d.balance for d in dpf_march.filter(currency='MN'))
me_bal = sum(d.balance for d in dpf_march.filter(currency='ME'))
print(f"March 31 MN: {mn_bal:,.2f}")
print(f"March 31 ME: {me_bal:,.2f}")
