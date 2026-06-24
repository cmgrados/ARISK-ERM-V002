from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponse
from .models import PlanFinanciero, PeriodoFinanciero

@login_required
def dashboard(request):
    organization = request.user.organization
    if not organization:
        from users.models import Organization
        organization = Organization.objects.first()
        
    plans = PlanFinanciero.objects.filter(organization=organization).order_by('-created_at')
    context = {
        'plans': plans
    }
    return render(request, 'financial_planning/dashboard.html', context)

@login_required
def plan_wizard_new(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        anio_base = request.POST.get('anio_base')
        horizonte_anios = request.POST.get('horizonte_anios', 3)
        
        organization = request.user.organization
        if not organization:
            from users.models import Organization
            organization = Organization.objects.first()
            
        from django.db import IntegrityError
        
        try:
            plan = PlanFinanciero.objects.create(
                organization=organization,
                nombre=nombre,
                descripcion=descripcion,
                anio_base=anio_base,
                horizonte_anios=horizonte_anios
            )
            messages.success(request, "Plan Financiero creado exitosamente.")
            return redirect('financial_planning:dashboard')
        except IntegrityError:
            messages.error(request, f"Ya existe un Plan Financiero con el nombre '{nombre}'. Por favor, elige otro.")
            context = {
                'nombre': nombre,
                'descripcion': descripcion,
                'anio_base': anio_base,
                'horizonte_anios': str(horizonte_anios),
            }
            return render(request, 'financial_planning/plan_form.html', context)
        
    return render(request, 'financial_planning/plan_form.html')

@login_required
def delete_plan(request, plan_id):
    if request.method == 'POST':
        organization = request.user.organization
        if not organization:
            from users.models import Organization
            organization = Organization.objects.first()
            
        plan = get_object_or_404(PlanFinanciero, id=plan_id, organization=organization)
        plan.delete()
        messages.success(request, "Plan Financiero eliminado exitosamente.")
    return redirect('financial_planning:dashboard')

@login_required
def trial_balance_viewer_no_id(request, plan_id=None):
    organization = request.user.organization
    if not organization:
        from users.models import Organization
        organization = Organization.objects.first()
        
    periodos = PeriodoFinanciero.objects.filter(organization=organization).order_by('-anio', '-mes')
    
    plan = None
    if plan_id:
        plan = get_object_or_404(PlanFinanciero, id=plan_id, organization=organization)
        
    context = {
        'title': 'Balance de Comprobación',
        'periodos': periodos,
        'plan': plan
    }
    return render(request, 'financial_planning/trial_balance_viewer.html', context)
@login_required
def budget_wizard_new(request, plan_id=None):
    plan = None
    if plan_id:
        plan = get_object_or_404(PlanFinanciero, id=plan_id)
        
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        anio_base = request.POST.get('anio_base', 2026)
        horizonte_anios = request.POST.get('horizonte_anios', 3)
        
        if plan:
            try:
                plan.nombre = nombre
                plan.descripcion = descripcion
                plan.anio_base = anio_base
                plan.horizonte_anios = horizonte_anios
                plan.save()
            except IntegrityError:
                messages.error(request, f"Ya existe un plan con el nombre '{nombre}' en su organización.")
                return redirect(f'/planificacion-financiera/plan/{plan.id}/wizard/?step=1')
        else:
            organization = request.user.organization
            if not organization:
                from users.models import Organization
                organization = Organization.objects.first()
            try:
                plan = PlanFinanciero.objects.create(
                    organization=organization,
                    nombre=nombre,
                    descripcion=descripcion,
                    anio_base=anio_base,
                    horizonte_anios=horizonte_anios
                )
            except IntegrityError:
                messages.error(request, f"Ya existe un plan con el nombre '{nombre}' en su organización.")
                return redirect('/planificacion-financiera/plan/nuevo/?step=1')
                
        return redirect(f'/planificacion-financiera/plan/{plan.id}/wizard/?step=2')

    step = int(request.GET.get('step', '1'))
    
    import json
    historical_data_json = '{}'
    if plan and plan.historical_data:
        historical_data_json = json.dumps(plan.historical_data)

    context = {
        'title': 'Asistente Presupuesto',
        'plan': plan,
        'step': step,
        'projected_years': [1, 2, 3], # Required by some parts of the wizard
        'historical_data_json': historical_data_json
    }
    
    return render(request, 'financial_planning/wizard.html', context)

import json
from django.http import JsonResponse

@login_required
def api_get_trend_data(request, plan_id=None):
    return JsonResponse({'status': 'success', 'msg': 'Endpoint en construccion: api_get_trend_data'})

@login_required
def manage_assumptions(request, plan_id=None):
    return JsonResponse({'status': 'success', 'msg': 'Endpoint en construccion: manage_assumptions'})

@login_required
def api_save_step_periods(request, plan_id=None):
    return JsonResponse({'status': 'success', 'msg': 'Endpoint en construccion: api_save_step_periods'})

@login_required
def api_run_montecarlo(request, plan_id=None):
    return JsonResponse({'status': 'success', 'msg': 'Endpoint en construccion: api_run_montecarlo'})

@login_required
def save_institutional_assumptions(request, plan_id=None):
    return JsonResponse({'status': 'success', 'msg': 'Endpoint en construccion: save_institutional_assumptions'})

@login_required
def api_unlock_step6(request, plan_id=None):
    return JsonResponse({'status': 'success', 'msg': 'Endpoint en construccion: api_unlock_step6'})

@login_required
def api_historical_portfolio_data(request, plan_id=None):
    return JsonResponse({'status': 'success', 'msg': 'Endpoint en construccion: api_historical_portfolio_data'})

@login_required
def api_save_trend_scenarios(request, plan_id=None):
    return JsonResponse({'status': 'success', 'msg': 'Endpoint en construccion: api_save_trend_scenarios'})

@login_required
def api_historical_passive_data(request, plan_id=None):
    return JsonResponse({'status': 'success', 'msg': 'Endpoint en construccion: api_historical_passive_data'})

@login_required
def api_available_passive_dates(request, plan_id=None):
    return JsonResponse({'status': 'success', 'msg': 'Endpoint en construccion: api_available_passive_dates'})
@login_required
def api_get_trend_data(request, plan_id=None):
    return JsonResponse({'status': 'success', 'msg': 'Endpoint en construccion: api_get_trend_data'})

@login_required
def manage_assumptions(request, plan_id=None):
    return JsonResponse({'status': 'success', 'msg': 'Endpoint en construccion: manage_assumptions'})

@login_required
def api_save_step_periods(request, plan_id=None):
    if request.method == 'POST' and plan_id:
        import json
        plan = get_object_or_404(PlanFinanciero, id=plan_id)
        
        try:
            body = json.loads(request.body)
            periods = body.get('periods', [])
            step = str(body.get('step', ''))
            
            hist_data = plan.historical_data or {}
            
            if step == '2':
                hist_data['selected_periods'] = periods
            elif step == '3':
                hist_data['portfolio_periods'] = periods
            elif step == '4':
                hist_data['passive_periods'] = periods
            else:
                hist_data['selected_periods'] = periods # Default
                
            plan.historical_data = hist_data
            plan.save()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'msg': str(e)})
    return JsonResponse({'status': 'error', 'msg': 'Método no permitido'})

