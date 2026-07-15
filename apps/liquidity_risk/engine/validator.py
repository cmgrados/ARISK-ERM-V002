import logging
from decimal import Decimal
from django.db.models import Sum
from liquidity_risk.models import LiqBalanceDetail, CarteraPasivoCarga
from credit_risk.models import CarteraCreditoCarga

logger = logging.getLogger(__name__)

def validar_cruce_maestro(fecha_corte, tolerancia_porcentaje=0.005):
    """
    Realiza el cruce entre las fuentes operativas (Anexo 6 y Depósitos) 
    y el Balance de Comprobación para una fecha de corte determinada.
    """
    resultado = {
        'status': 'OK',
        'detalles': [],
        'fecha': fecha_corte
    }
    
    # 1. Extraer Saldo Contable de Cartera (Cuenta 14)
    balance_cartera = LiqBalanceDetail.objects.filter(
        period=fecha_corte, 
        account_code__startswith='14'
    ).aggregate(total=Sum('balance'))['total'] or Decimal('0.00')

    # 2. Extraer Saldo Operativo de Cartera (Anexo 6)
    anexo6_cartera = CarteraCreditoCarga.objects.filter(
        fecha_corte=fecha_corte
    ).aggregate(total=Sum('scc'))['total'] or Decimal('0.00')

    # Validación Cartera
    dif_cartera = abs(balance_cartera - anexo6_cartera)
    max_tol_cartera = balance_cartera * Decimal(str(tolerancia_porcentaje))
    
    status_cartera = 'OK'
    if balance_cartera == 0 and anexo6_cartera == 0:
        status_cartera = 'SIN_DATOS'
    elif dif_cartera > max_tol_cartera:
        status_cartera = 'DESCUADRE'
        resultado['status'] = 'WARNING'

    resultado['detalles'].append({
        'modulo': 'Cartera de Créditos (Cta 14)',
        'saldo_contable': float(balance_cartera),
        'saldo_operativo': float(anexo6_cartera),
        'diferencia': float(dif_cartera),
        'estado': status_cartera
    })

    # 3. Extraer Saldo Contable de Obligaciones (Cuenta 21)
    balance_pasivos = LiqBalanceDetail.objects.filter(
        period=fecha_corte, 
        account_code__startswith='21'
    ).aggregate(total=Sum('balance'))['total'] or Decimal('0.00')

    # 4. Extraer Saldo Operativo de Depósitos
    depositos_pasivos = CarteraPasivoCarga.objects.filter(
        fecha_corte=fecha_corte
    ).aggregate(total=Sum('saldo'))['total'] or Decimal('0.00')

    # Validación Pasivos
    dif_pasivos = abs(balance_pasivos - depositos_pasivos)
    max_tol_pasivos = balance_pasivos * Decimal(str(tolerancia_porcentaje))
    
    status_pasivos = 'OK'
    if balance_pasivos == 0 and depositos_pasivos == 0:
        status_pasivos = 'SIN_DATOS'
    elif dif_pasivos > max_tol_pasivos:
        status_pasivos = 'DESCUADRE'
        resultado['status'] = 'WARNING'

    resultado['detalles'].append({
        'modulo': 'Obligaciones con el Público (Cta 21)',
        'saldo_contable': float(balance_pasivos),
        'saldo_operativo': float(depositos_pasivos),
        'diferencia': float(dif_pasivos),
        'estado': status_pasivos
    })

    return resultado
