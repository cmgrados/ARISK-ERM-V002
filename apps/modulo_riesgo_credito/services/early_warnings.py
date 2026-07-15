from django.utils import timezone
from credit_risk.models import CreditOperation
from modulo_riesgo_credito.models import AlertaActiva

def run_early_warning_scans():
    """
    Ejecuta reglas heurísticas para detectar señales tempranas de riesgo.
    Esto debería ejecutarse en un cron job diario (tasks.py / celery).
    """
    today = timezone.now().date()
    # 1. Alerta: Cliente entra a Mora (1 día) por primera vez
    # Simulamos una condición: days_past_due == 1
    new_delinquencies = CreditOperation.objects.filter(
        days_past_due=1
    )
    for op in new_delinquencies:
        AlertaActiva.objects.get_or_create(
            operation=op,
            alert_type='Primera Mora',
            defaults={
                'description': f'El crédito {op.operation_code} ha caído en mora (1 día) por primera vez.',
                'severity': 'MEDIA'
            }
        )

    # 2. Alerta: Refinanciados que caen de nuevo en mora (Segunda Caída)
    # Refinanciados con mora > 0
    second_fall = CreditOperation.objects.filter(
        is_refinanced=True,
        days_past_due__gt=0
    )
    for op in second_fall:
        AlertaActiva.objects.get_or_create(
            operation=op,
            alert_type='Segunda Caída',
            defaults={
                'description': f'Crédito REFINANCIADO {op.operation_code} volvió a caer en mora.',
                'severity': 'ALTA'
            }
        )
        
    return True
