from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

@login_required
@require_http_methods(["POST"])
def api_save_bg_snapshot(request, plan_id):
    import json
    from django.http import JsonResponse
    from django.shortcuts import get_object_or_404
    from financial_planning.models import PlanFinanciero, ProjectedBalanceSnapshot
    from django.http import QueryDict
    from financial_planning.views import api_get_projected_balance_data
    
    organization = getattr(request.user, 'organization', None)
    if not organization:
        from users.models import Organization
        organization = Organization.objects.first()
        
    plan = get_object_or_404(PlanFinanciero, id=plan_id, organization=organization)
    
    body = json.loads(request.body)
    scenario = body.get('scenario', 'BASE')
    
    q = QueryDict(mutable=True)
    q.update(request.GET)
    q['scenario'] = scenario
    request.GET = q
    
    api_response = api_get_projected_balance_data(request, plan_id)
    if api_response.status_code == 200:
        data = json.loads(api_response.content)
        
        snapshot, created = ProjectedBalanceSnapshot.objects.get_or_create(
            plan=plan,
            organization=organization,
            scenario=scenario,
            defaults={'data': data}
        )
        if not created:
            snapshot.data = data
            snapshot.save()
            
        return JsonResponse({'status': 'success', 'message': 'Snapshot guardado y aprobado.'})
    return JsonResponse({'status': 'error', 'message': 'Error calculando balance'}, status=400)


@login_required
@require_http_methods(["POST"])
def api_modify_bg_snapshot(request, plan_id):
    import json
    from django.http import JsonResponse
    from django.shortcuts import get_object_or_404
    from financial_planning.models import PlanFinanciero, ProjectedBalanceSnapshot
    
    organization = getattr(request.user, 'organization', None)
    if not organization:
        from users.models import Organization
        organization = Organization.objects.first()
        
    plan = get_object_or_404(PlanFinanciero, id=plan_id, organization=organization)
    
    body = json.loads(request.body)
    scenario = body.get('scenario', 'BASE')
    
    snapshot = ProjectedBalanceSnapshot.objects.filter(
        plan=plan, organization=organization, scenario=scenario
    ).first()
    
    if snapshot:
        snapshot.delete()
        
    return JsonResponse({'status': 'success', 'message': 'Snapshot modificado/eliminado.'})


@login_required
@require_http_methods(["POST"])
def api_save_bg_adjustment(request, plan_id):
    import json
    from django.http import JsonResponse
    from django.shortcuts import get_object_or_404
    from financial_planning.models import PlanFinanciero, ProjectedBalanceAdjustment
    
    organization = getattr(request.user, 'organization', None)
    if not organization:
        from users.models import Organization
        organization = Organization.objects.first()
        
    plan = get_object_or_404(PlanFinanciero, id=plan_id, organization=organization)
    
    body = json.loads(request.body)
    account_code = body.get('account_code')
    scenario = body.get('scenario', 'BASE')
    adjustments = body.get('adjustments', {})
    
    if not account_code:
        return JsonResponse({'status': 'error', 'message': 'Cuenta requerida'}, status=400)
        
    adj, _ = ProjectedBalanceAdjustment.objects.get_or_create(
        plan=plan, organization=organization, scenario=scenario, account_code=account_code,
        defaults={'adjustments': {}}
    )
    
    current = adj.adjustments or {}
    for k, v in adjustments.items():
        if v is None or v == "":
            current.pop(str(k), None)
        else:
            current[str(k)] = v
    adj.adjustments = current
    adj.save()
    
    return JsonResponse({'status': 'success'})


@login_required
@require_http_methods(["POST"])
def api_toggle_fixed_bg_account(request, plan_id):
    import json
    from django.http import JsonResponse
    from django.shortcuts import get_object_or_404
    from financial_planning.models import PlanFinanciero, ProjectedBalanceAdjustment
    
    organization = getattr(request.user, 'organization', None)
    if not organization:
        from users.models import Organization
        organization = Organization.objects.first()
        
    plan = get_object_or_404(PlanFinanciero, id=plan_id, organization=organization)
    
    body = json.loads(request.body)
    account_code = body.get('account_code')
    scenario = body.get('scenario', 'BASE')
    is_fixed = body.get('is_fixed', False)
    
    if not account_code:
        return JsonResponse({'status': 'error', 'message': 'Cuenta requerida'}, status=400)
        
    adj, _ = ProjectedBalanceAdjustment.objects.get_or_create(
        plan=plan, organization=organization, scenario=scenario, account_code=account_code,
        defaults={'adjustments': {}}
    )
    
    current = adj.adjustments or {}
    current['is_fixed'] = is_fixed
    adj.adjustments = current
    adj.save()
    
    return JsonResponse({'status': 'success'})


