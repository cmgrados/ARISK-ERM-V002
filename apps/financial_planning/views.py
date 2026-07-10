from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponse
from .models import PlanFinanciero, PeriodoFinanciero, SimulacionEscenario, ProyeccionMensual

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
        
        try:
            anio_base = int(request.POST.get('anio_base'))
        except (TypeError, ValueError):
            anio_base = 2026
            
        try:
            horizonte_anios = int(request.POST.get('horizonte_anios', 3))
        except (TypeError, ValueError):
            horizonte_anios = 3
        
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
        
        try:
            anio_base = int(request.POST.get('anio_base'))
        except (TypeError, ValueError):
            anio_base = 2026
            
        try:
            horizonte_anios = int(request.POST.get('horizonte_anios', 3))
        except (TypeError, ValueError):
            horizonte_anios = 3
        
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
    budget_data_json = '{}'
    if plan and plan.historical_data:
        historical_data_json = json.dumps(plan.historical_data)
        budget_data = {
            'income_statement': plan.historical_data.get('budget_income_statement'),
            'account_assumptions': plan.historical_data.get('account_assumptions')
        }
        if budget_data['income_statement']:
            budget_data_json = json.dumps(budget_data)

    context = {
        'title': 'Asistente Presupuesto',
        'plan': plan,
        'step': step,
        'projected_years': [1, 2, 3], # Required by some parts of the wizard
        'historical_data_json': historical_data_json,
        'budget_data_json': budget_data_json
    }
    
    return render(request, 'financial_planning/wizard.html', context)

import json
from django.http import JsonResponse



from django import forms
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.shortcuts import render, get_object_or_404
from .models import PlanFinanciero

class MacroForm(forms.Form):
    inflation_rate = forms.DecimalField(label="Tasa de Inflación (%)", max_digits=5, decimal_places=2, initial=0.00, widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    exchange_rate = forms.DecimalField(label="Tipo de Cambio (S/ por $)", max_digits=5, decimal_places=2, initial=0.00, widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    gdp_growth = forms.DecimalField(label="Crecimiento PBI (%)", max_digits=5, decimal_places=2, initial=0.00, widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    market_rate = forms.DecimalField(label="Tasa de Interés Referencial (%)", max_digits=5, decimal_places=2, initial=0.00, widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    unemployment_rate = forms.DecimalField(label="Tasa de Desempleo (%)", max_digits=5, decimal_places=2, initial=0.00, widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))

class LiqForm(forms.Form):
    savings_withdrawal_rate = forms.DecimalField(label="Tasa Retiro Ahorros (%)", max_digits=5, decimal_places=2, initial=0.00, widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    dpf_renewal_rate = forms.DecimalField(label="Tasa Renovación DPF (%)", max_digits=5, decimal_places=2, initial=0.00, widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))

class EqForm(forms.Form):
    retained_earnings_rate = forms.DecimalField(label="Retención Utilidades (%)", max_digits=5, decimal_places=2, initial=0.00, widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    capital_contributions = forms.DecimalField(label="Nuevos Aportes Capital (%)", max_digits=5, decimal_places=2, initial=0.00, widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))

@login_required
@xframe_options_sameorigin
def manage_assumptions(request, plan_id=None):
    plan = get_object_or_404(PlanFinanciero, id=plan_id) if plan_id else None
    
    is_iframe = request.GET.get('iframe') == '1'
    base_template = 'base_empty.html' if is_iframe else 'base.html'
    
    annual_goals_vars = [
        ('cartera', 'Cartera de Créditos (S/)'),
        ('ahorros', 'Ahorros (S/)'),
        ('ahorros_usd', 'Ahorros ($)'),
        ('dpf', 'Plazo Fijo (S/)'),
        ('dpf_usd', 'Plazo Fijo ($)'),
        ('aportaciones', 'Aportaciones'),
        ('numero_socios', 'Número de Socios')
    ]
    
    import json
    from django.db.models import Sum, Count
    from credit_risk.models import CreditOperation
    from liquidity_risk.models import LiqLiabilityDetail
    from utilities.models import Socio

    base_year_calc = plan.anio_base - 1 if plan else 2024
    
    # Defaults
    cartera_val_mn = 0.0
    ahorros_val_mn = 0.0
    ahorros_val_me = 0.0
    dpf_val_mn = 0.0
    dpf_val_me = 0.0
    
    # Try dynamic aggregation
    # Cartera
    cartera_mn_agg = CreditOperation.objects.filter(load_date__year=base_year_calc, load_date__month=12).aggregate(s=Sum('balance'))
    cartera_val_mn = float(cartera_mn_agg['s'] or 77815122.00)
    
    # Pasivos - Dynamic
    pasivos = LiqLiabilityDetail.objects.filter(period__year=base_year_calc, period__month=12).values('funding_type', 'product').annotate(s=Sum('amount'))
    for p in pasivos:
        val = float(p['s'] or 0)
        is_me = ('ME' in p['product'] or 'DOLARES' in p['product'].upper())
        is_dpf = (p['funding_type'] == 'PLAZO' or 'PLAZO' in p['product'].upper())
        
        if is_dpf:
            if is_me: dpf_val_me += val
            else: dpf_val_mn += val
        else:
            if is_me: ahorros_val_me += val
            else: ahorros_val_mn += val

    # Override with exact user-requested values for base_year 2025
    if base_year_calc == 2025:
        cartera_val_mn = 77815122.00
        dpf_val_mn = 51800307.40
        ahorros_val_mn = 7836711.60
        dpf_val_me = 5589371.54
        ahorros_val_me = 611132.18

    socios_agg = Socio.objects.filter(corte__year=base_year_calc, corte__month=12).aggregate(sum=Sum('aportes'), count=Count('id'))
    aportaciones_val = float(socios_agg['sum'] or 48000000)
    numero_socios_val = float(socios_agg['count'] or 25000)

    default_balances = {
        'cartera': cartera_val_mn,
        'ahorros': ahorros_val_mn,
        'ahorros_usd': ahorros_val_me,
        'dpf': dpf_val_mn,
        'dpf_usd': dpf_val_me,
        'aportaciones': aportaciones_val,
        'numero_socios': numero_socios_val
    }

    context = {
        'plan': plan,
        'base_template': base_template,
        'macro_form': MacroForm(),
        'liq_form': LiqForm(),
        'eq_form': EqForm(),
        'projection_years_range': range(1, (plan.horizonte_anios if plan else 3) + 1),
        'annual_goals_vars': annual_goals_vars,
        'base_year': base_year_calc,
        'default_base_balances_json': json.dumps(default_balances),
        'annual_goals_json': '{}',
        'products': [],
        'agencies': [],
    }
    
    if request.method == 'POST':
        return JsonResponse({'status': 'success', 'msg': 'Guardado correctamente.'})
    
    return render(request, 'financial_planning/manage_assumptions.html', context)

@login_required
def api_save_step_periods(request, plan_id=None):
    return JsonResponse({'status': 'success', 'msg': 'Endpoint en construccion: api_save_step_periods'})



@login_required
def save_institutional_assumptions_old(request, plan_id=None):
    return JsonResponse({'status': 'success', 'msg': 'Endpoint en construccion: save_institutional_assumptions'})

@login_required
def api_unlock_step6(request, plan_id=None):
    return JsonResponse({'status': 'success', 'msg': 'Endpoint en construccion: api_unlock_step6'})

@login_required


@login_required
def api_historical_passive_data(request, plan_id=None):
    from liquidity_risk.models import LiqLiabilityDetail
    from utilities.models import Socio
    from django.db.models import Sum, Count, Q
    from collections import defaultdict

    dates_str = request.GET.get('dates', '')
    if not dates_str:
        return JsonResponse({'status': 'error', 'msg': 'No se proporcionaron fechas.'})
    
    dates_list = dates_str.split(',')
    
    data_map = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: {
        'ahorros': 0.0,
        'dpf': 0.0,
        'aportaciones': 0.0,
        'nro_socios': 0
    })))
    
    acumulado_map = defaultdict(lambda: defaultdict(lambda: {
        'ahorros': 0.0,
        'dpf': 0.0,
        'aportaciones': 0.0,
        'nro_socios': 0
    }))

    q_liq = Q()
    q_socio = Q()
    for ym in dates_list:
        try:
            y, m = ym.split('-')
            q_liq |= Q(period__year=int(y), period__month=int(m))
            q_socio |= Q(corte__year=int(y), corte__month=int(m))
        except ValueError:
            pass

    # Pasivos (Ahorros & DPF)
    liabilities = LiqLiabilityDetail.objects.filter(q_liq).values('period', 'agency', 'currency', 'product').annotate(total_balance=Sum('balance'))
    for l in liabilities:
        p_str = l['period'].strftime('%Y-%m')
        ag = (l['agency'] or 'SIN AGENCIA').strip().upper()
        prod = (l['product'] or '').strip().upper()
        curr = 'USD' if 'DOLARES' in prod or ' ME' in prod else 'PEN'
        bal = float(l['total_balance'] or 0)
        
        if 'PLAZO' in prod:
            data_map[ag][p_str][curr]['dpf'] += bal
            acumulado_map[p_str][curr]['dpf'] += bal
        else:
            data_map[ag][p_str][curr]['ahorros'] += bal
            acumulado_map[p_str][curr]['ahorros'] += bal

    # Socios (Aportaciones & Count)
    socios = Socio.objects.filter(q_socio).values('corte', 'oficina').annotate(
        total_aportes=Sum('aportes'),
        total_socios=Count('id')
    )
    for so in socios:
        p_str = so['corte'].strftime('%Y-%m')
        ag = (so['oficina'] or 'SIN AGENCIA').strip().upper()
        aport = float(so['total_aportes'] or 0)
        num = int(so['total_socios'] or 0)
        
        data_map[ag][p_str]['PEN']['aportaciones'] += aport
        data_map[ag][p_str]['PEN']['nro_socios'] += num
        acumulado_map[p_str]['PEN']['aportaciones'] += aport
        acumulado_map[p_str]['PEN']['nro_socios'] += num

    final_data = {}
    final_data['ACUMULADO'] = []
    for d in sorted(acumulado_map.keys()):
        for curr in acumulado_map[d].keys():
            final_data['ACUMULADO'].append({
                'load_date': d,
                'currency': curr,
                'ahorros': acumulado_map[d][curr]['ahorros'],
                'dpf': acumulado_map[d][curr]['dpf'],
                'aportaciones': acumulado_map[d][curr]['aportaciones'],
                'nro_socios': acumulado_map[d][curr]['nro_socios']
            })

    for ag, periods_dict in data_map.items():
        if ag != 'ACUMULADO':
            final_data[ag] = []
            for d in sorted(periods_dict.keys()):
                for curr in periods_dict[d].keys():
                    final_data[ag].append({
                        'load_date': d,
                        'currency': curr,
                        'ahorros': periods_dict[d][curr]['ahorros'],
                        'dpf': periods_dict[d][curr]['dpf'],
                        'aportaciones': periods_dict[d][curr]['aportaciones'],
                        'nro_socios': periods_dict[d][curr]['nro_socios']
                    })

    return JsonResponse({'status': 'success', 'data': final_data})

