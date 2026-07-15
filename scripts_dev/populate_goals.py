from apps.goals.models import Factor, Variable

def populate():
    # 1. CRECIMIENTO
    factor_crecimiento, _ = Factor.objects.get_or_create(
        name__icontains='CRECIMIENTO',
        defaults={'name': 'CRECIMIENTO', 'weight': 60}
    )
    
    variables_crecimiento = ['SALDO DE CARTERA', 'SALDO DE DPF', 'SALDO DE APORTES']
    for idx, var_name in enumerate(variables_crecimiento):
        Variable.objects.get_or_create(
            factor=factor_crecimiento,
            name=var_name,
            defaults={'weight': 33.33, 'order': idx}
        )

    # 2. DIVERSIFICACIÓN
    factor_div, _ = Factor.objects.get_or_create(
        name__icontains='DIVERSIFICACIÓN',
        defaults={'name': 'DIVERSIFICACIÓN', 'weight': 10}
    )
    
    variables_div = ['TEM PROMEDIO', 'NÚMERO DE SOCIOS', 'P SALDO DE CRÉDITO']
    for idx, var_name in enumerate(variables_div):
        Variable.objects.get_or_create(
            factor=factor_div,
            name=var_name,
            defaults={'weight': 33.33, 'order': idx}
        )

    # 3. MORA
    factor_mora, _ = Factor.objects.get_or_create(
        name__icontains='MORA',
        defaults={'name': 'MORA', 'weight': 30}
    )
    
    variables_mora = ['MORA>3 DÍAS', 'MORA>30 DÍAS', 'PROVISIONES ESPEC.']
    for idx, var_name in enumerate(variables_mora):
        Variable.objects.get_or_create(
            factor=factor_mora,
            name=var_name,
            defaults={'weight': 33.33, 'order': idx}
        )

    print("Sincronizacion completada exitosamente.")

if __name__ == '__main__':
    populate()
