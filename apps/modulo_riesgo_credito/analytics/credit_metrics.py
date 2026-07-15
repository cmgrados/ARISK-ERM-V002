from decimal import Decimal

def calculate_ead(balance, pending_interests, ccf=Decimal('1.0')):
    """
    EAD (Exposure at Default). 
    Fórmula estándar: EAD = Balance + Intereses + (Línea no usada * Credit Conversion Factor)
    Para créditos a plazo fijo, CCF suele ser 1.0 y la línea no usada es 0.
    """
    return balance + pending_interests

def calculate_lgd(guarantee_value, ead, recovery_rate=Decimal('0.0')):
    """
    LGD (Loss Given Default). Porcentaje de pérdida si ocurre default.
    Si hay garantías prendarias/hipotecarias, reducen el LGD.
    Si recovery_rate > 0 (porcentaje de recupero histórico), disminuye el LGD.
    Retorna un valor entre 0 y 1.
    """
    if ead <= 0:
        return Decimal('0.0')
        
    net_exposure = ead - guarantee_value
    if net_exposure <= 0:
        return Decimal('0.0') # 100% garantizado
        
    base_lgd = net_exposure / ead
    final_lgd = base_lgd * (Decimal('1.0') - recovery_rate)
    
    # Floor en 0, Cap en 1
    return max(Decimal('0.0'), min(Decimal('1.0'), final_lgd))

def get_base_pd(sbs_classification, days_past_due):
    """
    Probabilidad de Default (PD) a 12 meses.
    En una implementación más avanzada, esto viene de un modelo de Regresión Logística.
    Por ahora, se usa una tabla paramétrica basada en los días de mora y la calificación.
    """
    if days_past_due == 0:
        return Decimal('0.02') # 2% de PD para Normales puros
    elif sbs_classification == 'Normal':
        return Decimal('0.05')
    elif sbs_classification == 'CPP':
        return Decimal('0.15')
    elif sbs_classification == 'Deficiente':
        return Decimal('0.40')
    elif sbs_classification == 'Dudoso':
        return Decimal('0.75')
    else:
        return Decimal('1.00') # Pérdida ya está en default

def calculate_expected_loss(pd, lgd, ead):
    """
    Pérdida Esperada (Expected Loss = PD * LGD * EAD)
    """
    return pd * lgd * ead
