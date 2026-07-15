from decimal import Decimal

def determine_sbs_classification(days_past_due, is_refinanced=False, active_alerts=0):
    """
    Reglas SBS simplificadas para clasificar deudores según mora.
    (Normal, CPP, Deficiente, Dudoso, Pérdida)
    Si es refinanciado, estadísticamente suele degradarse la calificación.
    Si tiene alertas activas, se aplica una regla de arrastre a peor categoría.
    """
    if days_past_due <= 8:
        base_class = 'Normal'
    elif days_past_due <= 30:
        base_class = 'CPP'
    elif days_past_due <= 60:
        base_class = 'Deficiente'
    elif days_past_due <= 120:
        base_class = 'Dudoso'
    else:
        base_class = 'Pérdida'
        
    # Regla de Arrastre (Deterioro Subjetivo)
    hierarchy = ['Normal', 'CPP', 'Deficiente', 'Dudoso', 'Pérdida']
    idx = hierarchy.index(base_class)
    
    if is_refinanced and idx < len(hierarchy) - 1:
        idx += 1 # Empeora un nivel
        
    if active_alerts > 0 and idx < len(hierarchy) - 1:
        idx += 1 # Empeora otro nivel por alertas
        
    return hierarchy[min(idx, len(hierarchy) - 1)]

def calculate_provision_rate(classification, credit_type='Consumo'):
    """
    Tasas regulatorias estándar de provisiones basadas en la clasificación SBS
    y el tipo de crédito.
    """
    rates = {
        'Normal': Decimal('0.01'),       # 1%
        'CPP': Decimal('0.05'),          # 5%
        'Deficiente': Decimal('0.25'),   # 25%
        'Dudoso': Decimal('0.60'),       # 60%
        'Pérdida': Decimal('1.00')       # 100%
    }
    return rates.get(classification, Decimal('0.01'))

def calculate_required_provision(ead, classification, credit_type='Consumo'):
    """
    Calcula la provisión monetaria en base a la Exposición al Default (EAD).
    """
    rate = calculate_provision_rate(classification, credit_type)
    return ead * rate