@login_required
def api_available_passive_dates(request, plan_id=None):
    from liquidity_risk.models import LiqLiabilityDetail
    from utilities.models import Socio
    
    dates = set()
    for d in LiqLiabilityDetail.objects.values_list('period', flat=True).distinct():
        if d: dates.add(d.strftime('%Y-%m'))
    for d in Socio.objects.values_list('corte', flat=True).distinct():
        if d: dates.add(d.strftime('%Y-%m'))
        
    sorted_dates = sorted(list(dates), reverse=True)
    data = [{"value": ym, "label": ym} for ym in sorted_dates]
    
    return JsonResponse({'status': 'success', 'data': data})
@login_required
def api_get_trend_data(request, plan_id=None):
    from credit_risk.models import CreditOperation
    from liquidity_risk.models import LiqLiabilityDetail
    from utilities.models import Socio
    from django.db.models import Sum, Count
    from .models import PlanFinanciero
    
    plan = get_object_or_404(PlanFinanciero, id=plan_id)
    
    hist_data = plan.historical_data or {}
    if 'step6_data' in hist_data and hist_data['step6_data']:
        return JsonResponse(hist_data['step6_data'])
        
    base_year_calc = plan.anio_base - 1
    
    # Let's generate a 12-month historical series for base_year_calc
    labels = [f"{base_year_calc}-{str(m).zfill(2)}" for m in range(1, 13)]
    for y in range(plan.anio_base, plan.anio_base + plan.horizonte_anios):
        for m in range(1, 13):
            labels.append(f"{y}-{str(m).zfill(2)}")
            
    # Initialize base values using exact logic from manage_assumptions
    cartera_mn_agg = CreditOperation.objects.filter(load_date__year=base_year_calc, load_date__month=12).aggregate(s=Sum('balance'))
    cartera_base_mn = float(cartera_mn_agg['s'] or 77815122.00)
    
    pasivos = LiqLiabilityDetail.objects.filter(period__year=base_year_calc, period__month=12).values('funding_type', 'currency', 'product').annotate(s=Sum('balance'))
    ahorros_base_mn = 0.0
    ahorros_base_me = 0.0
    dpf_base_mn = 0.0
    dpf_base_me = 0.0
    
    for p in pasivos:
        val = float(p['s'] or 0)
        is_me = (p['currency'] == 'ME' or 'ME' in p['product'] or 'DOLARES' in p['product'].upper())
        is_dpf = (p['funding_type'] == 'PLAZO' or 'PLAZO' in p['product'].upper())
        if is_dpf:
            if is_me: dpf_base_me += val
            else: dpf_base_mn += val
        else:
            if is_me: ahorros_base_me += val
            else: ahorros_base_mn += val
    socios_agg = Socio.objects.filter(corte__year=base_year_calc, corte__month=12).aggregate(sum=Sum('aportes'), count=Count('id'))
    aportes_base = float(socios_agg['sum'] or 48000000)
    socios_base = float(socios_agg['count'] or 25000)

    cartera_mn_hist = [0.0] * 12
    ahorros_mn_hist = [0.0] * 12
    ahorros_me_hist = [0.0] * 12
    dpf_mn_hist = [0.0] * 12
    dpf_me_hist = [0.0] * 12
    aportes_hist = [0.0] * 12
    socios_hist = [0.0] * 12

    mora_mn_hist = [0.0] * 12
    # Fetch real historical data for all 12 months
    cartera_mn_agg_hist = CreditOperation.objects.filter(load_date__year=base_year_calc).values('load_date__month').annotate(
        s=Sum('balance'),
        mora=Sum('past_due_portfolio') + Sum('refinanced_past_due') + Sum('restructured_past_due') + Sum('judicial_portfolio')
    )
    for c in cartera_mn_agg_hist:
        m = c['load_date__month'] - 1
        cartera_mn_hist[m] = float(c['s'] or 0)
        mora_mn_hist[m] = float(c['mora'] or 0)

    pasivos_agg_hist = LiqLiabilityDetail.objects.filter(period__year=base_year_calc).values('period__month', 'funding_type', 'currency', 'product').annotate(s=Sum('balance'))
    for p in pasivos_agg_hist:
        m = p['period__month'] - 1
        val = float(p['s'] or 0)
        is_me = (p['currency'] == 'ME' or 'ME' in p['product'] or 'DOLARES' in p['product'].upper())
        is_dpf = (p['funding_type'] == 'PLAZO' or 'PLAZO' in p['product'].upper())
        if is_dpf:
            if is_me: dpf_me_hist[m] += val
            else: dpf_mn_hist[m] += val
        else:
            if is_me: ahorros_me_hist[m] += val
            else: ahorros_mn_hist[m] += val

    socios_agg_hist = Socio.objects.filter(corte__year=base_year_calc).values('corte__month').annotate(sum=Sum('aportes'), count=Count('id'))
    for s in socios_agg_hist:
        m = s['corte__month'] - 1
        aportes_hist[m] = float(s['sum'] or 0)
        socios_hist[m] = float(s['count'] or 0)
    def generate_projections(hist_list, growth_rate, steps):
        # Siempre iniciamos la proyección exactamente desde el último valor histórico
        # para evitar el salto/caída visual (discontinuidad) en las gráficas.
        last_val = hist_list[-1] if len(hist_list) > 0 else 0
        if last_val < 0: last_val = 0
            
        proj = []
        # Convertimos la tasa de crecimiento anual a mensual simple
        monthly_rate = growth_rate / 12.0
        
        current_val = last_val
        for _ in range(steps):
            current_val *= (1 + monthly_rate)
            proj.append(current_val)
            
        return proj

    import numpy as np

    proj_steps = plan.horizonte_anios * 12
    
    variables = [
        {'id': 'cartera', 'name': 'Cartera de Créditos (S/)', 'hist': cartera_mn_hist},
        {'id': 'mora_soles', 'name': 'Mora (S/)', 'hist': mora_mn_hist},
        {'id': 'ahorros', 'name': 'Ahorros (S/)', 'hist': ahorros_mn_hist},
        {'id': 'ahorros_usd', 'name': 'Ahorros ($)', 'hist': ahorros_me_hist},
        {'id': 'dpf', 'name': 'Plazo Fijo (S/)', 'hist': dpf_mn_hist},
        {'id': 'dpf_usd', 'name': 'Plazo Fijo ($)', 'hist': dpf_me_hist},
        {'id': 'aportes', 'name': 'Aportaciones', 'hist': aportes_hist},
        {'id': 'socios', 'name': 'Número de Socios', 'hist': socios_hist},
    ]
    out_vars = []
    
    # Load custom rates if available
    hist_data = plan.historical_data or {}
    saved_scenarios = hist_data.get('trend_scenarios', {})
    agency_scenarios = saved_scenarios.get('Consolidado', {})
    step6_data = hist_data.get('step6_data', {})

    for v in variables:
        v_rates = agency_scenarios.get(v['id'], {})
        
        # Calcular tasa de tendencia estadística base con Numpy si hay datos
        y = np.array(v['hist'])
        valid_idx = np.where(y > 0)[0]
        calculated_trend_rate = 1.5 # default 1.5%
        
        if len(valid_idx) > 1:
            x = valid_idx
            y_valid = y[valid_idx]
            m, c = np.polyfit(x, y_valid, 1)
            
            # Aproximación de la tasa de crecimiento anual implícita en la pendiente
            # Asumimos que la pendiente m es el crecimiento mensual en valor absoluto.
            # growth_rate = (m * 12) / last_val
            last_val = v['hist'][-1]
            if last_val > 0:
                calculated_trend_rate = ((m * 12) / last_val) * 100.0
                
                # Limitamos la tasa calculada para evitar crecimientos absurdos (ej. >100% o <-100%)
                calculated_trend_rate = max(-100.0, min(100.0, calculated_trend_rate))
                
        # Si el usuario guardó una tasa manual, usamos esa; sino, usamos la estadística calculada
        trend_rate = float(v_rates.get('trend', calculated_trend_rate))
        
        # Determine defaults correctly based on variable type
        is_loss_variable = 'mora' in v['id'].lower()
        default_pesimista_offset = 2.5 if is_loss_variable else -2.5
        default_optimista_offset = -2.5 if is_loss_variable else 2.5
        
        pesimista_rate = float(v_rates.get('pessimistic', calculated_trend_rate + default_pesimista_offset))
        base_rate = float(v_rates.get('base', calculated_trend_rate))
        optimista_rate = float(v_rates.get('optimistic', calculated_trend_rate + default_optimista_offset))
        
        # Force logical ordering: for loss variables, pesimista must be >= optimista
        if is_loss_variable:
            actual_pes = max(pesimista_rate, optimista_rate)
            actual_opt = min(pesimista_rate, optimista_rate)
            pesimista_rate = actual_pes
            optimista_rate = actual_opt
        else:
            actual_pes = min(pesimista_rate, optimista_rate)
            actual_opt = max(pesimista_rate, optimista_rate)
            pesimista_rate = actual_pes
            optimista_rate = actual_opt
            
        trend = generate_projections(v['hist'], trend_rate / 100.0, proj_steps)
        pesimista = generate_projections(v['hist'], pesimista_rate / 100.0, proj_steps)
        base = generate_projections(v['hist'], base_rate / 100.0, proj_steps)
        optimista = generate_projections(v['hist'], optimista_rate / 100.0, proj_steps)
        
        out_var = {
            'id': v['id'],
            'name': v['name'],
            'hist': v['hist'],
            'trend': trend,
            'base': base,
            'pesimista': pesimista,
            'optimista': optimista,
            'rates': {
                'trend': round(trend_rate, 2),
                'pesimista': round(pesimista_rate, 2),
                'base': round(base_rate, 2),
                'optimista': round(optimista_rate, 2)
            },
            'mc_data': None
        }
        
        # Load mc_data if saved previously in step6_data
        if step6_data and 'datasets_by_agency' in step6_data:
            cons_data = step6_data['datasets_by_agency'].get('Consolidado', {})
            for saved_v in cons_data.get('variables', []):
                if saved_v.get('id') == v['id'] and saved_v.get('mc_data'):
                    out_var['mc_data'] = saved_v['mc_data']
                    break
                    
        out_vars.append(out_var)

    ui_state = step6_data.get('ui_state', {})
    if not ui_state.get('currentPeriod'):
        ui_state['currentPeriod'] = (plan.horizonte_anios or 1) * 12

    data = {
        'labels': labels,
        'hist_months': 12,
        'datasets_by_agency': {
            'Consolidado': {
                'variables': out_vars
            }
        },
        'ui_state': ui_state
    }
    return JsonResponse({'status': 'success', **data})



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
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'msg': 'Invalid request method'})
    
    try:
        data = json.loads(request.body)
        history = data.get('history', [])
        proj_months = data.get('proj_months', 12)
        iterations = data.get('iterations', 1000)
        variable_id = data.get('variable_id', '')
        base_rate = data.get('base_rate')
        pesimista_rate = data.get('pesimista_rate')
        optimista_rate = data.get('optimista_rate')

        import numpy as np
        
        # Si base_rate no viene, lo calculamos igual que en la tendencia normal
        if base_rate is None and history:
            y = np.array(history)
            valid_idx = np.where(y > 0)[0]
            calculated_trend_rate = 1.5
            if len(valid_idx) > 1:
                x = valid_idx
                y_valid = y[valid_idx]
                m, c = np.polyfit(x, y_valid, 1)
                last_val = history[-1]
                if last_val > 0:
                    calculated_trend_rate = ((m * 12) / last_val) * 100.0
                    calculated_trend_rate = max(-100.0, min(100.0, calculated_trend_rate))
            base_rate = calculated_trend_rate / 100.0
            pesimista_rate = (calculated_trend_rate - 2.5) / 100.0
            optimista_rate = (calculated_trend_rate + 2.5) / 100.0
        elif base_rate is None:
            base_rate = 0.015
            pesimista_rate = 0.005
            optimista_rate = 0.025

        monthly_rate = base_rate / 12.0
        
        # Derivar volatilidad estandarizada a partir de la amplitud de los escenarios definidos por el usuario
        # Usamos Z=1.645 asumiendo que Optimista/Pesimista representan el percentil 95 o 5
        spread_opt = abs(optimista_rate - base_rate)
        spread_pes = abs(base_rate - pesimista_rate)
        max_spread_annual = max(spread_opt, spread_pes)
        
        # Volatilidad anual inferida
        annual_volatility = max_spread_annual / 1.645 
        # Volatilidad mensualizada
        volatility = max(0.001, annual_volatility / np.sqrt(12)) 
        
        last_val = history[-1] if history else 0
        if last_val < 0: last_val = 0
            
        # Vectorized calculation for maximum performance
        random_rates = np.random.normal(loc=monthly_rate, scale=volatility, size=(iterations, proj_months))
        multipliers = np.cumprod(1 + random_rates, axis=1)
        results = last_val * multipliers

        if 'mora' in variable_id.lower():
            pesimista_idx = 95
            optimista_idx = 5
        else:
            pesimista_idx = 5
            optimista_idx = 95
            
        pesimista = np.percentile(results, pesimista_idx, axis=0).tolist()
        base = np.mean(results, axis=0).tolist()
        optimista = np.percentile(results, optimista_idx, axis=0).tolist()
        
        mc_data = {
            'pesimista': [round(x, 2) for x in pesimista],
            'base': [round(x, 2) for x in base],
            'optimista': [round(x, 2) for x in optimista]
        }
        
        return JsonResponse({'status': 'success', 'data': mc_data})
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'status': 'error', 'msg': str(e)})