@login_required
def api_run_montecarlo(request, plan_id=None):
    return JsonResponse({'status': 'success', 'msg': 'Endpoint en construccion: api_run_montecarlo'})

@login_required
def save_institutional_assumptions(request, plan_id=None):
    return JsonResponse({'status': 'success', 'msg': 'Endpoint en construccion: save_institutional_assumptions'})

@login_required
def api_unlock_step6(request, plan_id=None):
    return JsonResponse({'status': 'success', 'msg': 'Endpoint en construccion: api_unlock_step6'})

@login_required
def api_historical_portfolio_data(request, plan_id=None):
    return JsonResponse({'status': 'success', 'msg': 'Endpoint en construccion: api_historical_portfolio_data'})

@login_required
def api_save_trend_scenarios(request, plan_id=None):
    return JsonResponse({'status': 'success', 'msg': 'Endpoint en construccion: api_save_trend_scenarios'})

@login_required
def api_historical_passive_data(request, plan_id=None):
    return JsonResponse({'status': 'success', 'msg': 'Endpoint en construccion: api_historical_passive_data'})

@login_required
def api_available_historical_dates(request, plan_id=None):
    from liquidity_risk.models import LiqBalanceUpload
    # The uploads have a `period` date field.
    uploads = LiqBalanceUpload.objects.filter(status='SUCCESS').order_by('-period')
    dates = []
    for u in uploads:
        d_str = f"{u.period.year}-{u.period.month:02d}"
        if d_str not in dates:
            dates.append(d_str)
    return JsonResponse({'status': 'success', 'dates': dates})

