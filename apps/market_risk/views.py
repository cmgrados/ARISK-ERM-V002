from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import MarketTimeBand, MarketScenario, MarketLimit, CurrencyType
from liquidity_risk.engine.cashflow import get_cashflow_projections
from liquidity_risk.models import CarteraPasivoCarga
from credit_risk.models import CreditOperation
from django.db.models import Sum
from django.utils import timezone
import json
import csv
from datetime import datetime

def _get_latest_market_data():
    pasivos_periods = list(CarteraPasivoCarga.objects.values_list('fecha_corte', flat=True).distinct())
    creditos_periods = list(CreditOperation.objects.values_list('load_date', flat=True).distinct())
    periods = sorted(list(set(pasivos_periods + creditos_periods)), reverse=True)
    cutoff_date = periods[0] if periods else timezone.now().date()
    
    try:
        report = get_cashflow_projections(cutoff_date)
    except Exception:
        report = None
    return cutoff_date, report

@login_required
def dashboard_view(request):
    cutoff_date, report = _get_latest_market_data()
    
    gap_analysis = []
    cumulative_gap = 0
    total_ear = 0
    net_usd = 0
    
    echart_bands = []
    echart_assets = []
    echart_liabilities = []
    echart_gaps = []
    
    usd_assets = 0
    usd_liab = 0
    total_assets = 0
    total_liab = 0
    
    if report:
        for band in report['bandas']:
            assets = float(report['total_activos'].get(band, 0))
            liabilities = float(report['total_pasivos'].get(band, 0))
            marginal_gap = float(report['brecha_marginal'].get(band, 0))
            cumulative_gap += marginal_gap
            
            gap_analysis.append({
                'band': band,
                'assets': assets,
                'liabilities': liabilities,
                'marginal_gap': marginal_gap,
                'cumulative_gap': cumulative_gap
            })
            
            echart_bands.append(band)
            echart_assets.append(assets)
            echart_liabilities.append(liabilities)
            echart_gaps.append(marginal_gap)
            
        # Estimación USD (mock basado en un ratio del balance total)
        total_assets = sum(float(v) for v in report['total_activos'].values())
        total_liab = sum(float(v) for v in report['total_pasivos'].values())
        usd_assets = total_assets * 0.15 # 15% as USD (Simplified)
        usd_liab = total_liab * 0.10     # 10% as USD (Simplified)
        net_usd = usd_assets - usd_liab

    scenarios = MarketScenario.objects.filter(is_active=True)
    sensitivity_results = []
    echart_scen_names = []
    echart_scen_impacts = []
    echart_dual_scatter = []
    
    for scen in scenarios:
        shock_decimal = scen.rate_shock_bps / 10000.0
        impact = float(cumulative_gap) * shock_decimal
        
        if impact < total_ear:
            total_ear = impact
            
        sensitivity_results.append({
            'scenario_name': scen.name,
            'type': scen.get_scenario_type_display(),
            'shock_bps': scen.rate_shock_bps,
            'fx_shock': scen.fx_shock_percent,
            'impact': impact
        })
        
        echart_scen_names.append(scen.name)
        echart_scen_impacts.append(impact)
        echart_dual_scatter.append([float(scen.fx_shock_percent), float(scen.rate_shock_bps)])

    pen_assets = total_assets * 0.85 if report else 0
    pen_liab = total_liab * 0.90 if report else 0

    echart_fx_data = [
        {'value': pen_assets + pen_liab, 'name': 'Soles (PEN)'},
        {'value': usd_assets + usd_liab, 'name': 'Dólares (USD)'}
    ]

    context = {
        'gap_analysis': gap_analysis,
        'sensitivity_results': sensitivity_results,
        'total_ear': total_ear,
        'net_usd': net_usd,
        'echart_bands': json.dumps(echart_bands),
        'echart_assets': json.dumps(echart_assets),
        'echart_liabilities': json.dumps(echart_liabilities),
        'echart_gaps': json.dumps(echart_gaps),
        'echart_scen_names': json.dumps(echart_scen_names),
        'echart_scen_impacts': json.dumps(echart_scen_impacts),
        'echart_dual_scatter': json.dumps(echart_dual_scatter),
        'echart_fx_data': json.dumps(echart_fx_data),
    }
    return render(request, 'market_risk/dashboard.html', context)

@login_required
def positions_view(request):
    return render(request, 'market_risk/positions.html')

@login_required
def gaps_view(request):
    return redirect('market_risk:dashboard')

@login_required
def sensitivity_view(request):
    return render(request, 'market_risk/sensitivity.html')