@login_required
@require_http_methods(["POST"])
def api_clear_other_trends(request, plan_id):
    import json
    from django.http import JsonResponse
    from django.shortcuts import get_object_or_404
    from financial_planning.models import PlanFinanciero, ProjectedBalanceAdjustment
    
    organization = getattr(request.user, 'organization', None)
    if not organization:
        from users.models import Organization
        organization = Organization.objects.first()
        
    plan = get_object_or_404(PlanFinanciero, id=plan_id, organization=organization)
    
    body = json.loads(request.body)
    scenario = body.get('scenario')
    clear_type = body.get('clear_type', 'auto')
    
    adjs = ProjectedBalanceAdjustment.objects.filter(plan=plan, organization=organization)
    if scenario:
        adjs = adjs.filter(scenario=scenario)
        
    count = 0
    for adj in adjs:
        is_fixed = str(adj.adjustments.get('is_fixed', '')).lower() in ['true', '1']
        should_delete = False
        
        if clear_type == 'auto' and not is_fixed:
            should_delete = True
        elif clear_type == 'sync' and is_fixed:
            should_delete = True
        elif clear_type == 'all':
            should_delete = True
            
        if should_delete:
            adj.delete()
            count += 1
            
    return JsonResponse({'status': 'success', 'deleted': count})