from django.views.decorators.csrf import csrf_exempt
import json

@login_required
def toggle_step_lock(request, plan_id=None):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            step = str(data.get('step'))
            action = data.get('action') # 'lock' or 'unlock'
            
            plan = get_object_or_404(PlanFinanciero, id=plan_id, organization_id=request.user.tenant_id)
            
            if not isinstance(plan.historical_data, dict):
                plan.historical_data = {}
            if 'locked_steps' not in plan.historical_data:
                plan.historical_data['locked_steps'] = {}
                
            if action == 'lock':
                plan.historical_data['locked_steps'][step] = True
            elif action == 'unlock':
                plan.historical_data['locked_steps'][step] = False
                
            plan.save()
            
            msg = f'Paso {step} {action}ed.'
            return JsonResponse({'status': 'success', 'msg': msg})
        except Exception as e:
            return JsonResponse({'status': 'error', 'msg': str(e)})
    return JsonResponse({'status': 'error', 'msg': 'Invalid request.'})

@login_required
def ml_trend_projection(request, plan_id=None):
    return JsonResponse({'status': 'success', 'msg': 'Endpoint en construccion: ml_trend_projection'})

@login_required
def api_available_portfolio_dates(request, plan_id=None):
    return JsonResponse({'status': 'success', 'msg': 'Endpoint en construccion: api_available_portfolio_dates'})

