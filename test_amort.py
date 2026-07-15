import os
import django
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from credit_risk.models import CarteraCreditoCarga
from liquidity_risk.engine.cashflow import get_cashflow_projections

cutoff_date = date(2024, 12, 31)

creditos = CarteraCreditoCarga.objects.filter(fecha_corte=cutoff_date, skcr__gt=0).exclude(ncpr__isnull=True)[:5]
for credito in creditos:
    print(f"Credito id={credito.id}, saldo={credito.skcr}, ncpr={credito.ncpr}, ncpa={credito.ncpa}, fvga={credito.fvga}")
    
report = get_cashflow_projections(cutoff_date)
print("\nBandas amortización:")
for k, v in report['flujo_de_ingresos']['Amortizacion de creditos programadas'].items():
    if v > 0:
        print(f"{k}: {v}")
print("\nBandas interes:")
for k, v in report['flujo_de_ingresos']['Ingresos financieros programadas'].items():
    if v > 0:
        print(f"{k}: {v}")
