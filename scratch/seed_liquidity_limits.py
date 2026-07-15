import os
import django
import sys

# Add project root to sys.path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from liquidity_risk.models import LiquidityLimit

def seed_limits():
    limits = [
        {
            'indicator_name': 'Índice de Morosidad',
            'limit_type': 'MAX',
            'value': 5.00,
            'description': 'Límite regulatorio para mantener la salud de la cartera.'
        },
        {
            'indicator_name': 'Grado de Liquidez',
            'limit_type': 'MAX',
            'value': 0.95,
            'description': 'Límite prudencial para evitar sobreapalancamiento.'
        },
        {
            'indicator_name': 'Volatilidad de Depósitos',
            'limit_type': 'MAX',
            'value': 10.00,
            'description': 'Alerta temprana ante retiros atípicos.'
        }
    ]
    
    for l in limits:
        LiquidityLimit.objects.get_or_create(
            indicator_name=l['indicator_name'],
            defaults={
                'limit_type': l['limit_type'],
                'value': l['value'],
                'description': l['description']
            }
        )
    print("Límites de liquidez sembrados exitosamente.")

if __name__ == '__main__':
    seed_limits()