@login_required
def stress_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        scenario_type = request.POST.get('scenario_type', 'STRESS')
        rate_shock = float(request.POST.get('rate_shock_bps', 0))
        fx_shock = float(request.POST.get('fx_shock_percent', 0))
        
        if name:
            MarketScenario.objects.create(
                name=name, scenario_type=scenario_type, rate_shock_bps=rate_shock, fx_shock_percent=fx_shock, is_active=True
            )
            messages.success(request, f'Escenario "{name}" creado exitosamente.')
            return redirect('market_risk:stress')
            
    cutoff_date, report = _get_latest_market_data()
    cumulative_gap = 0
    net_usd = 0
    if report:
        for band in report['bandas']:
            cumulative_gap += float(report['brecha_marginal'].get(band, 0))
        total_assets = sum(float(v) for v in report['total_activos'].values())
        total_liab = sum(float(v) for v in report['total_pasivos'].values())
        net_usd = (total_assets * 0.15) - (total_liab * 0.10)

    scenarios = MarketScenario.objects.all().order_by('-id')
    results = []
    for scen in scenarios:
        rate_impact = cumulative_gap * (scen.rate_shock_bps / 10000.0)
        fx_impact = net_usd * (float(scen.fx_shock_percent) / 100.0)
        results.append({
            'scenario': scen, 'rate_impact': rate_impact, 'fx_impact': fx_impact, 'total_impact': rate_impact + fx_impact
        })
        
    context = {'results': results, 'cumulative_gap': cumulative_gap, 'net_usd': net_usd}
    return render(request, 'market_risk/stress.html', context)

@login_required
def guide_view(request):
    return render(request, 'market_risk/guide.html')

@login_required
def limits_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        threshold = float(request.POST.get('threshold_value', 0))
        is_perc = request.POST.get('is_percentage') == 'on'
        if name:
            MarketLimit.objects.create(name=name, threshold_value=threshold, is_percentage=is_perc)
            messages.success(request, f'Límite para "{name}" creado.')
            return redirect('market_risk:limits')

    cutoff_date, report = _get_latest_market_data()
    cumulative_gap = 0
    net_usd = 0
    if report:
        for band in report['bandas']:
            cumulative_gap += float(report['brecha_marginal'].get(band, 0))
        total_assets = sum(float(v) for v in report['total_activos'].values())
        total_liab = sum(float(v) for v in report['total_pasivos'].values())
        net_usd = (total_assets * 0.15) - (total_liab * 0.10)
    
    scenarios = MarketScenario.objects.filter(is_active=True)
    worst_ear = 0
    for scen in scenarios:
        impact = (cumulative_gap * (scen.rate_shock_bps / 10000.0)) + (net_usd * (float(scen.fx_shock_percent) / 100.0))
        if impact < worst_ear:
            worst_ear = impact

    kpi_map = {
        'Exposición Neta USD': abs(net_usd),
        'Peor Escenario EaR': abs(worst_ear),
        'VaR Paramétrico': 1200000.0,
        'Brecha Acumulada 1 Año': abs(cumulative_gap)
    }
    
    limits = MarketLimit.objects.all()
    evaluation = []
    for limit in limits:
        actual_val = kpi_map.get(limit.name, 0)
        ratio = (actual_val / float(limit.threshold_value)) * 100 if limit.threshold_value > 0 else 0
        status = 'success'
        if ratio >= 100: status = 'danger'
        elif ratio >= 80: status = 'warning'
        evaluation.append({'limit': limit, 'actual_value': actual_val, 'ratio': ratio, 'status': status})

    return render(request, 'market_risk/limits.html', {'evaluation': evaluation, 'kpi_options': kpi_map.keys()})

@login_required
def reports_view(request):
    return render(request, 'market_risk/reports.html')

@login_required
def export_gaps_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="reporte_brechas_liquidez.csv"'
    writer = csv.writer(response)
    writer.writerow(['Banda Temporal', 'Activos Sensibles', 'Pasivos Sensibles', 'Brecha Marginal', 'Brecha Acumulada'])
    
    cutoff_date, report = _get_latest_market_data()
    if report:
        cum_gap = 0
        for band in report['bandas']:
            a = report['total_activos'].get(band, 0)
            l = report['total_pasivos'].get(band, 0)
            m = report['brecha_marginal'].get(band, 0)
            cum_gap += m
            writer.writerow([band, a, l, m, cum_gap])
            
    return response

@login_required
def export_stress_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="reporte_estres_escenarios.csv"'
    writer = csv.writer(response)
    writer.writerow(['Nombre Escenario', 'Tipo', 'Shock Tasa (bps)', 'Shock FX (%)', 'Impacto Tasa', 'Impacto FX', 'Impacto Total'])
    
    cutoff_date, report = _get_latest_market_data()
    cumulative_gap = 0
    net_usd = 0
    if report:
        for band in report['bandas']:
            cumulative_gap += float(report['brecha_marginal'].get(band, 0))
        total_assets = sum(float(v) for v in report['total_activos'].values())
        total_liab = sum(float(v) for v in report['total_pasivos'].values())
        net_usd = (total_assets * 0.15) - (total_liab * 0.10)
        
    scenarios = MarketScenario.objects.all()
    for scen in scenarios:
        rate_impact = cumulative_gap * (scen.rate_shock_bps / 10000.0)
        fx_impact = net_usd * (float(scen.fx_shock_percent) / 100.0)
        writer.writerow([scen.name, scen.get_scenario_type_display(), scen.rate_shock_bps, scen.fx_shock_percent, rate_impact, fx_impact, rate_impact + fx_impact])
        
    return response

@login_required
def download_template_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="plantilla_deprecated.csv"'
    writer = csv.writer(response)
    writer.writerow(['Este proceso ha sido automatizado y ya no requiere plantillas.'])
    return response

@login_required
def var_view(request):
    return render(request, 'market_risk/var.html')
