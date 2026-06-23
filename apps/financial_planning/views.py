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
    from .models import PeriodoFinanciero
    from users.models import Organization
    organization = request.user.organization
    if not organization:
        organization = Organization.objects.first()
        
    periodos = PeriodoFinanciero.objects.filter(organization=organization, estado='FINAL').order_by('-anio', '-mes')
    dates = [f"{p.anio}-{p.mes:02d}" for p in periodos]
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
                
            plan.historical_data['locked_steps'][step] = (action == 'lock')
            plan.save()
            
            msg = 'Paso bloqueado correctamente.' if action == 'lock' else 'Paso desbloqueado.'
            return JsonResponse({'status': 'success', 'msg': msg})
        except Exception as e:
            return JsonResponse({'status': 'error', 'msg': str(e)})
    return JsonResponse({'status': 'error', 'msg': 'Método no permitido.'})

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
            
    organization = request.user.organization
    if not organization:
        from users.models import Organization
        organization = Organization.objects.first()

    # Query the balances for the selected periods
    from django.db.models import Sum
    from .models import PeriodoFinanciero, CuentaContable, BalanceDetalle
    
    # Filter periods
    selected_period_objs = []
    for p_str in periods:
        try:
            y, m = p_str.split('-')
            y, m = int(y), int(m)
            p_obj = PeriodoFinanciero.objects.filter(organization=organization, anio=y, mes=m).first()
            if p_obj:
                selected_period_objs.append(p_obj)
        except Exception:
            pass
            
    # Get all accounts that have balances in these periods, plus their parents
    balances = BalanceDetalle.objects.filter(periodo__in=selected_period_objs)
    
    account_dict = {}
    for b in balances:
        c = b.cuenta
        p_str = f"{b.periodo.anio}-{b.periodo.mes:02d}"
        
        # Build path to root to ensure all parents exist
        path = []
        curr = c
        while curr:
            path.append(curr)
            curr = curr.parent
            
        for acc in path:
            if acc.codigo not in account_dict:
                account_dict[acc.codigo] = {
                    'code': acc.codigo,
                    'parent_code': acc.parent.codigo if acc.parent else None,
                    'level': acc.nivel,
                    'depth': acc.nivel,
                    'name': acc.nombre,
                    'tipo': acc.tipo,
                    'balances': {},
                    'monthly_balances': {},
                    'children_codes': []
                }
                
        # Add the balance to the specific account
        if p_str not in account_dict[c.codigo]['balances']:
            account_dict[c.codigo]['balances'][p_str] = 0
            account_dict[c.codigo]['monthly_balances'][p_str] = 0
            
        account_dict[c.codigo]['balances'][p_str] += float(b.monto)
        account_dict[c.codigo]['monthly_balances'][p_str] += float(b.monto)
        
    # Populate children_codes and roll up balances
    # Sort accounts by level (deepest first) to roll up
    accounts_sorted = sorted(account_dict.values(), key=lambda x: x['level'], reverse=True)
    
    # Identify parents to avoid double counting if the DB already stored aggregated values
    parent_codes = set(acc['parent_code'] for acc in accounts_sorted if acc['parent_code'])
    for acc in accounts_sorted:
        if acc['code'] in parent_codes:
            for p_str in periods:
                acc['balances'][p_str] = 0
                acc['monthly_balances'][p_str] = 0
                
    for acc in accounts_sorted:
        if acc['parent_code'] and acc['parent_code'] in account_dict:
            parent = account_dict[acc['parent_code']]
            if acc['code'] not in parent['children_codes']:
                parent['children_codes'].append(acc['code'])
                
            # Roll up balance
            for p_str, amt in acc['balances'].items():
                parent['balances'][p_str] = parent['balances'].get(p_str, 0) + amt
                parent['monthly_balances'][p_str] = parent['monthly_balances'].get(p_str, 0) + amt

    # Split into balance_sheet and income_statement
    balance_sheet = []
    income_statement = []
    
    for code, acc in sorted(account_dict.items(), key=lambda x: x[0]):
        if acc['tipo'] in ['ACTIVO', 'PASIVO', 'PATRIMONIO']:
            balance_sheet.append(acc)
        elif acc['tipo'] in ['INGRESO', 'GASTO']:
            income_statement.append(acc)
            
    # Calculate totals
    totals = {p: {'A': 0, 'P': 0, 'PT': 0} for p in periods}
    for acc in balance_sheet:
        if acc['level'] == 1:
            for p_str, amt in acc['balances'].items():
                if p_str in totals:
                    if acc['tipo'] == 'ACTIVO': totals[p_str]['A'] += amt
                    elif acc['tipo'] == 'PASIVO': totals[p_str]['P'] += amt
                    elif acc['tipo'] == 'PATRIMONIO': totals[p_str]['PT'] += amt
                    
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
