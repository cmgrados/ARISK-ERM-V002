import os
import django
import sys
from datetime import date

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from liquidity_risk.engine import process_monthly_liquidity
from liquidity_risk.models import LiquidityMetric

def recalculate_all():
    dates = LiquidityMetric.objects.values_list('load_date', flat=True).distinct()
    for d in dates:
        print(f"Procesando {d}...")
        process_monthly_liquidity(d)
    print("Recálculo completo.")

if __name__ == '__main__':
    recalculate_all()