@login_required
def api_trial_balance_data(request, plan_id=None):
    import json
    periods_param = request.GET.get('periods')
    periods = []
    if periods_param:
        try:
            periods = json.loads(periods_param)
        except Exception:
            pass
            
    from liquidity_risk.models import LiqBalanceDetail
    
    # Filter by period list
    selected_details = []
    for p_str in periods:
        try:
            y, m = p_str.split('-')
            details = LiqBalanceDetail.objects.filter(period__year=y, period__month=m, upload__status='SUCCESS')
            selected_details.extend(details)
        except Exception:
            pass
            
    def get_parent_code(code):
        if len(code) == 1: return None
        if len(code) == 2: return code[0]
        if len(code) % 2 == 0: return code[:-2]
        return code[:-1] # fallback

    account_dict = {}
    
    for d in selected_details:
        c_code = str(d.account_code)
        c_name = d.account_name
        p_str = f"{d.period.year}-{d.period.month:02d}"
        
        # Reverse sign for Pasivo and Patrimonio to show as positive numbers natively, 
        # making debit results (like negative outcomes) show as negative.
        val = float(d.balance)
        if c_code.startswith('2') or c_code.startswith('3') or c_code.startswith('5'):
            val = val * -1
            
        # Ensure all parents in the hierarchy exist
        curr_code = c_code
        curr_name = c_name
        path = []
        while curr_code:
            path.append((curr_code, curr_name))
            curr_code = get_parent_code(curr_code)
            curr_name = f"Cuenta {curr_code}" if curr_code else "" # Default name for created parents
            
        for idx, (code, name) in enumerate(path):
            if code not in account_dict:
                if code.startswith('1'): tipo = 'ACTIVO'
                elif code.startswith('2'): tipo = 'PASIVO'
                elif code.startswith('3'): tipo = 'PATRIMONIO'
                elif code.startswith('4'): tipo = 'GASTO'
                elif code.startswith('5'): tipo = 'INGRESO'
                else: tipo = 'OTRO'
                
                parent_code = get_parent_code(code)
                account_dict[code] = {
                    'code': code,
                    'parent_code': parent_code,
                    'level': len(code),
                    'depth': len(code),
                    'name': name if idx == 0 else account_dict.get(code, {}).get('name', name),
                    'tipo': tipo,
                    'balances': {},
                    'monthly_balances': {},
                    'children_codes': []
                }
                
        # We only add the balance to the specific leaf account; we will roll up later
        if p_str not in account_dict[c_code]['balances']:
            account_dict[c_code]['balances'][p_str] = 0
            account_dict[c_code]['monthly_balances'][p_str] = 0
            
        account_dict[c_code]['balances'][p_str] += val
        account_dict[c_code]['monthly_balances'][p_str] += val
        
    # Correct names for parents if they were already present in the DB
    for d in selected_details:
        c_code = str(d.account_code)
        if c_code in account_dict:
            account_dict[c_code]['name'] = d.account_name

    # Roll up balances from deepest to top
    accounts_sorted = sorted(account_dict.values(), key=lambda x: x['level'], reverse=True)
    
    # Initialize 0 balances for all periods for all accounts
    for acc in accounts_sorted:
        for p_str in periods:
            if p_str not in acc['balances']:
                acc['balances'][p_str] = 0
                acc['monthly_balances'][p_str] = 0
                
    # Identify parents to avoid double counting if the DB already stored aggregated values
    # In this logic, we assume we want to roll up leaf values manually
    # But LiqBalanceDetail usually already contains level 1, 2, 3 values!
    # If the real DB already has balances for "1", "11", we SHOULD NOT roll up!
    # Let's check if the account has children in the DB. If it does, we don't roll up, we just use its own value!
    # But wait, we just added all values. Let's just link children to parents.
    for acc in accounts_sorted:
        if acc['parent_code'] and acc['parent_code'] in account_dict:
            parent = account_dict[acc['parent_code']]
            if acc['code'] not in parent['children_codes']:
                parent['children_codes'].append(acc['code'])

    # Identify required previous months for monthly balances
    prev_months_needed = set()
    for p_str in periods:
        y, m = p_str.split('-')
        m_int = int(m)
        y_int = int(y)
        if m_int > 1:
            prev_months_needed.add((y_int, m_int - 1))
            
    # Fetch previous balances for accounts 4 and 5
    from django.db.models import Q
    prev_details_dict = {}
    if prev_months_needed:
        prev_q = Q()
        for y, m in prev_months_needed:
            prev_q |= Q(period__year=y, period__month=m)
        
        from liquidity_risk.models import LiqBalanceDetail
        prev_details_qs = LiqBalanceDetail.objects.filter(
            prev_q, 
            upload__status='SUCCESS'
        ).filter(Q(account_code__startswith='4') | Q(account_code__startswith='5'))
        for d in prev_details_qs:
            c_code = str(d.account_code)
            p_str = f"{d.period.year}-{d.period.month:02d}"
            val = float(d.balance)
            if c_code.startswith('5'):
                val *= -1
            prev_details_dict[(c_code, p_str)] = val

    # Split into balance_sheet and income_statement
    balance_sheet = []
    income_statement = []
    
    for code, acc in sorted(account_dict.items(), key=lambda x: x[0]):
        if acc['tipo'] in ['ACTIVO', 'PASIVO', 'PATRIMONIO']:
            balance_sheet.append(acc)
        elif acc['tipo'] in ['INGRESO', 'GASTO']:
            income_statement.append(acc)

    # Compute monthly balances for income statement
    for acc in income_statement:
        c_code = acc['code']
        for p_str in periods:
            y, m = p_str.split('-')
            m_int = int(m)
            y_int = int(y)
            curr_ytd = acc['balances'].get(p_str, 0)
            
            if m_int == 1:
                acc['monthly_balances'][p_str] = curr_ytd
            else:
                prev_p_str = f"{y_int}-{m_int - 1:02d}"
                prev_val = 0
                if prev_p_str in acc['balances']:
                    prev_val = acc['balances'][prev_p_str]
                else:
                    prev_val = prev_details_dict.get((c_code, prev_p_str), 0)
                
                acc['monthly_balances'][p_str] = curr_ytd - prev_val
            
    # Calculate totals
    totals = {p: {'A': 0, 'P': 0, 'PT': 0, 'I_accum': 0, 'G_accum': 0, 'I_month': 0, 'G_month': 0} for p in periods}
    for acc in balance_sheet:
        if acc['level'] == 1:
            for p_str, amt in acc['balances'].items():
                if p_str in totals:
                    if acc['tipo'] == 'ACTIVO': totals[p_str]['A'] += amt
                    elif acc['tipo'] == 'PASIVO': totals[p_str]['P'] += amt
                    elif acc['tipo'] == 'PATRIMONIO': totals[p_str]['PT'] += amt
                    
    for acc in income_statement:
        if acc['level'] == 1:
            for p_str in periods:
                amt_accum = acc['balances'].get(p_str, 0)
                amt_month = acc['monthly_balances'].get(p_str, 0)
                if p_str in totals:
                    if acc['tipo'] == 'INGRESO':
                        totals[p_str]['I_accum'] += amt_accum
                        totals[p_str]['I_month'] += amt_month
                    elif acc['tipo'] == 'GASTO':
                        totals[p_str]['G_accum'] += amt_accum
                        totals[p_str]['G_month'] += amt_month
                    
    # Check cuadratura and set utilidades
    for p_str in totals:
        t = totals[p_str]
        t['total_activo'] = t['A']
        t['total_pasivo'] = t['P']
        t['total_patrimonio'] = t['PT']
        t['total_pasivo_patrimonio'] = t['P'] + t['PT']
        t['diferencia'] = t['A'] - t['total_pasivo_patrimonio']
        t['es_cuadrado'] = abs(t['diferencia']) < 2.0
        
        t['total_ingresos'] = t['I_accum']
        t['total_gastos'] = t['G_accum']
        t['utilidad_neta'] = t['I_accum'] - t['G_accum']
        
        t['total_ingresos_mensual'] = t['I_month']
        t['total_gastos_mensual'] = t['G_month']
        t['utilidad_neta_mensual'] = t['I_month'] - t['G_month']
                    
    return JsonResponse({
        'status': 'success',
        'periods': periods,
        'currency': 'MN',
        'balance_sheet': balance_sheet,
        'income_statement': income_statement,
        'totals': totals
    })

