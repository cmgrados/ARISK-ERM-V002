import os
import django
import sys

# Add project root to sys.path
sys.path.append(r'c:\Users\VICTUS\Desktop\A.RISK ERM')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from credit_risk.models import CreditOperation
from liquidity_risk.views import get_latest_period

period = get_latest_period()
print(f"Checking data for period: {period}")

ops = CreditOperation.objects.filter(load_date=period)
print(f"Total ops: {ops.count()}")

for op in ops[:10]:
    print(f"Op: {op.operation_code}, Bal: {op.balance}, Disb: {op.disbursement_date}, Term: {op.term}, Mat: {op.maturity_date}, Type: {op.credit_type}")
