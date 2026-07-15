import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.op_risk.models import OperationalCapitalCalculation

data = [
    {'year': 2026, 'y1': 15000000.00, 'y2': 14500000.00, 'y3': 13800000.00, 'alfa': 0.15},
    {'year': 2025, 'y1': 14500000.00, 'y2': 13800000.00, 'y3': 12500000.00, 'alfa': 0.15},
    {'year': 2024, 'y1': 13800000.00, 'y2': 12500000.00, 'y3': 11000000.00, 'alfa': 0.15},
    {'year': 2023, 'y1': 12500000.00, 'y2': 11000000.00, 'y3': 10500000.00, 'alfa': 0.15},
    {'year': 2022, 'y1': 11000000.00, 'y2': 10500000.00, 'y3': 9500000.00, 'alfa': 0.15},
]

OperationalCapitalCalculation.objects.all().delete()

for item in data:
    calc = OperationalCapitalCalculation(
        year=item['year'],
        gross_income_y1=item['y1'],
        gross_income_y2=item['y2'],
        gross_income_y3=item['y3'],
        alfa_factor=item['alfa']
    )
    calc.save()
    print(f"Created capital calculation for year {item['year']} with calculated capital: {calc.calculated_capital}")

print("Capital calculations loaded successfully.")
