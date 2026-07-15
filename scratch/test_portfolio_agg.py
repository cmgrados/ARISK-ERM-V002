import os
import django
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncMonth

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from credit_risk.models import CreditOperation
from liquidity_risk.models import LiqBalanceDetail

# Get available load dates from CreditOperation
periods = CreditOperation.objects.values_list('load_date', flat=True).distinct().order_by('load_date')
print("Periods:", periods)

# We want to aggregate by Agency -> Month
# Metrics:
# 1. Nro Analistas = Count(distinct advisor)
# 2. Desembolsos (disbursement_date in the same month as load_date) - Count and Sum by type
# 3. Cartera (total operations in the load_date) - Count and Sum by type
# 4. Cartera Vencida (past_due_portfolio) - Sum
