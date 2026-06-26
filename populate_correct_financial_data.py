from django.apps import apps
import random

def run():
    PeriodoFinanciero = apps.get_model('financial_planning', 'PeriodoFinanciero')
    CuentaContable = apps.get_model('financial_planning', 'CuentaContable')
    BalanceDetalle = apps.get_model('financial_planning', 'BalanceDetalle')
    Organization = apps.get_model('users', 'Organization')
    
    org = Organization.objects.first()
    if not org:
        print("No organization found.")
        return

    # Delete existing data for a clean slate
    BalanceDetalle.objects.filter(organization=org).delete()
    CuentaContable.objects.filter(organization=org).delete()
    PeriodoFinanciero.objects.filter(organization=org).delete()
    
    # Create periods for 2024, 2025, 2026
    periods = []
    for y in [2024, 2025, 2026]:
        for m in range(1, 13):
            p = PeriodoFinanciero.objects.create(
                organization=org,
                anio=y,
                mes=m,
                estado='FINAL'
            )
            periods.append(p)
    print(f"Created {len(periods)} periods.")

    # Base values for Ene-2025
    base_values = {
        '1101': 565000,
        '11030501': 2401870,
        '13': 149567,
        '14': 73398087,
        '15': 1061914,
        '17': 4993375,
        '18': 43330161,
        '19': 1312420,
        '21': 59760473,
        '25': 1373513,
        '27': 13689237,
        '29': 2869471,
        '31': 54794515,
        '33': 3363535,
        '38': -5382736,
        '39': -3255615
    }

    # Define account hierarchy
    accounts_info = [
        ('1', None, 'ACTIVO', 'ACTIVO'),
        ('11', '1', 'FONDOS DISPONIBLES', 'ACTIVO'),
        ('1101', '11', 'CAJA', 'ACTIVO'),
        ('1103', '11', 'BANCOS Y OTRAS INSTITUCIONES FINANCIERAS', 'ACTIVO'),
        ('110305', '1103', 'BANCOS Y OTRAS INSTITUCIONES FINANCIERAS DEL PAIS', 'ACTIVO'),
        ('11030501', '110305', 'BANCOS Y OTRAS INSTITUCIONES FINANCIERAS DEL PAIS', 'ACTIVO'),
        ('13', '1', 'INVERSIONES NEGOCIABLES Y A VENCIMIENTO', 'ACTIVO'),
        ('14', '1', 'CRÉDITOS', 'ACTIVO'),
        ('15', '1', 'CUENTAS POR COBRAR', 'ACTIVO'),
        ('17', '1', 'INVERSIONES EN SUBSIDIARIAS Y ASOCIADAS', 'ACTIVO'),
        ('18', '1', 'INMUEBLES, MOBILIARIO Y EQUIPO', 'ACTIVO'),
        ('19', '1', 'OTROS ACTIVOS', 'ACTIVO'),
        ('2', None, 'PASIVO', 'PASIVO'),
        ('21', '2', 'OBLIGACIONES CON LOS SOCIOS', 'PASIVO'),
        ('25', '2', 'CUENTAS POR PAGAR', 'PASIVO'),
        ('27', '2', 'PROVISIONES', 'PASIVO'),
        ('29', '2', 'OTROS PASIVOS', 'PASIVO'),
        ('3', None, 'PATRIMONIO', 'PATRIMONIO'),
        ('31', '3', 'CAPITAL SOCIAL', 'PATRIMONIO'),
        ('33', '3', 'RESERVAS', 'PATRIMONIO'),
        ('38', '3', 'RESULTADOS ACUMULADOS', 'PATRIMONIO'),
        ('39', '3', 'RESULTADO NETO DEL EJERCICIO', 'PATRIMONIO'),
    ]

    account_objs = {}
    for code, parent_code, name, tipo in accounts_info:
        parent_obj = account_objs.get(parent_code) if parent_code else None
        
        # Calculate level based on length of code or parent level
        if parent_obj:
            level = parent_obj.nivel + 1
        else:
            level = 1

        c = CuentaContable.objects.create(
            organization=org,
            codigo=code,
            nombre=name,
            tipo=tipo,
            nivel=level,
            parent=parent_obj
        )
        account_objs[code] = c

    # Create balances for the leaf accounts
    for p in periods:
        # Determine a multiplier based on time diff from Jan 2025
        # Jan 2025 is (2025 * 12 + 1)
        months_from_jan_2025 = (p.anio * 12 + p.mes) - (2025 * 12 + 1)
        
        # Add 0.5% growth per month to make numbers look slightly different but close
        multiplier = 1.0 + (0.005 * months_from_jan_2025)

        for leaf_code, base_val in base_values.items():
            val = base_val * multiplier
            
            BalanceDetalle.objects.create(
                organization=org,
                periodo=p,
                cuenta=account_objs[leaf_code],
                monto=val
            )
            
    print("Populated accurate trial balance with 2024, 2025 and 2026 periods!")
