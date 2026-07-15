import os
import django
import sys
from decimal import Decimal

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from credit_risk.models import CreditOperation, CreditRiskMetrics

def init_metrics():
    print("Limpiando métricas previas...")
    CreditRiskMetrics.objects.all().delete()
    
    latest_date = CreditOperation.objects.order_by('-load_date').values_list('load_date', flat=True).first()
    if not latest_date:
        print("No hay operaciones en la base de datos.")
        return
        
    ops = CreditOperation.objects.filter(load_date=latest_date)
    metrics_list = []
    
    # Mapping SBS Classifications to standard PD
    pd_map = {
        'Normal': Decimal('1.00'),
        'CPP': Decimal('5.00'),
        'Deficiente': Decimal('25.00'),
        'Dudoso': Decimal('60.00'),
        'Pérdida': Decimal('100.00')
    }
    lgd_standard = Decimal('45.00') # 45% standard LGD
    
    print(f"Generando métricas EL para el corte {latest_date} ({ops.count()} registros)...")
    for op in ops:
        pd_val = pd_map.get(op.sbs_classification, Decimal('1.00'))
        ead_val = op.balance
        
        # EL = PD * EAD * LGD (PD y LGD están en base porcentual, así que dividimos entre 100)
        el_val = (pd_val / Decimal('100')) * ead_val * (lgd_standard / Decimal('100'))
        
        metrics_list.append(
            CreditRiskMetrics(
                operation=op,
                pd=pd_val,
                ead=ead_val,
                lgd=lgd_standard,
                expected_loss=el_val
            )
        )
        
    CreditRiskMetrics.objects.bulk_create(metrics_list)
    print("¡Finalizado! Las metodologías EL han sido generadas y ya figuran en la lista.")

if __name__ == "__main__":
    init_metrics()