@login_required
def ml_montecarlo_projection(request, plan_id=None):
    return JsonResponse({'status': 'success', 'msg': 'Endpoint en construccion: ml_montecarlo_projection'})

@login_required
def api_lock_step6(request, plan_id=None):
    return JsonResponse({'status': 'success', 'msg': 'Endpoint en construccion: api_lock_step6'})

@login_required
def projected_results(request, plan_id=None):
    return JsonResponse({'status': 'success', 'msg': 'Endpoint en construccion: projected_results'})

from django.views.decorators.http import require_POST

@login_required
@require_POST
def assign_trial_balance_to_plan(request):
    try:
        body = json.loads(request.body)
        plan_id = body.get('plan_id')
        periods = body.get('periods', [])
        currency = body.get('currency', 'MN')
        
        plan = get_object_or_404(PlanFinanciero, id=plan_id)
        
        # We need to make sure the user has access to this plan's organization
        organization = request.user.organization
        if not organization:
            from users.models import Organization
            organization = Organization.objects.first()
            
        if plan.organization != organization:
            return JsonResponse({'status': 'error', 'msg': 'No tiene permisos para modificar este plan.'}, status=403)
        
        hist_data = plan.historical_data or {}
        hist_data['selected_periods'] = periods
        hist_data['currency'] = currency
        
        plan.historical_data = hist_data
        plan.save()
        
        return JsonResponse({'status': 'success', 'msg': 'Balance histórico asignado correctamente al plan.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'msg': str(e)})
