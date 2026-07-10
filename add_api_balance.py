import os

with open('apps/financial_planning/views.py', 'r', encoding='utf8') as f:
    views_content = f.read()

view_code = """
@login_required
@require_GET
def api_get_projected_balance_data(request, plan_id):
    from django.http import JsonResponse
    from django.shortcuts import get_object_or_404
    from .models import PlanFinanciero, SimulacionEscenario, ProyeccionMensual, BudgetVersion, BudgetLine, BudgetLineDetail
    from liquidity_risk.models import LiqBalanceDetail
    
    organization = request.user.organization
    if not organization:
        from users.models import Organization
        organization = Organization.objects.first()
        
    plan = get_object_or_404(PlanFinanciero, id=plan_id, organization=organization)
    scenario = request.GET.get('scenario', 'BASE')

    # 1. Historical Balance (Dec of Base Year)
    selected_periods = plan.historical_data.get('selected_periods', []) if plan.historical_data else []
    years = sorted({p.split('-')[0] for p in selected_periods}, reverse=True)
    base_year = int(years[0]) if years else (plan.anio_base - 1)

    dec_qs = LiqBalanceDetail.objects.filter(
        period__year=base_year,
        period__month=12,
        upload__status='SUCCESS',
    ).values('account_code', 'balance')

    hist_bals = {}
    for row in dec_qs:
        code = str(row['account_code'])
        bal = abs(float(row['balance']))
        hist_bals[code] = bal

    def get_sum(prefix, exclude_prefix=None):
        return sum(v for k, v in hist_bals.items() if k.startswith(prefix) and (not exclude_prefix or not k.startswith(exclude_prefix)))

    base_cartera = get_sum('14', exclude_prefix='149')
    base_prov = get_sum('149')
    base_cxc = get_sum('16')
    base_af = get_sum('18')
    base_otros_act = get_sum('1') - (base_cartera + base_prov + base_cxc + base_af)

    base_ahorros = get_sum('211')
    base_dpf = get_sum('212')
    base_adeudos = get_sum('24')
    base_otros_pas = get_sum('2') - (base_ahorros + base_dpf + base_adeudos)

    base_cap_social = get_sum('31')
    base_reservas = get_sum('32')
    base_res_acum = get_sum('33')
    base_otros_pat = get_sum('3') - (base_cap_social + base_reservas + base_res_acum)

    # 2. Get Projections
    sims = SimulacionEscenario.objects.filter(plan=plan, organization=organization)
    
    def get_proj_vals(variable_id):
        sim = sims.filter(variable_id=variable_id).first()
        if not sim:
            return None
        projs = list(ProyeccionMensual.objects.filter(escenario=sim).order_by('mes_proyeccion'))
        field = 'valor_base'
        if scenario == 'OPTIMISTIC': field = 'valor_optimista'
        elif scenario == 'PESSIMISTIC': field = 'valor_pesimista'
        return [float(getattr(p, field, 0) or 0) for p in projs]
        
    proj_cartera = get_proj_vals('cartera')
    proj_ahorros = get_proj_vals('ahorros')
    proj_dpf = get_proj_vals('dpf')
    
    # 3. Get Budget Net Income (Resultado del Ejercicio)
    version = BudgetVersion.objects.filter(plan_financiero=plan, organization=organization, scenario=scenario, status='DRAFT').first()
    net_incomes = [0.0] * 36
    if version:
        lines = BudgetLine.objects.filter(version=version).select_related('item')
        for line in lines:
            details = list(BudgetLineDetail.objects.filter(budget_line=line).order_by('period_index'))
            cat = line.item.category
            sign = 1 if cat in ['ING_FIN', 'ING_SERV', 'OTROS_ING'] else -1
            for i, d in enumerate(details[:12]):
                if i < 12:
                    net_incomes[i] += float(d.amount) * sign
            
            y2 = float(line.total_amount_y2 or 0) * sign
            y3 = float(line.total_amount_y3 or 0) * sign
            for i in range(12, 24): net_incomes[i] += y2 / 12
            for i in range(24, 36): net_incomes[i] += y3 / 12
            
    def build_row(name, base_val, proj_array, is_negative=False):
        row_vals = []
        for i in range(36):
            val = proj_array[i] if proj_array and i < len(proj_array) else base_val
            row_vals.append(val)
            
        m1_12 = row_vals[:12]
        y1_total = row_vals[11]
        y2_total = row_vals[23]
        y3_total = row_vals[35]
        return {
            'name': name,
            'base': -base_val if is_negative else base_val,
            'm1_12': [-v if is_negative else v for v in m1_12],
            'y1': -y1_total if is_negative else y1_total,
            'y2': -y2_total if is_negative else y2_total,
            'y3': -y3_total if is_negative else y3_total
        }
        
    cartera_row = build_row('Cartera de Créditos (Bruta)', base_cartera, proj_cartera)
    prov_row = build_row('(-) Provisiones para Créditos', base_prov, None, is_negative=True)
    cxc_row = build_row('Cuentas por Cobrar', base_cxc, None)
    af_row = build_row('Activo Fijo (Neto)', base_af, None)
    otros_act_row = build_row('Otros Activos', base_otros_act, None)
    
    ahorros_row = build_row('Obligaciones con el Público (Ahorros)', base_ahorros, proj_ahorros)
    dpf_row = build_row('Obligaciones con el Público (Plazo Fijo)', base_dpf, proj_dpf)
    adeudos_row = build_row('Adeudos y Oblig. Financieras', base_adeudos, None)
    otros_pas_row = build_row('Otros Pasivos', base_otros_pas, None)
    
    cap_social_row = build_row('Capital Social', base_cap_social, None)
    reservas_row = build_row('Reservas', base_reservas, None)
    res_acum_row = build_row('Resultados Acumulados', base_res_acum, None)
    otros_pat_row = build_row('Otros Patrimonio', base_otros_pat, None)
    
    res_ej_base = 0.0
    res_ej_m1_12 = []
    cum = 0
    for i in range(12):
        cum += net_incomes[i]
        res_ej_m1_12.append(cum)
    
    y1_ej = sum(net_incomes[:12])
    y2_ej = sum(net_incomes[12:24])
    y3_ej = sum(net_incomes[24:36])
    
    res_acum_row['y1'] = base_res_acum
    res_acum_row['y2'] = base_res_acum + y1_ej
    res_acum_row['y3'] = base_res_acum + y1_ej + y2_ej
    
    res_ej_row = {
        'name': 'Resultado del Ejercicio',
        'base': res_ej_base,
        'm1_12': res_ej_m1_12,
        'y1': y1_ej,
        'y2': y2_ej,
        'y3': y3_ej
    }
    
    def sum_rows(rows, attr):
        return sum(r[attr] for r in rows)
        
    def sum_rows_array(rows, attr):
        return [sum(r[attr][i] for r in rows) for i in range(12)]
        
    pasivo_rows = [ahorros_row, dpf_row, adeudos_row, otros_pas_row]
    patrimonio_rows = [cap_social_row, reservas_row, res_acum_row, otros_pat_row, res_ej_row]
    
    total_pasivo = {
        'base': sum_rows(pasivo_rows, 'base'),
        'm1_12': sum_rows_array(pasivo_rows, 'm1_12'),
        'y1': sum_rows(pasivo_rows, 'y1'),
        'y2': sum_rows(pasivo_rows, 'y2'),
        'y3': sum_rows(pasivo_rows, 'y3'),
    }
    
    total_patrimonio = {
        'base': sum_rows(patrimonio_rows, 'base'),
        'm1_12': sum_rows_array(patrimonio_rows, 'm1_12'),
        'y1': sum_rows(patrimonio_rows, 'y1'),
        'y2': sum_rows(patrimonio_rows, 'y2'),
        'y3': sum_rows(patrimonio_rows, 'y3'),
    }
    
    total_pas_pat = {
        'base': total_pasivo['base'] + total_patrimonio['base'],
        'm1_12': [total_pasivo['m1_12'][i] + total_patrimonio['m1_12'][i] for i in range(12)],
        'y1': total_pasivo['y1'] + total_patrimonio['y1'],
        'y2': total_pasivo['y2'] + total_patrimonio['y2'],
        'y3': total_pasivo['y3'] + total_patrimonio['y3'],
    }
    
    activo_no_fd_rows = [cartera_row, prov_row, cxc_row, af_row, otros_act_row]
    
    sub_activo = {
        'base': sum_rows(activo_no_fd_rows, 'base'),
        'm1_12': sum_rows_array(activo_no_fd_rows, 'm1_12'),
        'y1': sum_rows(activo_no_fd_rows, 'y1'),
        'y2': sum_rows(activo_no_fd_rows, 'y2'),
        'y3': sum_rows(activo_no_fd_rows, 'y3'),
    }
    
    fondos_row = {
        'name': 'Fondos Disponibles',
        'base': total_pas_pat['base'] - sub_activo['base'],
        'm1_12': [total_pas_pat['m1_12'][i] - sub_activo['m1_12'][i] for i in range(12)],
        'y1': total_pas_pat['y1'] - sub_activo['y1'],
        'y2': total_pas_pat['y2'] - sub_activo['y2'],
        'y3': total_pas_pat['y3'] - sub_activo['y3'],
    }
    
    activo_rows = [fondos_row, cartera_row, prov_row, cxc_row, af_row, otros_act_row]
    total_activo = {
        'base': sum_rows(activo_rows, 'base'),
        'm1_12': sum_rows_array(activo_rows, 'm1_12'),
        'y1': sum_rows(activo_rows, 'y1'),
        'y2': sum_rows(activo_rows, 'y2'),
        'y3': sum_rows(activo_rows, 'y3'),
    }
    
    data = {
        'status': 'success',
        'groups': [
            {
                'name': 'ACTIVO',
                'accounts': activo_rows,
                'total': total_activo
            },
            {
                'name': 'PASIVO',
                'accounts': pasivo_rows,
                'total': total_pasivo
            },
            {
                'name': 'PATRIMONIO',
                'accounts': patrimonio_rows,
                'total': total_patrimonio
            }
        ],
        'total_pasivo_patrimonio': total_pas_pat
    }
    
    return JsonResponse(data)

"""

if 'def api_get_projected_balance_data' not in views_content:
    with open('apps/financial_planning/views.py', 'a', encoding='utf8') as f:
        f.write('\n\n' + view_code)
    print('Added to views.py')

with open('apps/financial_planning/urls.py', 'r', encoding='utf8') as f:
    urls_content = f.read()

if 'api_get_projected_balance_data' not in urls_content:
    urls_content = urls_content.replace(']', "    path('plan/<int:plan_id>/api/api_get_projected_balance_data/', views.api_get_projected_balance_data, name='api_get_projected_balance_data'),\n]")
    with open('apps/financial_planning/urls.py', 'w', encoding='utf8') as f:
        f.write(urls_content)
    print('Added to urls.py')
