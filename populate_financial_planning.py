import os
import django
from datetime import date
import random


from django.db import transaction
from django.apps import apps

@transaction.atomic
def populate():
    BalanceDetalle = apps.get_model('financial_planning', 'BalanceDetalle')
    CuentaContable = apps.get_model('financial_planning', 'CuentaContable')
    PeriodoFinanciero = apps.get_model('financial_planning', 'PeriodoFinanciero')
    Organization = apps.get_model('users', 'Organization')

    org = Organization.objects.first()
    if not org:
        org = Organization.objects.create(name='Organización Default')

    print("Limpiando datos anteriores...")
    BalanceDetalle.objects.all().delete()
    CuentaContable.objects.all().delete()
    PeriodoFinanciero.objects.all().delete()

    print("Creando periodos...")
    periods_data = [
        (2023, 12), (2024, 12),
        (2025, 1), (2025, 2), (2025, 3), (2025, 4), (2025, 5), (2025, 6),
        (2025, 7), (2025, 8), (2025, 9), (2025, 10), (2025, 11), (2025, 12),
    ]
    periods = {}
    for y, m in periods_data:
        p = PeriodoFinanciero.objects.create(anio=y, mes=m, estado='CERRADO', organization=org)
        periods[f"{y}-{m:02d}"] = p

    print("Creando cuentas...")
    accounts_data = [
        # Activo
        {'code': '1', 'name': 'ACTIVO', 'type': 'ACTIVO', 'level': 1, 'parent': None},
        {'code': '11', 'name': 'FONDOS DISPONIBLES', 'type': 'ACTIVO', 'level': 2, 'parent': '1'},
        {'code': '13', 'name': 'INVERSIONES NEGOCIABLES Y A VENCIMIENTO', 'type': 'ACTIVO', 'level': 2, 'parent': '1'},
        {'code': '14', 'name': 'CRÉDITOS', 'type': 'ACTIVO', 'level': 2, 'parent': '1'},
        {'code': '15', 'name': 'CUENTAS POR COBRAR', 'type': 'ACTIVO', 'level': 2, 'parent': '1'},
        {'code': '17', 'name': 'INVERSIONES EN SUBSIDIARIAS Y ASOCIADAS', 'type': 'ACTIVO', 'level': 2, 'parent': '1'},
        {'code': '18', 'name': 'INMUEBLES, MOBILIARIO Y EQUIPO', 'type': 'ACTIVO', 'level': 2, 'parent': '1'},
        {'code': '19', 'name': 'OTROS ACTIVOS', 'type': 'ACTIVO', 'level': 2, 'parent': '1'},
        # Pasivo
        {'code': '2', 'name': 'PASIVO', 'type': 'PASIVO', 'level': 1, 'parent': None},
        {'code': '21', 'name': 'OBLIGACIONES CON LOS SOCIOS', 'type': 'PASIVO', 'level': 2, 'parent': '2'},
        {'code': '25', 'name': 'CUENTAS POR PAGAR', 'type': 'PASIVO', 'level': 2, 'parent': '2'},
        {'code': '27', 'name': 'PROVISIONES', 'type': 'PASIVO', 'level': 2, 'parent': '2'},
        {'code': '29', 'name': 'OTROS PASIVOS', 'type': 'PASIVO', 'level': 2, 'parent': '2'},
        # Patrimonio
        {'code': '3', 'name': 'PATRIMONIO', 'type': 'PATRIMONIO', 'level': 1, 'parent': None},
        {'code': '31', 'name': 'CAPITAL SOCIAL', 'type': 'PATRIMONIO', 'level': 2, 'parent': '3'},
        {'code': '33', 'name': 'RESERVAS', 'type': 'PATRIMONIO', 'level': 2, 'parent': '3'},
        {'code': '38', 'name': 'RESULTADOS ACUMULADOS', 'type': 'PATRIMONIO', 'level': 2, 'parent': '3'},
        {'code': '39', 'name': 'RESULTADO NETO DEL EJERCICIO', 'type': 'PATRIMONIO', 'level': 2, 'parent': '3'},
        # We also need Level 3 and 4 to simulate deep nodes (e.g. 1101, 1103 as shown in screenshot)
        {'code': '1101', 'name': 'CAJA', 'type': 'ACTIVO', 'level': 3, 'parent': '11'},
        {'code': '1103', 'name': 'BANCOS Y OTRAS INSTITUCIONES FINANCIERAS', 'type': 'ACTIVO', 'level': 3, 'parent': '11'},
        {'code': '110305', 'name': 'BANCOS Y OTRAS INSTITUCIONES FINANCIERAS DEL PAIS', 'type': 'ACTIVO', 'level': 4, 'parent': '1103'},
        {'code': '11030501', 'name': 'BANCOS Y OTRAS INSTITUCIONES FINANCIERAS DEL PAIS', 'type': 'ACTIVO', 'level': 5, 'parent': '110305'},
        
        # We also create a dummy income statement (codes 4, 5) even though the viewer uses 1, 2, 3
        # just so the database has realistic full data.
        {'code': '4', 'name': 'GASTOS', 'type': 'GASTO', 'level': 1, 'parent': None},
        {'code': '41', 'name': 'GASTOS FINANCIEROS', 'type': 'GASTO', 'level': 2, 'parent': '4'},
        {'code': '5', 'name': 'INGRESOS', 'type': 'INGRESO', 'level': 1, 'parent': None},
        {'code': '51', 'name': 'INGRESOS FINANCIEROS', 'type': 'INGRESO', 'level': 2, 'parent': '5'},
    ]

    accounts = {}
    # Create them in order of level
    for a in sorted(accounts_data, key=lambda x: x['level']):
        parent = accounts.get(a['parent']) if a['parent'] else None
        acc = CuentaContable.objects.create(
            codigo=a['code'],
            nombre=a['name'],
            tipo=a['type'],
            nivel=a['level'],
            parent=parent,
            organization=org
        )
        accounts[a['code']] = acc

    print("Generando montos de balances (sólo para cuentas hoja para simular rollup)...")
    leaf_accounts = {
        '1101': 500000, '11030501': 2125549, # Sums to 2,625,549
        '13': 132360,
        '14': 64954059,
        '15': 939747,
        '17': 4418916,
        '18': 38345275,
        '19': 1161434,
        
        '21': 52885374,
        '25': 1215498,
        '27': 12114369,
        '29': 2539355,
        
        '31': 48490721,
        '33': 2976580,
        '38': -4763483,
        '39': -2881075,
        
        '41': 1500000,
        '51': 3000000
    }

    balances_to_create = []
    
    # We will generate base values for Dic-2023 and add some simple random drift for other periods
    for code, base_amt in leaf_accounts.items():
        acc = accounts[code]
        for p_key, p_obj in periods.items():
            # calculate some drift relative to the month. 
            # In Screenshot 2 they grow. Let's make it grow 1% per month.
            year, month = int(p_key.split('-')[0]), int(p_key.split('-')[1])
            months_diff = (year - 2023) * 12 + (month - 12)
            if months_diff < 0: months_diff = 0
            
            amt = base_amt * (1 + (0.01 * months_diff))
            
            balances_to_create.append(BalanceDetalle(
                periodo=p_obj,
                cuenta=acc,
                monto=round(amt, 2),
                organization=org
            ))

    BalanceDetalle.objects.bulk_create(balances_to_create)
    print("¡Datos financieros poblados exitosamente!")

if __name__ == '__main__':
    populate()