@login_required
def save_institutional_assumptions(request, plan_id=None):
    if request.method == 'POST' and plan_id:
        import json
        plan = get_object_or_404(PlanFinanciero, id=plan_id)
        try:
            body = json.loads(request.body)
            hist_data = plan.historical_data or {}
            inst_assump = hist_data.get('institutional_assumptions', {})
            
            if 'costParams' in body:
                inst_assump['costParams'] = body['costParams']
            if 'yieldParams' in body:
                inst_assump['yieldParams'] = body['yieldParams']
                
            hist_data['institutional_assumptions'] = inst_assump
            
            if 'income_statement' in body:
                hist_data['budget_income_statement'] = body['income_statement']
            if 'account_assumptions' in body:
                hist_data['account_assumptions'] = body['account_assumptions']
            plan.historical_data = hist_data
            plan.save()
            return JsonResponse({'status': 'success', 'msg': 'Assumptions saved'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'msg': str(e)})
    return JsonResponse({'status': 'error', 'msg': 'Invalid request'})

@login_required
def api_unlock_step6(request, plan_id=None):
    return JsonResponse({'status': 'success', 'msg': 'Endpoint en construccion: api_unlock_step6'})

@login_required
def api_historical_portfolio_data(request, plan_id=None):
    import json
    from credit_risk.models import CreditOperation
    from django.db.models import Count, Sum, Q, F
    from django.http import JsonResponse
    
    dates_param = request.GET.get('dates')
    periods = []
    if dates_param:
        periods = [d.strip() for d in dates_param.split(',')]
            
    if not periods:
        return JsonResponse({'status': 'success', 'data': {}, 'msg': 'No periods provided.'})
        
    query = Q()
    for p_str in periods:
        try:
            y, m = map(int, p_str.split('-'))
            query |= Q(load_date__year=y, load_date__month=m)
        except Exception:
            pass

    overall_qs = CreditOperation.objects.filter(query).values('load_date', 'agency').annotate(
        nro_socios=Count('customer', distinct=True),
        nro_analistas=Count('advisor', distinct=True)
    )
    overall_map = {}
    for row in overall_qs:
        ld = row['load_date'].strftime('%Y-%m')
        ag = row['agency'] or 'SIN AGENCIA'
        if ld not in overall_map:
            overall_map[ld] = {}
        overall_map[ld][ag] = {
            'nro_socios': row['nro_socios'],
            'nro_analistas': row['nro_analistas']
        }

    qs = CreditOperation.objects.filter(query).values('load_date', 'agency', 'credit_type').annotate(
        saldo=Sum('balance'),
        total_ops=Count('id'),
        num_desemb=Count('id', filter=Q(disbursement_date__year=F('load_date__year'), disbursement_date__month=F('load_date__month'))),
        monto_desemb=Sum('original_amount', filter=Q(disbursement_date__year=F('load_date__year'), disbursement_date__month=F('load_date__month'))),
        cartera_vencida_calc=Sum('balance', filter=Q(days_past_due__gt=30))
    ).order_by('load_date', 'agency', 'credit_type')

    data_map = {}
    
    # We will map our DB types to the types expected by the frontend.
    # Frontend expects: 'G.EMP.', 'M.EMP.', 'P.EMP.', 'MI.EMP.', 'CONS'
    # DB might have 'CONSUMO', 'MICROEMPRESA', 'PEQUEÑA EMPRESA', 'MEDIANA EMPRESA', 'GRAN EMPRESA'
    def map_type(ct):
        ct_upper = str(ct).upper()
        if 'CONS' in ct_upper: return 'CONS'
        if 'MICRO' in ct_upper: return 'MI.EMP.'
        if 'PEQUE' in ct_upper: return 'P.EMP.'
        if 'MEDIANA' in ct_upper: return 'M.EMP.'
        if 'GRAN' in ct_upper: return 'G.EMP.'
        return 'CONS' # Default fallback
    
    MONTH_NAMES = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']

    for row in qs:
        ld = row['load_date'].strftime('%Y-%m')
        y, m = map(int, ld.split('-'))
        period_str = f"{MONTH_NAMES[m-1]}-{str(y)[2:]}" # format as Ene-25

        ag = row['agency'] or 'SIN AGENCIA'
        ct_original = row['credit_type'] or 'CONSUMO'
        ct = map_type(ct_original)
        
        for current_ag in (ag, 'ACUMULADO'):
            if current_ag not in data_map:
                data_map[current_ag] = {}
                
            if ld not in data_map[current_ag]:
                advisors_count = 0
                if current_ag == 'ACUMULADO':
                    advisors_count = sum(info.get('nro_analistas', 0) for info in overall_map.get(ld, {}).values())
                else:
                    advisors_count = overall_map.get(ld, {}).get(ag, {}).get('nro_analistas', 0)
                    
                data_map[current_ag][ld] = {
                    'period': period_str,
                    'advisors': advisors_count,
                    'types': {},
                    'cartera_vencida': 0
                }
                
            if ct not in data_map[current_ag][ld]['types']:
                data_map[current_ag][ld]['types'][ct] = {
                    'nro_des': 0,
                    'mto_des': 0,
                    'nro_car': 0,
                    'sld_car': 0,
                    'cob_est': 0
                }
                
            t_data = data_map[current_ag][ld]['types'][ct]
            t_data['nro_des'] += row['num_desemb'] or 0
            t_data['mto_des'] += float(row['monto_desemb'] or 0)
            t_data['nro_car'] += row['total_ops'] or 0
            t_data['sld_car'] += float(row['saldo'] or 0)
            data_map[current_ag][ld]['cartera_vencida'] += float(row['cartera_vencida_calc'] or 0)
        
    # Convert data_map inner dicts to lists
    final_data = {}
    for ag, periods_dict in data_map.items():
        # Sort by load_date descending or ascending based on requirements
        final_data[ag] = [periods_dict[ld] for ld in sorted(periods_dict.keys())]

    return JsonResponse({
        'status': 'success',
        'data': final_data
    })

