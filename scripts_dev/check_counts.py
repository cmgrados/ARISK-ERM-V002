import os
import django
import sys

# Add project root to sys.path
sys.path.append('c:/Users/VICTUS/Desktop/A.RISK ERM')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from liquidity_risk.models import LiqSavingsAccount, LiqTermDeposit
from django.db.models import Count

print("--- SAVINGS ACCOUNTS ---")
savings = LiqSavingsAccount.objects.values('period').annotate(count=Count('id')).order_by('period')
for s in savings:
    print(f"Period: {s['period']}, Count: {s['count']}")

print("\n--- TERM DEPOSITS ---")
dpf = LiqTermDeposit.objects.values('period').annotate(count=Count('id')).order_by('period')
for d in dpf:
    print(f"Period: {d['period']}, Count: {d['count']}")