@login_required
@require_http_methods(["GET"])
def api_get_cash_flow_data(request, plan_id):
    import json
    from django.http import JsonResponse
    from django.shortcuts import get_object_or_404
    from financial_planning.models import PlanFinanciero, SimulacionEscenario, ProyeccionMensual, BudgetVersion, BudgetLine, BudgetLineDetail
    from liquidity_risk.models import LiqBalanceDetail
    
    organization = getattr(request.user, 'organization', None)
    if not organization:
        from users.models import Organization
        organization = Organization.objects.first()
        
    plan = get_object_or_404(PlanFinanciero, id=plan_id, organization=organization)
    scenario = request.GET.get('scenario', 'BASE')
    
    base_year = plan.anio_base - 1
    
    from django.db.models import Max
    max_month_dict = LiqBalanceDetail.objects.filter(
        period__year=base_year,
        upload__status='SUCCESS'
    ).aggregate(max_month=Max('period__month'))
    max_month = max_month_dict['max_month'] if max_month_dict['max_month'] else 12

    dec_qs = list(LiqBalanceDetail.objects.filter(
        period__year=base_year, 
        period__month=max_month, 
        upload__status='SUCCESS'
    ).values('account_code', 'balance'))
    
    saldo_inicial_caja = 0.0
    for r in dec_qs:
        if str(r['account_code']).startswith('11'):
            saldo_inicial_caja += abs(float(r['balance']))
            
    cf_history = plan.historical_data.get('cf_adjustments', {}).get(scenario, {}) if plan.historical_data else {}
    
    sim_cartera = SimulacionEscenario.objects.filter(plan=plan, organization=organization, variable_id='cartera').first()
    proj_cartera = []
    if sim_cartera:
        field = 'valor_base'
        if scenario == 'OPTIMISTIC': field = 'valor_optimista'
        elif scenario == 'PESSIMISTIC': field = 'valor_pesimista'
        elif scenario == 'MC_BASE': field = 'mc_base'
        elif scenario == 'MC_OPTIMISTIC': field = 'mc_optimista'
        elif scenario == 'MC_PESSIMISTIC': field = 'mc_pesimista'
        proj_cartera = [float(getattr(p, field, 0) or 0) for p in ProyeccionMensual.objects.filter(escenario=sim_cartera).order_by('mes_proyeccion')]
        
    sim_ahorros = SimulacionEscenario.objects.filter(plan=plan, organization=organization, variable_id='ahorros').first()
    proj_ahorros = []
    if sim_ahorros:
        field = 'valor_base'
        if scenario == 'OPTIMISTIC': field = 'valor_optimista'
        elif scenario == 'PESSIMISTIC': field = 'valor_pesimista'
        elif scenario == 'MC_BASE': field = 'mc_base'
        elif scenario == 'MC_OPTIMISTIC': field = 'mc_optimista'
        elif scenario == 'MC_PESSIMISTIC': field = 'mc_pesimista'
        proj_ahorros = [float(getattr(p, field, 0) or 0) for p in ProyeccionMensual.objects.filter(escenario=sim_ahorros).order_by('mes_proyeccion')]
        
    sim_dpf = SimulacionEscenario.objects.filter(plan=plan, organization=organization, variable_id='dpf').first()
    proj_dpf = []
    if sim_dpf:
        field = 'valor_base'
        if scenario == 'OPTIMISTIC': field = 'valor_optimista'
        elif scenario == 'PESSIMISTIC': field = 'valor_pesimista'
        elif scenario == 'MC_BASE': field = 'mc_base'
        elif scenario == 'MC_OPTIMISTIC': field = 'mc_optimista'
        elif scenario == 'MC_PESSIMISTIC': field = 'mc_pesimista'
        proj_dpf = [float(getattr(p, field, 0) or 0) for p in ProyeccionMensual.objects.filter(escenario=sim_dpf).order_by('mes_proyeccion')]

    version = BudgetVersion.objects.filter(plan_financiero=plan, organization=organization, scenario=scenario).order_by('-created_at').first()
    if not version:
        version = BudgetVersion.objects.filter(plan_financiero=plan, organization=organization, scenario='BASE').order_by('-created_at').first()
        
    ingresos_op = [0.0]*36
    egresos_op = [0.0]*36
    if version:
        lines = BudgetLine.objects.filter(version=version).select_related('item').prefetch_related('details')
        for line in lines:
            details = sorted(list(line.details.all()), key=lambda d: d.period_index)
            cat = line.item.category
            is_income = cat in ['ING_FIN', 'ING_SERV', 'OTROS_ING']
            for i in range(12):
                if i < len(details):
                    val = float(details[i].amount)
                    if is_income: ingresos_op[i] += val
                    else: egresos_op[i] += val
            
            y2 = float(line.total_amount_y2 or 0)
            y3 = float(line.total_amount_y3 or 0)
            if is_income:
                for i in range(12, 24): ingresos_op[i] += y2/12
                for i in range(24, 36): ingresos_op[i] += y3/12
            else:
                for i in range(12, 24): egresos_op[i] += y2/12
                for i in range(24, 36): egresos_op[i] += y3/12

    rows = []
    def add_row(code, name, values):
        r = {
            "code": code,
            "name": name,
            "cat": "Flujo de Caja",
            "is_total": False,
            "base": sum(values[:12]) / 12 if values else 0,
            "m1_12": values[:12],
            "y1": sum(values[:12]),
            "y2": sum(values[12:24]),
            "y3": sum(values[24:36]),
        }
        m1_12_actual = []
        y2_actual = 0
        y3_actual = 0
        for i in range(36):
            val = values[i] if i < len(values) else 0
            adj = cf_history.get(code, {}).get(str(i+1))
            if adj is not None: val = float(adj)
            
            if i < 12: m1_12_actual.append(val)
            elif i < 24: y2_actual += val
            else: y3_actual += val
            
        r["m1_12"] = m1_12_actual
        r["months"] = m1_12_actual
        r["y1"] = sum(m1_12_actual)
        r["y2"] = y2_actual
        r["y3"] = y3_actual
        rows.append(r)
        return m1_12_actual + [y2_actual/12]*12 + [y3_actual/12]*12
        
    ingresos_arr = add_row('ING', 'Ingresos Operativos', ingresos_op)
    egresos_arr = add_row('EGR', '(-) Egresos Operativos', [-x for x in egresos_op])
    
    prev_c = float(sum(x['balance'] for x in dec_qs if str(x['account_code']).startswith('14') and not str(x['account_code']).startswith('149')))
    recup = [0.0]*36
    desem = [0.0]*36
    for i in range(36):
        c = proj_cartera[i] if i < len(proj_cartera) else prev_c
        delta = c - prev_c
        if delta > 0: desem[i] = -delta
        else: recup[i] = -delta
        prev_c = c
        
    recup_arr = add_row('RECUP', 'Recuperación de Cartera', recup)
    desem_arr = add_row('DESEM', '(-) Desembolsos de Cartera', desem)
    
    prev_p = float(sum(x['balance'] for x in dec_qs if str(x['account_code']).startswith('211') or str(x['account_code']).startswith('212')))
    ing_pas = [0.0]*36
    ret_pas = [0.0]*36
    for i in range(36):
        a = proj_ahorros[i] if i < len(proj_ahorros) else 0
        d = proj_dpf[i] if i < len(proj_dpf) else 0
        p = a + d
        delta = p - prev_p
        if delta > 0: ing_pas[i] = delta
        else: ret_pas[i] = -delta
        prev_p = p
        
    ingpas_arr = add_row('ING_PAS', 'Captaciones del Público', ing_pas)
    retpas_arr = add_row('RET_PAS', '(-) Retiros del Público', ret_pas)
    
    flujo_neto = {
        "name": "Flujo Neto Mensual",
        "m1_12": [0]*12, "y1": 0, "y2": 0, "y3": 0,
        "cat": "RESULTADOS", "months": [0]*12, "base": 0, "is_total": True
    }
    
    for i in range(12):
        s = sum(r["m1_12"][i] for r in rows)
        flujo_neto["m1_12"][i] = s
        flujo_neto["months"][i] = s
    flujo_neto["y1"] = sum(r["y1"] for r in rows)
    flujo_neto["y2"] = sum(r["y2"] for r in rows)
    flujo_neto["y3"] = sum(r["y3"] for r in rows)
    
    saldo_inicial = {
        "name": "Saldo Inicial de Caja",
        "m1_12": [0]*12, "y1": saldo_inicial_caja, "y2": 0, "y3": 0,
        "cat": "RESULTADOS", "months": [0]*12, "base": 0, "is_total": True
    }
    saldo_final = {
        "name": "Saldo Final de Caja",
        "m1_12": [0]*12, "y1": 0, "y2": 0, "y3": 0,
        "cat": "RESULTADOS", "months": [0]*12, "base": 0, "is_total": True
    }
    
    current_saldo = saldo_inicial_caja
    for i in range(12):
        saldo_inicial["m1_12"][i] = current_saldo
        saldo_inicial["months"][i] = current_saldo
        current_saldo += flujo_neto["m1_12"][i]
        saldo_final["m1_12"][i] = current_saldo
        saldo_final["months"][i] = current_saldo
        
    saldo_final["y1"] = current_saldo
    saldo_inicial["y2"] = current_saldo
    current_saldo += flujo_neto["y2"]
    saldo_final["y2"] = current_saldo
    
    saldo_inicial["y3"] = current_saldo
    current_saldo += flujo_neto["y3"]
    saldo_final["y3"] = current_saldo
    
    rows.append(saldo_inicial)
    rows.append(flujo_neto)
    rows.append(saldo_final)
    
    return JsonResponse({
        "status": "success",
        "rows": rows,
        "flujo_neto": flujo_neto,
        "saldo_inicial": saldo_inicial,
        "saldo_final": saldo_final
    })

