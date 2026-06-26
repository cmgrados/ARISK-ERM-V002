import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.financial_planning.models import PeriodoFinanciero, BalanceDetalle
print('Periodos:', list(PeriodoFinanciero.objects.values('id', 'anio', 'mes', 'estado')))
print('Balances:', BalanceDetalle.objects.count())