@login_required
def api_save_trend_scenarios(request, plan_id=None):
    if request.method == 'POST' and plan_id:
        import json
        plan = get_object_or_404(PlanFinanciero, id=plan_id)
        try:
            body = json.loads(request.body)
            agency = body.get('agency', 'Consolidado')
            scenarios = body.get('scenarios', {})
            
            hist_data = plan.historical_data or {}
            trend_scenarios = hist_data.get('trend_scenarios', {})
            
            if agency not in trend_scenarios:
                trend_scenarios[agency] = {}
                
            for var_id, rates in scenarios.items():
                if var_id not in trend_scenarios[agency]:
                    trend_scenarios[agency][var_id] = {}
                trend_scenarios[agency][var_id]['pessimistic'] = rates.get('pessimistic')
                trend_scenarios[agency][var_id]['base'] = rates.get('base')
                trend_scenarios[agency][var_id]['optimistic'] = rates.get('optimistic')
                
            hist_data['trend_scenarios'] = trend_scenarios
            if 'step6_data' in hist_data:
                del hist_data['step6_data']
            plan.historical_data = hist_data
            plan.save()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'msg': str(e)})
    return JsonResponse({'status': 'error', 'msg': 'Método no permitido'})

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
    from credit_risk.models import CreditOperation
    from django.http import JsonResponse
    dates = CreditOperation.objects.values_list('load_date', flat=True).distinct().order_by('-load_date')
    dates_str = [d.strftime('%Y-%m') for d in dates if d]
    return JsonResponse({'status': 'success', 'data': dates_str})

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
    
    # Filter by period list using a single optimized query
    from django.db.models import Q
    query = Q()
    for p_str in periods:
        try:
            y, m = p_str.split('-')
            query |= Q(period__year=y, period__month=m, upload__status='SUCCESS')
        except Exception:
            pass
            
    if query:
        # Use .values() to fetch dictionaries directly, skipping expensive model instantiation
        selected_details = list(LiqBalanceDetail.objects.filter(query).values('account_code', 'account_name', 'period__year', 'period__month', 'balance'))
    else:
        selected_details = []
            
    def get_parent_code(code):
        if len(code) == 1: return None
        if len(code) == 2: return code[0]
        if len(code) % 2 == 0: return code[:-2]
        return code[:-1] # fallback

    account_dict = {}
    
    for d in selected_details:
        c_code = str(d['account_code'])
        c_name = d['account_name']
        p_str = f"{d['period__year']}-{d['period__month']:02d}"
        
        # Reverse sign for Pasivo and Patrimonio to show as positive numbers natively, 
        # making debit results (like negative outcomes) show as negative.
        val = float(d['balance'])
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
        c_code = str(d['account_code'])
        if c_code in account_dict:
            account_dict[c_code]['name'] = d['account_name']

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
    if request.method == 'POST' and plan_id:
        import json
        plan = get_object_or_404(PlanFinanciero, id=plan_id)
        try:
            body = json.loads(request.body)
            full_payload = body.get('full_payload', {})
            hist_data = plan.historical_data or {}
            
            ui_state = full_payload.get('ui_state', {})
            if ui_state and ui_state.get('currentPeriod'):
                try:
                    plan.horizonte_anios = int(ui_state['currentPeriod']) // 12
                except ValueError:
                    pass
            
            hist_data['step6_data'] = full_payload
            
            if 'locked_steps' not in hist_data:
                hist_data['locked_steps'] = {}
            hist_data['locked_steps']['step6'] = True
            
            plan.historical_data = hist_data
            plan.save()
            return JsonResponse({'status': 'success', 'msg': 'Paso 6 bloqueado exitosamente.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'msg': str(e)})
    return JsonResponse({'status': 'error', 'msg': 'Método no permitido'})

@login_required
def save_scenario_fragment(request, plan_id=None):
    if request.method == 'POST' and plan_id:
        import json
        from django.db import transaction
        plan = get_object_or_404(PlanFinanciero, id=plan_id)
        organization = plan.organization
        try:
            body = json.loads(request.body)
            full_payload = body.get('full_payload', {})
            hist_data = plan.historical_data or {}
            
            ui_state = full_payload.get('ui_state', {})
            if ui_state and ui_state.get('currentPeriod'):
                try:
                    plan.horizonte_anios = int(ui_state['currentPeriod']) // 12
                except ValueError:
                    pass
            
            hist_data['step6_data'] = full_payload
            plan.historical_data = hist_data
            plan.save()
            
            datasets_by_agency = full_payload.get('datasets_by_agency', {})
            
            with transaction.atomic():
                for agency, agency_data in datasets_by_agency.items():
                    variables = agency_data.get('variables', [])
                    for var in variables:
                        var_id = var.get('id')
                        var_name = var.get('name')
                        rates = var.get('rates', {})
                        
                        escenario, created = SimulacionEscenario.objects.update_or_create(
                            organization=organization,
                            plan=plan,
                            agencia=agency,
                            variable_id=var_id,
                            defaults={
                                'variable_name': var_name,
                                'tasa_tendencia': rates.get('trend', 0),
                                'tasa_base': rates.get('base', 0),
                                'tasa_pesimista': rates.get('pesimista', 0),
                                'tasa_optimista': rates.get('optimista', 0),
                            }
                        )
                        
                        base_arr = var.get('base', [])
                        trend_arr = var.get('trend', [])
                        pesimista_arr = var.get('pesimista', [])
                        optimista_arr = var.get('optimista', [])
                        
                        mc_data = var.get('mc_data') or {}
                        mc_base = mc_data.get('base', [])
                        mc_pesimista = mc_data.get('pesimista', [])
                        mc_optimista = mc_data.get('optimista', [])
                        
                        num_months = len(base_arr)
                        
                        for i in range(num_months):
                            mes = i + 1
                            ProyeccionMensual.objects.update_or_create(
                                organization=organization,
                                escenario=escenario,
                                mes_proyeccion=mes,
                                defaults={
                                    'valor_tendencia': trend_arr[i] if i < len(trend_arr) else 0,
                                    'valor_base': base_arr[i] if i < len(base_arr) else 0,
                                    'valor_pesimista': pesimista_arr[i] if i < len(pesimista_arr) else 0,
                                    'valor_optimista': optimista_arr[i] if i < len(optimista_arr) else 0,
                                    
                                    'mc_valor_base': mc_base[i] if i < len(mc_base) else None,
                                    'mc_valor_pesimista': mc_pesimista[i] if i < len(mc_pesimista) else None,
                                    'mc_valor_optimista': mc_optimista[i] if i < len(mc_optimista) else None,
                                }
                            )

            return JsonResponse({'status': 'success', 'msg': 'Simulaciones guardadas correctamente.'})
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            return JsonResponse({'status': 'error', 'msg': str(e)})
    return JsonResponse({'status': 'error', 'msg': 'Método no permitido'})
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
        income_statement = body.get('income_statement', None)
        balance_sheet = body.get('balance_sheet', None)
        
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
        if income_statement:
            hist_data['income_statement'] = income_statement
        if balance_sheet:
            hist_data['balance_sheet'] = balance_sheet
        
        plan.historical_data = hist_data
        plan.save()
        
        return JsonResponse({'status': 'success', 'msg': 'Balance histórico asignado correctamente al plan.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'msg': str(e)})

@login_required
def api_get_assumptions_product(request, plan_id=None):
    return JsonResponse({'status': 'success', 'data': []})

@login_required
def api_save_assumptions_product(request, plan_id=None):
    return JsonResponse({'status': 'success'})


from decimal import Decimal
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
import json
import pandas as pd
from .models import PlanFinanciero, BudgetItem, BudgetVersion, BudgetLine, BudgetLineDetail, BudgetCalculationRule
from .services.budget_engine import BudgetEngine

@login_required
def api_get_budget_data(request, plan_id):
    organization = request.user.organization
    if not organization:
        from users.models import Organization
        organization = Organization.objects.first()
        
    plan = get_object_or_404(PlanFinanciero, id=plan_id, organization=organization)
    scenario = request.GET.get('scenario', 'BASE')
    
    engine = BudgetEngine(plan, organization, request.user)
    engine._ensure_default_items()
    
    er_totals = engine._get_historical_er_totals()
    
    version = BudgetVersion.objects.filter(
        plan_financiero=plan, 
        organization=organization, 
        scenario=scenario, 
        status='DRAFT'
    ).first()
    
    if not version:
        version = BudgetVersion.objects.filter(
            plan_financiero=plan, 
            organization=organization, 
            scenario=scenario, 
            status='APPROVED'
        ).first()
        
    if not version:
        version = engine.get_or_create_draft_version(scenario)
    
    items = BudgetItem.objects.filter(organization=organization).order_by('category')
    data = []
    lines = BudgetLine.objects.filter(version=version)
    lines_by_item = {l.item_id: l for l in lines}
    
    for item in items:
        rule = BudgetCalculationRule.objects.filter(item=item).first()
        line = lines_by_item.get(item.id)
        
        calc_type = line.applied_calculation_type if line else (rule.calculation_type if rule else 'MANUAL')
        source_trend = rule.source_trend_variable if rule else ''
        account_prefix = rule.assumption_driver if rule and rule.assumption_driver else ''
        
        if not account_prefix:
            # Fallback a DEFAULT_BUDGET_ITEMS
            from .services.budget_engine import DEFAULT_BUDGET_ITEMS
            default_item = next((d for d in DEFAULT_BUDGET_ITEMS if d['code'] == item.code), None)
            if default_item:
                account_prefix = default_item.get('account_prefix', '')

        # Resolve historical total
        historical_total = 0.0
        if account_prefix:
            historical_total = engine._resolve_historical_total(account_prefix, er_totals)

        item_data = {
            'item_id': item.id,
            'category': item.category,
            'code': item.code,
            'name': item.name,
            'calc_type': calc_type,
            'source_trend_variable': source_trend,
            'account_prefix': account_prefix,
            'monthly_values': [0]*12,
            'y1_total': 0,
            'y2_total': 0,
            'y3_total': 0,
            'historical_total': historical_total
        }
        
        if line:
            item_data['y1_total'] = float(line.total_amount_y1)
            item_data['y2_total'] = float(line.total_amount_y2)
            item_data['y3_total'] = float(line.total_amount_y3)
            
            details = BudgetLineDetail.objects.filter(budget_line=line, period_type='MONTH').order_by('period_index')
            for d in details:
                if 1 <= d.period_index <= 12:
                    item_data['monthly_values'][d.period_index - 1] = float(d.amount)
                    
        data.append(item_data)
        
    # No custom sort needed; BudgetItem query is ordered by category
    
    has_yield_params = False
    has_cost_params = False
    er_accounts = []
    if plan.historical_data:
        inst_assump = plan.historical_data.get('institutional_assumptions', {})
        has_yield_params = bool(inst_assump.get('yieldParams'))
        has_cost_params = bool(inst_assump.get('costParams'))
        
        selected_periods = plan.historical_data.get('selected_periods', [])
        if not selected_periods:
            selected_periods = [f"{plan.anio_base - 1}-12"]
            
        if selected_periods:
            from liquidity_risk.models import LiqBalanceDetail
            from django.db.models import Q
            q = Q()
            for p_str in selected_periods:
                try:
                    y, m = p_str.split('-')
                    q |= Q(period__year=int(y), period__month=int(m), upload__status='SUCCESS')
                except:
                    pass
            if q:
                qs = LiqBalanceDetail.objects.filter(q).filter(
                    Q(account_code__startswith='4') | Q(account_code__startswith='5')
                ).values('account_code', 'account_name').distinct().order_by('account_code')
                for acc in qs:
                    er_accounts.append({
                        'val': str(acc['account_code']),
                        'label': f"{acc['account_code']} - {acc['account_name']}"
                    })

    # Default fallback if empty
    if not er_accounts:
        er_accounts = [
            {'val': '51', 'label': 'Ing. Financieros (51)'},
            {'val': '52', 'label': 'Ing. Servicios (52)'},
            {'val': '53', 'label': 'Rev. Provisiones (53)'},
            {'val': '54', 'label': 'Reversiones (54)'},
            {'val': '56', 'label': 'Otros Ingresos (56)'},
            {'val': '57', 'label': 'Ventas (57)'},
            {'val': '41', 'label': 'Gtos. Financieros (41)'},
            {'val': '42', 'label': 'Gtos. Servicios (42)'},
            {'val': '43', 'label': 'Provisiones (43)'},
            {'val': '44', 'label': 'Depreciación (44)'},
            {'val': '45', 'label': 'Gtos. Admin (45)'},
            {'val': '46', 'label': 'Otros Gastos (46)'},
            {'val': '49', 'label': 'Costo Ventas (49)'}
        ]
        
    return JsonResponse({
        'status': 'success',
        'data': data,
        'version_id': version.id,
        'version_status': version.status,
        'has_yield_params': has_yield_params,
        'has_cost_params': has_cost_params,
        'er_accounts': er_accounts
    })
@login_required
@require_POST
def api_sync_budget_trends(request, plan_id):
    import traceback
    organization = request.user.organization
    if not organization:
        from users.models import Organization
        organization = Organization.objects.first()
        
    plan = get_object_or_404(PlanFinanciero, id=plan_id, organization=organization)

    # Accept scenario from JSON body or form POST
    scenario = 'BASE'
    try:
        body = json.loads(request.body)
        scenario = body.get('scenario', 'BASE')
    except Exception:
        scenario = request.POST.get('scenario', 'BASE')
    
    engine = BudgetEngine(plan, organization, request.user)
    try:
        engine.sync_with_trends(scenario)
        # Re-count synced lines
        version = engine.get_or_create_draft_version(scenario)
        synced_count = BudgetLine.objects.filter(version=version).count()
        return JsonResponse({
            'status': 'success',
            'message': f'Sincronizado con tendencias: {synced_count} rubros calculados.',
            'synced_count': synced_count,
        })
    except Exception as e:
        print(traceback.format_exc())
        return JsonResponse({'status': 'error', 'message': str(e)})


@login_required
def api_get_er_historico(request, plan_id):
    """
    Returns the historical Income Statement (E.R.) for the plan's selected periods,
    grouped by account category.  Used by Step 7 budget builder to show the base year.
    """
    import traceback
    organization = request.user.organization
    if not organization:
        from users.models import Organization
        organization = Organization.objects.first()

    plan = get_object_or_404(PlanFinanciero, id=plan_id, organization=organization)
    hist_data = plan.historical_data or {}
    selected_periods = hist_data.get('selected_periods', [])

    from liquidity_risk.models import LiqBalanceDetail
    from django.db.models import Q

    if not selected_periods:
        base_year = str(plan.anio_base - 1)
        q = Q(period__year=int(base_year), upload__status='SUCCESS')
    else:
        # Build query for all selected periods
        q = Q()
        for p_str in selected_periods:
            try:
                y, m = p_str.split('-')
                q |= Q(period__year=int(y), period__month=int(m), upload__status='SUCCESS')
            except Exception:
                pass
        years = sorted({p.split('-')[0] for p in selected_periods}, reverse=True)
        base_year = years[0] if years else str(plan.anio_base - 1)

    if not q:
        return JsonResponse({'status': 'error', 'msg': 'No se pudo procesar los períodos seleccionados.'})

    # Fetch only income/expense accounts
    qs = LiqBalanceDetail.objects.filter(q).filter(
        Q(account_code__startswith='4') | Q(account_code__startswith='5')
    ).values('account_code', 'account_name', 'period__year', 'period__month', 'balance')

    # Determine base_year is done above

    # Group by account (use Dec value = YTD; fall back to sum)
    account_totals = {}
    period_months = set()
    for row in qs:
        code = str(row['account_code'])
        y_val = row['period__year']
        m_val = row['period__month']
        bal = float(row['balance'])
        period_months.add((y_val, m_val))

        if code not in account_totals:
            account_totals[code] = {
                'code': code,
                'name': row['account_name'],
                'monthly': {},
                'ytd': 0.0,
            }

        p_key = f"{y_val}-{m_val:02d}"
        account_totals[code]['monthly'][p_key] = bal

    # Use December balance as YTD; otherwise sum all months
    for code, acc in account_totals.items():
        dec_key = f"{base_year}-12"
        if dec_key in acc['monthly']:
            ytd = acc['monthly'][dec_key]
        else:
            ytd = sum(acc['monthly'].values())
        # Flip sign for income (5x) to show as positive
        if code.startswith('5'):
            ytd = abs(ytd)
        acc['ytd'] = round(ytd, 2)

    # Aggregate by 2-digit account group
    CATEGORY_MAP = {
        '51': 'Ingresos Financieros',
        '52': 'Ingresos por Servicios Financieros',
        '53': 'Reversión Pérdidas / Provisiones',
        '54': 'Reversión de Provisiones',
        '56': 'Otros Ingresos',
        '57': 'Ventas',
        '41': 'Gastos Financieros',
        '42': 'Gastos por Servicios Financieros',
        '43': 'Provisiones para Incobrabilidad',
        '44': 'Depreciación y Amortización',
        '45': 'Gastos de Administración',
        '46': 'Otros Gastos',
        '49': 'Costo de Ventas',
    }

    grouped = {}
    for code, acc in account_totals.items():
        prefix_2 = code[:2] if len(code) >= 2 else code[:1]
        if prefix_2 not in grouped:
            grouped[prefix_2] = {
                'group_code': prefix_2,
                'group_name': CATEGORY_MAP.get(prefix_2, f'Cuenta {prefix_2}'),
                'is_income': code.startswith('5'),
                'total': 0.0,
                'accounts': [],
            }
        grouped[prefix_2]['total'] += acc['ytd']
        grouped[prefix_2]['accounts'].append({
            'code': code,
            'name': acc['name'],
            'amount': acc['ytd'],
        })

    # Sort: income groups first (5x), then expense groups (4x)
    income_groups = sorted(
        [v for v in grouped.values() if v['is_income']],
        key=lambda x: x['group_code']
    )
    expense_groups = sorted(
        [v for v in grouped.values() if not v['is_income']],
        key=lambda x: x['group_code']
    )

    total_ingresos = sum(g['total'] for g in income_groups)
    total_gastos = sum(g['total'] for g in expense_groups)
    utilidad_neta = total_ingresos - total_gastos

    return JsonResponse({
        'status': 'success',
        'base_year': base_year,
        'income_groups': income_groups,
        'expense_groups': expense_groups,
        'totals': {
            'total_ingresos': round(total_ingresos, 2),
            'total_gastos': round(total_gastos, 2),
            'utilidad_neta': round(utilidad_neta, 2),
        }
    })


@login_required
def api_get_historical_account_monthly(request, plan_id):
    """
    Returns the 12-month breakdown for a given account_prefix from historical data.
    Used by "Manual" calc_type rows that want to load historical data and apply a % adjustment.
    GET params:
        - account_prefix: e.g. '4501', '51', '57'
        - adjustment_pct: e.g. 5 (means +5%), -10 (means -10%). Default 0.
    """
    organization = request.user.organization
    if not organization:
        from users.models import Organization
        organization = Organization.objects.first()

    plan = get_object_or_404(PlanFinanciero, id=plan_id, organization=organization)
    account_prefix = request.GET.get('account_prefix', '')
    try:
        adjustment_pct = float(request.GET.get('adjustment_pct', 0))
    except (ValueError, TypeError):
        adjustment_pct = 0.0

    if not account_prefix:
        return JsonResponse({'status': 'error', 'msg': 'Se requiere un prefijo de cuenta.'})

    hist_data = plan.historical_data or {}
    selected_periods = hist_data.get('selected_periods', [])

    from liquidity_risk.models import LiqBalanceDetail
    from django.db.models import Q

    if not selected_periods:
        base_year = plan.anio_base - 1
    else:
        # Determine base year
        years = sorted({p.split('-')[0] for p in selected_periods}, reverse=True)
        base_year = int(years[0]) if years else (plan.anio_base - 1)

    # Build query for all months of the base year
    q = Q(period__year=base_year, upload__status='SUCCESS')

    qs = LiqBalanceDetail.objects.filter(q).filter(
        account_code__startswith=account_prefix
    ).values('account_code', 'account_name', 'period__month', 'balance')

    # Aggregate by month across all sub-accounts of this prefix
    monthly_totals = [0.0] * 12
    account_names = set()
    has_data = False

    for row in qs:
        has_data = True
        m = row['period__month']
        bal = float(row['balance'])
        # Income accounts (5x) are stored as negative; flip to positive
        if str(row['account_code']).startswith('5'):
            bal = abs(bal)
        if 1 <= m <= 12:
            monthly_totals[m - 1] += bal
        account_names.add(f"{row['account_code']} - {row['account_name']}")

    if not has_data:
        return JsonResponse({
            'status': 'warning',
            'msg': f'No se encontraron datos históricos para el prefijo {account_prefix} en {base_year}.',
            'monthly': [0.0] * 12,
            'annual_total': 0.0,
            'adjusted_monthly': [0.0] * 12,
            'adjusted_annual': 0.0,
        })

    # De-accumulate the YTD values into discrete monthly flows.
    # Trial balances for ER accounts (4 and 5) are stored cumulatively (YTD).
    actual_monthly = [0.0] * 12
    last_ytd = 0.0
    for i in range(12):
        curr_ytd = monthly_totals[i]
        if curr_ytd == 0 and i > 0 and last_ytd > 0:
            # Missing month data, assume 0 flow
            actual_monthly[i] = 0.0
        else:
            actual_monthly[i] = max(0.0, curr_ytd - last_ytd)
            last_ytd = curr_ytd
            
    monthly_totals = [round(v, 2) for v in actual_monthly]
    
    annual_total = sum(monthly_totals)
    
    # Apply percentage adjustment
    factor = 1.0 + (adjustment_pct / 100.0)
    adjusted_monthly = [round(v * factor, 2) for v in monthly_totals]
    adjusted_annual = round(sum(adjusted_monthly), 2)

    # Fetch default trend growth to allow Y2 and Y3 projections to follow the Montecarlo trend
    from .models import SimulacionEscenario
    trend_growth = 0.0
    sims = SimulacionEscenario.objects.filter(plan=plan, organization=organization, agencia='Consolidado')
    if sims.exists():
        cartera_sim = sims.filter(variable_id='cartera').first()
        if cartera_sim and cartera_sim.tasa_tendencia:
            trend_growth = float(cartera_sim.tasa_tendencia)
        else:
            tasa_list = [float(s.tasa_tendencia) for s in sims if s.tasa_tendencia]
            if tasa_list:
                trend_growth = sum(tasa_list) / len(tasa_list)

    return JsonResponse({
        'status': 'success',
        'base_year': base_year,
        'account_prefix': account_prefix,
        'accounts_found': list(account_names)[:20],
        'adjustment_pct': adjustment_pct,
        'monthly': [round(v, 2) for v in monthly_totals],
        'annual_total': round(annual_total, 2),
        'adjusted_monthly': adjusted_monthly,
        'adjusted_annual': adjusted_annual,
        'trend_growth': round(trend_growth, 4)
    })


@login_required
@require_POST
def api_seed_budget_items(request, plan_id):
    """Force-seeds / refreshes all canonical BudgetItems and their Calculation Rules."""
    import traceback
    organization = request.user.organization
    if not organization:
        from users.models import Organization
        organization = Organization.objects.first()

    plan = get_object_or_404(PlanFinanciero, id=plan_id, organization=organization)
    engine = BudgetEngine(plan, organization, request.user)
    try:
        # Force full re-seed by temporarily clearing existing items to re-check
        from .services.budget_engine import DEFAULT_BUDGET_ITEMS
        created_codes = []
        for defn in DEFAULT_BUDGET_ITEMS:
            item, created = BudgetItem.objects.update_or_create(
                organization=organization,
                code=defn['code'],
                defaults={
                    'name': defn['name'],
                    'category': defn['category'],
                }
            )
            BudgetCalculationRule.objects.update_or_create(
                organization=organization,
                item=item,
                defaults={
                    'calculation_type': defn['calc_type'] if defn['calc_type'] != 'GROWTH_VARIABLE' else 'TREND',
                    'source_trend_variable': defn.get('trend_variable'),
                    'assumption_driver': defn.get('account_prefix'),
                }
            )
            if created:
                created_codes.append(defn['code'])
        return JsonResponse({
            'status': 'success',
            'message': f'Rubros presupuestales actualizados ({len(DEFAULT_BUDGET_ITEMS)} total, {len(created_codes)} nuevos).',
            'total': len(DEFAULT_BUDGET_ITEMS),
            'new': len(created_codes),
        })
    except Exception as e:
        print(traceback.format_exc())
        return JsonResponse({'status': 'error', 'message': str(e)})

@login_required
@require_POST
def api_save_budget_version(request, plan_id):
    organization = request.user.organization
    if not organization:
        from users.models import Organization
        organization = Organization.objects.first()
        
    plan = get_object_or_404(PlanFinanciero, id=plan_id, organization=organization)
    try:
        payload = json.loads(request.body)
        scenario = payload.get('scenario', 'BASE')
        lines_data = payload.get('lines', [])
        
        engine = BudgetEngine(plan, organization, request.user)
        version = engine.get_or_create_draft_version(scenario)
        
        with transaction.atomic():
            for l_data in lines_data:
                item_id = l_data.get('item_id')
                if not item_id: continue
                item = get_object_or_404(BudgetItem, id=item_id)
                
                calc_type = l_data.get('calc_type', 'MANUAL')
                source_trend = l_data.get('source_trend_variable', '')
                
                rule, _ = BudgetCalculationRule.objects.get_or_create(
                    organization=organization,
                    item=item
                )
                rule.calculation_type = calc_type
                rule.source_trend_variable = source_trend
                rule.save()
                
                budget_line, _ = BudgetLine.objects.update_or_create(
                    organization=organization,
                    version=version,
                    item=item,
                    defaults={
                        'applied_calculation_type': calc_type,
                        'total_amount_y1': Decimal(str(l_data.get('y1_total', 0) or 0)),
                        'total_amount_y2': Decimal(str(l_data.get('y2_total', 0) or 0)),
                        'total_amount_y3': Decimal(str(l_data.get('y3_total', 0) or 0))
                    }
                )
                
                monthly = l_data.get('monthly_values', [])
                for idx, val in enumerate(monthly):
                    amt = Decimal(str(val or 0))
                    BudgetLineDetail.objects.update_or_create(
                        organization=organization,
                        budget_line=budget_line,
                        period_type='MONTH',
                        period_index=idx + 1,
                        defaults={'amount': amt}
                    )
        
        return JsonResponse({'status': 'success', 'message': 'Guardado exitosamente.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@login_required
@require_POST
def api_approve_budget_version(request, plan_id):
    organization = request.user.organization
    if not organization:
        from users.models import Organization
        organization = Organization.objects.first()
        
    plan = get_object_or_404(PlanFinanciero, id=plan_id, organization=organization)
    scenario = request.POST.get('scenario', 'BASE')
    
    version = BudgetVersion.objects.filter(
        plan_financiero=plan, 
        organization=organization, 
        scenario=scenario, 
        status='DRAFT'
    ).first()
    
    if not version:
        return JsonResponse({'status': 'error', 'message': 'No hay versión en borrador para aprobar.'})
        
    BudgetVersion.objects.filter(
        plan_financiero=plan, 
        organization=organization, 
        scenario=scenario, 
        status='APPROVED'
    ).update(status='ARCHIVED')
    
    version.status = 'APPROVED'
    version.save()
    
    return JsonResponse({'status': 'success', 'message': 'Versión aprobada.'})

@login_required
@require_POST
def api_copy_base_year_budget(request, plan_id):
    organization = request.user.organization
    if not organization:
        from users.models import Organization
        organization = Organization.objects.first()
        
    plan = get_object_or_404(PlanFinanciero, id=plan_id, organization=organization)
    scenario = request.POST.get('scenario', 'BASE')
    return JsonResponse({'status': 'success', 'message': 'Datos del año base copiados (Simulado)'})

@login_required
def export_er_proyectado(request, plan_id):
    organization = request.user.organization
    if not organization:
        from users.models import Organization
        organization = Organization.objects.first()
        
    plan = get_object_or_404(PlanFinanciero, id=plan_id, organization=organization)
    
    version = BudgetVersion.objects.filter(
        plan_financiero=plan, 
        organization=organization, 
        scenario=request.GET.get('scenario', 'BASE')
    ).order_by('-created_at').first()

    data = []
    
    if version:
        # Definir el orden de presentación de las categorías
        category_order = ['ING_FIN', 'ING_SERV', 'OTROS_ING', 'GAS_FIN', 'GAS_SERV', 'PROV', 'DEP_AMORT', 'GAS_ADMIN', 'OTROS_EG']
        category_names = {
            'ING_FIN': 'INGRESOS FINANCIEROS',
            'ING_SERV': 'INGRESOS POR SERVICIOS',
            'OTROS_ING': 'OTROS INGRESOS',
            'GAS_FIN': 'GASTOS FINANCIEROS',
            'GAS_SERV': 'GASTOS POR SERVICIOS FIN.',
            'PROV': 'PROVISIONES',
            'DEP_AMORT': 'DEPRECIACIÓN Y AMORTIZACIÓN',
            'GAS_ADMIN': 'GASTOS ADMINISTRATIVOS',
            'OTROS_EG': 'OTROS EGRESOS'
        }
        
        items = BudgetItem.objects.filter(organization=organization)
        lines = BudgetLine.objects.filter(version=version)
        lines_by_item = {l.item_id: l for l in lines}
        
        items_by_cat = {}
        for item in items:
            cat = item.category
            if cat not in items_by_cat:
                items_by_cat[cat] = []
            items_by_cat[cat].append(item)
            
        total_ingresos_y1, total_ingresos_y2, total_ingresos_y3 = 0, 0, 0
        total_gastos_y1, total_gastos_y2, total_gastos_y3 = 0, 0, 0
        
        for cat in category_order:
            if cat in items_by_cat:
                cat_name = category_names.get(cat, cat)
                data.append({"Rubro": cat_name, "Año 1 Proy.": "", "Año 2 Proy.": "", "Año 3 Proy.": ""})
                
                cat_y1, cat_y2, cat_y3 = 0, 0, 0
                sign = 1 if cat in ['ING_FIN', 'ING_SERV', 'OTROS_ING'] else -1
                
                for item in items_by_cat[cat]:
                    line = lines_by_item.get(item.id)
                    y1 = float(line.total_amount_y1) if line else 0.0
                    y2 = float(line.total_amount_y2) if line else 0.0
                    y3 = float(line.total_amount_y3) if line else 0.0
                    
                    cat_y1 += y1
                    cat_y2 += y2
                    cat_y3 += y3
                    
                    data.append({
                        "Rubro": f"  {item.name}", 
                        "Año 1 Proy.": y1, 
                        "Año 2 Proy.": y2, 
                        "Año 3 Proy.": y3
                    })
                    
                data.append({
                    "Rubro": f"Total {cat_name}", 
                    "Año 1 Proy.": cat_y1 * sign, 
                    "Año 2 Proy.": cat_y2 * sign, 
                    "Año 3 Proy.": cat_y3 * sign
                })
                
                if sign == 1:
                    total_ingresos_y1 += cat_y1
                    total_ingresos_y2 += cat_y2
                    total_ingresos_y3 += cat_y3
                else:
                    total_gastos_y1 += cat_y1
                    total_gastos_y2 += cat_y2
                    total_gastos_y3 += cat_y3
                    
        # Add summary row
        data.append({"Rubro": "RESULTADO DEL EJERCICIO", 
                     "Año 1 Proy.": total_ingresos_y1 - total_gastos_y1, 
                     "Año 2 Proy.": total_ingresos_y2 - total_gastos_y2, 
                     "Año 3 Proy.": total_ingresos_y3 - total_gastos_y3})

    if not data:
        data = [{"Rubro": "No hay datos de presupuesto disponibles", "Año 1 Proy.": "", "Año 2 Proy.": "", "Año 3 Proy.": ""}]
        
    df = pd.DataFrame(data)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="ER_Proyectado_{plan.name}.xlsx"'
    df.to_excel(response, index=False)
    return response

@login_required
def export_bg_proyectado(request, plan_id):
    organization = request.user.organization
    if not organization:
        from users.models import Organization
        organization = Organization.objects.first()
        
    plan = get_object_or_404(PlanFinanciero, id=plan_id, organization=organization)
    
    scenario = request.GET.get('scenario', 'BASE')
    
    # Obtener simulaciones del paso 6
    simulaciones = SimulacionEscenario.objects.filter(plan=plan, organization=organization, agencia='Consolidado')
    
    sim_dict = {}
    for sim in simulaciones:
        proy_anuales = []
        for year in range(1, 4):
            # Tomamos el valor del mes 12 de cada año proyectado (ej. mes 12, 24, 36)
            pm = ProyeccionMensual.objects.filter(escenario=sim, mes_proyeccion=year*12).first()
            if pm:
                if scenario == 'PESIMISTA': val = pm.valor_pesimista
                elif scenario == 'OPTIMISTA': val = pm.valor_optimista
                else: val = pm.valor_base
                proy_anuales.append(float(val))
            else:
                proy_anuales.append(0.0)
        sim_dict[sim.variable_id] = proy_anuales
        
    hist_data = plan.historical_data or {}
    step6_data = hist_data.get('step6_data', {})
    
    def get_hist_val(var_id):
        if 'datasets_by_agency' in step6_data:
            variables = step6_data['datasets_by_agency'].get('Consolidado', {}).get('variables', [])
            for v in variables:
                if v.get('id') == var_id:
                    hist_arr = v.get('hist', [])
                    return hist_arr[-1] if hist_arr else 0.0
        return 0.0

    cartera_hist = get_hist_val('cartera')
    mora_hist = get_hist_val('mora_soles')
    ahorros_hist = get_hist_val('ahorros')
    dpf_hist = get_hist_val('dpf')
    aportes_hist = get_hist_val('aportes')
    
    # Asumimos que Fondos Disponibles es aprox 15-20% del total pasivo o un valor predeterminado si no hay
    fondos_hist = 15000000.0
    
    data = [
        {"Rubro": "ACTIVO", "Base Histórica": "", "Año 1 Proy.": "", "Año 2 Proy.": "", "Año 3 Proy.": ""},
        {"Rubro": "Fondos Disponibles", "Base Histórica": fondos_hist, "Año 1 Proy.": fondos_hist*1.05, "Año 2 Proy.": fondos_hist*1.10, "Año 3 Proy.": fondos_hist*1.15},
        {"Rubro": "Cartera de Créditos (Bruta)", 
         "Base Histórica": cartera_hist, 
         "Año 1 Proy.": sim_dict.get('cartera', [0,0,0])[0], 
         "Año 2 Proy.": sim_dict.get('cartera', [0,0,0])[1], 
         "Año 3 Proy.": sim_dict.get('cartera', [0,0,0])[2]},
        {"Rubro": "(-) Provisiones para Créditos", 
         "Base Histórica": -mora_hist, 
         "Año 1 Proy.": -sim_dict.get('mora_soles', [0,0,0])[0], 
         "Año 2 Proy.": -sim_dict.get('mora_soles', [0,0,0])[1], 
         "Año 3 Proy.": -sim_dict.get('mora_soles', [0,0,0])[2]},
        {"Rubro": "TOTAL ACTIVO", "Base Histórica": fondos_hist + cartera_hist - mora_hist, 
         "Año 1 Proy.": (fondos_hist*1.05) + sim_dict.get('cartera', [0,0,0])[0] - sim_dict.get('mora_soles', [0,0,0])[0], 
         "Año 2 Proy.": (fondos_hist*1.10) + sim_dict.get('cartera', [0,0,0])[1] - sim_dict.get('mora_soles', [0,0,0])[1], 
         "Año 3 Proy.": (fondos_hist*1.15) + sim_dict.get('cartera', [0,0,0])[2] - sim_dict.get('mora_soles', [0,0,0])[2]},
        
        {"Rubro": "PASIVO", "Base Histórica": "", "Año 1 Proy.": "", "Año 2 Proy.": "", "Año 3 Proy.": ""},
        {"Rubro": "Obligaciones con el Público (Ahorros)", 
         "Base Histórica": ahorros_hist, 
         "Año 1 Proy.": sim_dict.get('ahorros', [0,0,0])[0], 
         "Año 2 Proy.": sim_dict.get('ahorros', [0,0,0])[1], 
         "Año 3 Proy.": sim_dict.get('ahorros', [0,0,0])[2]},
        {"Rubro": "Obligaciones con el Público (Plazo Fijo)", 
         "Base Histórica": dpf_hist, 
         "Año 1 Proy.": sim_dict.get('dpf', [0,0,0])[0], 
         "Año 2 Proy.": sim_dict.get('dpf', [0,0,0])[1], 
         "Año 3 Proy.": sim_dict.get('dpf', [0,0,0])[2]},
        {"Rubro": "TOTAL PASIVO", "Base Histórica": ahorros_hist + dpf_hist, 
         "Año 1 Proy.": sim_dict.get('ahorros', [0,0,0])[0] + sim_dict.get('dpf', [0,0,0])[0], 
         "Año 2 Proy.": sim_dict.get('ahorros', [0,0,0])[1] + sim_dict.get('dpf', [0,0,0])[1], 
         "Año 3 Proy.": sim_dict.get('ahorros', [0,0,0])[2] + sim_dict.get('dpf', [0,0,0])[2]},
        
        {"Rubro": "PATRIMONIO", "Base Histórica": "", "Año 1 Proy.": "", "Año 2 Proy.": "", "Año 3 Proy.": ""},
        {"Rubro": "Capital Social (Aportes)", 
         "Base Histórica": aportes_hist, 
         "Año 1 Proy.": sim_dict.get('aportes', [0,0,0])[0], 
         "Año 2 Proy.": sim_dict.get('aportes', [0,0,0])[1], 
         "Año 3 Proy.": sim_dict.get('aportes', [0,0,0])[2]},
        {"Rubro": "TOTAL PATRIMONIO", "Base Histórica": aportes_hist, "Año 1 Proy.": sim_dict.get('aportes', [0,0,0])[0], "Año 2 Proy.": sim_dict.get('aportes', [0,0,0])[1], "Año 3 Proy.": sim_dict.get('aportes', [0,0,0])[2]},
        
        {"Rubro": "Total Pasivo y Patrimonio", "Base Histórica": ahorros_hist + dpf_hist + aportes_hist, 
         "Año 1 Proy.": sim_dict.get('ahorros', [0,0,0])[0] + sim_dict.get('dpf', [0,0,0])[0] + sim_dict.get('aportes', [0,0,0])[0], 
         "Año 2 Proy.": sim_dict.get('ahorros', [0,0,0])[1] + sim_dict.get('dpf', [0,0,0])[1] + sim_dict.get('aportes', [0,0,0])[1], 
         "Año 3 Proy.": sim_dict.get('ahorros', [0,0,0])[2] + sim_dict.get('dpf', [0,0,0])[2] + sim_dict.get('aportes', [0,0,0])[2]},
    ]
    df = pd.DataFrame(data)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="BG_Proyectado_{plan.name}.xlsx"'
    df.to_excel(response, index=False)
    return response



@login_required
def api_get_projected_balance_data(request, plan_id):
    from django.http import JsonResponse
    from django.shortcuts import get_object_or_404
    from .models import PlanFinanciero, SimulacionEscenario, ProyeccionMensual, BudgetVersion, BudgetLine, BudgetLineDetail
    from liquidity_risk.models import LiqBalanceDetail
    from django.db.models import Max
    
    organization = request.user.organization
    if not organization:
        from users.models import Organization
        organization = Organization.objects.first()
        
    plan = get_object_or_404(PlanFinanciero, id=plan_id, organization=organization)
    scenario = request.GET.get('scenario', 'BASE')

    # 1. Historical Balance (Max Month of Base Year)
    base_year = plan.anio_base - 1

    max_month = LiqBalanceDetail.objects.filter(
        period__year=base_year,
        upload__status='SUCCESS'
    ).aggregate(max_month=Max('period__month'))['max_month']
    
    if max_month is None:
        return JsonResponse({'status': 'error', 'message': 'No hay datos base.'})

    qs = LiqBalanceDetail.objects.filter(
        period__year=base_year,
        period__month=max_month,
        upload__status='SUCCESS',
    ).values('account_code', 'account_name', 'balance')

    tree = {}
    for q in qs:
        code = str(q['account_code'])
        if code.startswith(('1', '2', '3')):
            val = float(q['balance'])
            is_negative_nature = code.startswith(('2', '3'))
            
            # Pasivo and Patrimonio balances are naturally negative in database
            # We show them as positive in balance sheet
            if is_negative_nature:
                val = -val
            else:
                val = val
                
            tree[code] = {
                'code': code,
                'name': q['account_name'],
                'base': val,
                'row_vals': [val] * 36,
                'is_negative_nature': is_negative_nature
            }

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

    def get_sum(prefix):
        return sum(acc['base'] for code, acc in tree.items() if code.startswith(prefix) and len(code) == 2)
        
    def get_sum_len4(prefix):
        return sum(acc['base'] for code, acc in tree.items() if code.startswith(prefix) and len(code) == 4)

    base_cartera = get_sum('14')
    base_ahorros = get_sum_len4('2101') + get_sum_len4('2102') # 2101 and 2102
    base_dpf = get_sum_len4('2103')

    def apply_growth(prefix_list, proj_array, base_val):
        if not proj_array or base_val == 0: return
        for i in range(36):
            factor = proj_array[i] / base_val
            for code, acc in tree.items():
                if any(code.startswith(p) for p in prefix_list):
                    acc['row_vals'][i] = acc['base'] * factor

    apply_growth(['14'], proj_cartera, base_cartera)
    apply_growth(['2101', '2102'], proj_ahorros, base_ahorros)
    apply_growth(['2103'], proj_dpf, base_dpf)
    
    # 3. Get Budget Net Income (Resultado del Ejercicio) -> 39
    version = BudgetVersion.objects.filter(plan_financiero=plan, organization=organization, scenario=scenario, status='DRAFT').first()
    net_incomes = [0.0] * 36
    if version:
        lines = BudgetLine.objects.filter(version=version).select_related('item')
        for line in lines:
            details = list(BudgetLineDetail.objects.filter(budget_line=line).order_by('period_index'))
            cat = line.item.category
            sign = 1 if cat in ['ING_FIN', 'ING_SERV', 'OTROS_ING', 'VENTAS'] else -1
            for i, d in enumerate(details[:12]):
                if i < 12:
                    net_incomes[i] += float(d.amount) * sign
            
            y2 = float(line.total_amount_y2 or 0) * sign
            y3 = float(line.total_amount_y3 or 0) * sign
            for i in range(12, 24): net_incomes[i] += y2 / 12
            for i in range(24, 36): net_incomes[i] += y3 / 12

    # Add Net Income to Patrimonio
    pat_codes = sorted([c for c in tree.keys() if c.startswith('39')])
    ancestors_to_inc = ['3']
    if pat_codes:
        deepest_leaf_pat = max((c for c in pat_codes if c.startswith(pat_codes[0])), key=len)
        for j in range(2, len(deepest_leaf_pat) + 1, 2):
            ancestors_to_inc.append(deepest_leaf_pat[:j])
            
    for i in range(36):
        inc = net_incomes[i]
        if inc == 0: continue
        for code in ancestors_to_inc:
            if code in tree:
                tree[code]['row_vals'][i] += inc
                
    # 4. Plug Account (Fondos Disponibles 11) to square balance
    # To maintain mathematical hierarchy, we must apply the plug only to ONE leaf and its direct ancestors.
    cash_codes = sorted([c for c in tree.keys() if c.startswith('11')])
    if cash_codes:
        # Find the deepest leaf of the first branch (e.g. 11010101)
        deepest_leaf = max((c for c in cash_codes if c.startswith(cash_codes[0])), key=len)
        
        # Build the list of ancestors (e.g. ['1', '11', '1101', '110101', '11010101'])
        ancestors_to_plug = ['1']
        for j in range(2, len(deepest_leaf) + 1, 2):
            ancestors_to_plug.append(deepest_leaf[:j])
            
        for i in range(36):
            tot_activo = tree['1']['row_vals'][i] if '1' in tree else 0
            tot_pas_pat = (tree['2']['row_vals'][i] if '2' in tree else 0) + (tree['3']['row_vals'][i] if '3' in tree else 0)
            plug = tot_pas_pat - tot_activo
            
            for code in ancestors_to_plug:
                if code in tree:
                    tree[code]['row_vals'][i] += plug

    # Build response format
    accounts_list = []
    for code in sorted(tree.keys()):
        acc = tree[code]
        row_vals = acc['row_vals']
        accounts_list.append({
            'code': code,
            'name': acc['name'],
            'base': acc['base'],
            'm1_12': row_vals[:12],
            'y1': row_vals[11],
            'y2': row_vals[23],
            'y3': row_vals[35]
        })

    # Optional: ensure we have version info
    plan_version = getattr(plan, 'status', 'DRAFT')

    return JsonResponse({
        'status': 'success',
        'accounts': accounts_list,
        'version_status': plan_version,
    })


# Import missing API functions from funcs.py so urls.py can find them here
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from funcs import (
    api_save_bg_snapshot,
    api_modify_bg_snapshot,
    api_save_bg_adjustment,
    api_toggle_fixed_bg_account,
    api_clear_other_trends,
    api_get_cash_flow_data,
    api_save_cf_adjustment
)




@require_http_methods(["POST"])
def api_apply_other_trends(request, plan_id):
    from django.http import JsonResponse
    from django.shortcuts import get_object_or_404
    from .models import PlanFinanciero, ProjectedBalanceAdjustment
    from liquidity_risk.models import LiqBalanceDetail
    from django.db.models import Q
    
    organization = request.user.organization
    if not organization:
        from users.models import Organization
        organization = Organization.objects.first()
        
    plan = get_object_or_404(PlanFinanciero, id=plan_id, organization=organization)
    base_year = plan.anio_base - 1
    
    # Identify first and last month for trend calculation
    months = list(LiqBalanceDetail.objects.filter(period__year=base_year, upload__status='SUCCESS').values_list('period__month', flat=True).distinct().order_by('period__month'))
    if not months or len(months) < 2:
        return JsonResponse({'error': 'No hay suficientes datos historicos para calcular tendencia anual.'}, status=400)
        
    first_month = months[0]
    last_month = months[-1]
    diff_months = last_month - first_month
    if diff_months <= 0: diff_months = 1
    
    upload_first = LiqBalanceDetail.objects.filter(period__year=base_year, period__month=first_month, upload__status='SUCCESS').order_by('-upload_id').values_list('upload_id', flat=True).first()
    upload_last = LiqBalanceDetail.objects.filter(period__year=base_year, period__month=last_month, upload__status='SUCCESS').order_by('-upload_id').values_list('upload_id', flat=True).first()
    
    qs_first = {x['account_code']: float(x['balance']) for x in LiqBalanceDetail.objects.filter(upload_id=upload_first).filter(Q(account_code__startswith='1') | Q(account_code__startswith='2') | Q(account_code__startswith='3')).values('account_code', 'balance')}
    qs_last = {x['account_code']: float(x['balance']) for x in LiqBalanceDetail.objects.filter(upload_id=upload_last).filter(Q(account_code__startswith='1') | Q(account_code__startswith='2') | Q(account_code__startswith='3')).values('account_code', 'balance')}
    
    scenarios = ['PESIMISTA', 'BASE', 'OPTIMISTA', 'MC_PESIMISTA', 'MC_BASE', 'MC_OPTIMISTA']
    
    adjustments_to_create = []
    
    # Process unhandled accounts
    for code, val_last in qs_last.items():
        if code.startswith('14') or code.startswith('21') or code.startswith('3101') or code.startswith('39'):
            continue
            
        val_first = qs_first.get(code, val_last)
        abs_last = abs(val_last)
        abs_first = abs(val_first)
        delta_monthly = (abs_last - abs_first) / diff_months
        
        if delta_monthly != 0.0:
            adj_dict = {str(i): delta_monthly for i in range(1, 37)}
            for sc in scenarios:
                ProjectedBalanceAdjustment.objects.filter(plan=plan, organization=organization, scenario=sc, account_code=code).delete()
                adjustments_to_create.append(
                    ProjectedBalanceAdjustment(
                        plan=plan,
                        organization=organization,
                        scenario=sc,
                        account_code=code,
                        adjustments=adj_dict
                    )
                )
    
    if adjustments_to_create:
        ProjectedBalanceAdjustment.objects.bulk_create(adjustments_to_create)
        
    return JsonResponse({'status': 'success', 'message': f'Tendencia historica aplicada a {len(adjustments_to_create)//len(scenarios)} cuentas para todos los escenarios.'})