@login_required
@require_http_methods(["POST"])
def api_save_cf_adjustment(request, plan_id):
    import json
    from django.http import JsonResponse
    from django.shortcuts import get_object_or_404
    from financial_planning.models import PlanFinanciero
    
    organization = getattr(request.user, 'organization', None)
    if not organization:
        from users.models import Organization
        organization = Organization.objects.first()
        
    plan = get_object_or_404(PlanFinanciero, id=plan_id, organization=organization)
    
    body = json.loads(request.body)
    scenario = body.get('scenario', 'BASE')
    code = body.get('code')
    adjustments = body.get('adjustments', {})
    
    if not code:
        return JsonResponse({'status': 'error', 'message': 'Código requerido'}, status=400)
        
    hist = plan.historical_data or {}
    if 'cf_adjustments' not in hist: hist['cf_adjustments'] = {}
    if scenario not in hist['cf_adjustments']: hist['cf_adjustments'][scenario] = {}
    if code not in hist['cf_adjustments'][scenario]: hist['cf_adjustments'][scenario][code] = {}
    
    for k, v in adjustments.items():
        if v is None or v == "":
            hist['cf_adjustments'][scenario][code].pop(str(k), None)
        else:
            hist['cf_adjustments'][scenario][code][str(k)] = v
            
    plan.historical_data = hist
    plan.save()
    
    return JsonResponse({'status': 'success'})
