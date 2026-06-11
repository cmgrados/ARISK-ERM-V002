from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import pandas as pd
import io
from django.utils.timezone import now
from .models import (
    LiqBalanceUpload, LiqSavingsUpload, LiqTermDepositUpload,
    LiqBalanceDetail, LiqSavingsAccount, LiqTermDeposit,
    LiqAccountMapping, LiqAccountPlanModel, LiqLoadStatus, LiqSbsLimit,
    LiqLaRResult
)
from .loaders import (
    process_balance_load, process_savings_load, process_account_mapping_load
)
from .engine import get_latest_period, calculate_liquidity_metrics, generate_maturity_gap, calculate_lar, generate_interpretative_analysis
from datetime import datetime

from django.db.models import Sum, Max, Q
from decimal import Decimal

@login_required
def dashboard(request):
    # Distinct periods available
    available_periods = LiqBalanceUpload.objects.filter(status=LiqLoadStatus.SUCCESS).values_list('period', flat=True).distinct().order_by('-period')
    
    selected_period_str = request.GET.get('period')
    if selected_period_str:
        try:
            selected_date = datetime.strptime(selected_period_str, '%Y-%m-%d').date()
        except:
            selected_date = get_latest_period()
    else:
        selected_date = get_latest_period()

    # Calculate indicators via engine
    metrics = calculate_liquidity_metrics(selected_date)
    gap_table = generate_maturity_gap(selected_date)
    
    context = {
        'page_title': 'Panel Ejecutivo de Riesgo de Liquidez',
        'metrics': metrics,
        'gap_table': gap_table,
        'periods': available_periods,
        'selected_period': selected_date,
    }
    return render(request, 'liquidity_risk/dashboard.html', context)

# -----------------------------------------------------------------------------
# CARGA DE INFORMACIÓN (Balance Loading and Account Mapping moved to Utilities)
# -----------------------------------------------------------------------------

@login_required
def load_savings(request):
    if request.method == 'POST':
        period = request.POST.get('period')
        file = request.FILES.get('file')
        if period and file:
            upload, created = LiqSavingsUpload.objects.update_or_create(
                period=period,
                defaults={'file_source': file, 'user': request.user, 'status': LiqLoadStatus.PENDING}
            )
            if process_savings_load(upload.id):
                messages.success(request, "Reporte de ahorros cargado correctamente.")
            else:
                messages.error(request, "Error al procesar el reporte de ahorros.")
        return redirect('liquidity_risk:load_savings')

    history = LiqSavingsUpload.objects.all().order_by('-period')
    return render(request, 'liquidity_risk/loaders/load_savings.html', {
        'page_title': 'Carga de Reporte de Ahorros',
        'history': history
    })

# Stub for other loads
@login_required
def load_term_deposits(request):
    if request.method == 'POST':
        period = request.POST.get('period')
        file = request.FILES.get('file')
        if period and file:
            upload, created = LiqTermDepositUpload.objects.update_or_create(
                period=period,
                defaults={'file_source': file}
            )
            # Logic to process DPF will be called here
            messages.success(request, "Auxiliar de DPF cargado correctamente.")
        return redirect('liquidity_risk:load_term_deposits')

    history = LiqTermDepositUpload.objects.all().order_by('-period')
    return render(request, 'liquidity_risk/loaders/load_dpf.html', {
        'page_title': 'Carga de Auxiliar DPF',
        'history': history
    })

@login_required
def load_funding(request):
    if request.method == 'POST':
        period = request.POST.get('period')
        file = request.FILES.get('file')
        if period and file:
            upload, created = LiqFundingUpload.objects.update_or_create(
                period=period,
                defaults={'file_source': file, 'user': request.user}
            )
            messages.success(request, "Auxiliar de líneas de financiamiento cargado.")
        return redirect('liquidity_risk:load_funding')
    
    history = LiqFundingUpload.objects.all().order_by('-period')
    return render(request, 'liquidity_risk/loaders/load_funding.html', {
        'page_title': 'Carga de Líneas de Financiamiento',
        'history': history
    })

@login_required
def load_investments(request):
    if request.method == 'POST':
        period = request.POST.get('period')
        file = request.FILES.get('file')
        if period and file:
            upload, created = LiqInvestmentUpload.objects.update_or_create(
                period=period,
                defaults={'file_source': file, 'user': request.user}
            )
            messages.success(request, "Auxiliar de inversiones cargado.")
        return redirect('liquidity_risk:load_investments')

    history = LiqInvestmentUpload.objects.all().order_by('-period')
    return render(request, 'liquidity_risk/loaders/load_investments.html', {
        'page_title': 'Carga de Inversiones',
        'history': history
    })

@login_required
def load_contributions(request):
    return render(request, 'liquidity_risk/loaders/load_contributions.html', {
        'page_title': 'Carga de Aportes Sociales'
    })

@login_required
def load_portfolio(request):
    return render(request, 'liquidity_risk/loaders/load_portfolio.html', {
        'page_title': 'Carga de Cartera de Créditos (Auxiliar)'
    })

@login_required
def validations(request):
    return render(request, 'liquidity_risk/loaders/validations.html', {
        'page_title': 'Validación y Conciliación de Cargas'
    })

@login_required
def monthly_position(request):
    upload_id = request.GET.get('upload_id')
    if upload_id:
        upload = get_object_or_404(LiqBalanceUpload, id=upload_id)
    else:
        upload = LiqBalanceUpload.objects.filter(status='SUCCESS').order_by('-period').first()
    
    results = []
    if upload:
        # Optimized Database Grouping
        item_groups = LiqBalanceDetail.objects.filter(upload=upload).values('liquidity_item').annotate(
            total=Sum('balance')
        ).order_by('liquidity_item')
        
        for group in item_groups:
            item = group['liquidity_item'] or "SIN VINCULAR"
            results.append({
                'item': item,
                'total': group['total'],
                'type': 'ACT' if any(x in item.upper() for x in ['ACTIVO', 'DISPONIBLE', 'INVERSIONES', 'CREDITOS']) else 'PAS'
            })
            
    context = {
        'page_title': 'Posición Mensual de Liquidez',
        'upload': upload,
        'results': results,
        'all_uploads': LiqBalanceUpload.objects.filter(status='SUCCESS').order_by('-period')
    }
    return render(request, 'liquidity_risk/analytics/position.html', context)
@login_required
def gap_analysis(request):
    
    period_str = request.GET.get('period')
    currency = request.GET.get('currency', 'MN')
    
    if period_str:
        period = datetime.strptime(period_str, '%Y-%m-%d').date()
    else:
        period = get_latest_period()
        
    matrix = generate_maturity_gap(period, currency)
    
    # Calculate summary for cards
    gap_30 = matrix['gaps_accumulated'][0] if matrix.get('gaps_accumulated') else Decimal('0')
    gap_90 = matrix['gaps_accumulated'][2] if len(matrix.get('gaps_accumulated', [])) > 2 else Decimal('0')
    lar_res = LiqLaRResult.objects.filter(period=period, currency=currency, is_official=True).first()
            
    context = {
        'page_title': 'Análisis de Brecha de Liquidez',
        'period': period,
        'currency': currency,
        'matrix': matrix,
        'gap_30': gap_30,
        'gap_90': gap_90,
        'lar_res': lar_res,
        'all_periods': LiqBalanceUpload.objects.filter(status='SUCCESS').values_list('period', flat=True).distinct().order_by('-period')
    }
    return render(request, 'liquidity_risk/analytics/gap.html', context)
def concentration(request): return render(request, 'liquidity_risk/analytics/concentration.html', {'page_title': 'Concentración'})
def stress_testing(request): return render(request, 'liquidity_risk/analytics/stress.html', {'page_title': 'Escenarios y Stress Testing'})

# -----------------------------------------------------------------------------
# OTROS
# -----------------------------------------------------------------------------

@login_required
def sbs_parameters(request):
    # Inicializar parámetros si no existen
    defaults = [
        {'code': 'IL_MN', 'name': 'Indicador de Liquidez MN', 'sign': '>=', 'value': 8.0, 'pct': True},
        {'code': 'IL_ME', 'name': 'Indicador de Liquidez ME', 'sign': '>=', 'value': 20.0, 'pct': True},
        {'code': 'TOP10_ACR', 'name': '10 Mayores Acreedores', 'sign': '<=', 'value': 20.0, 'pct': True},
        {'code': 'TOP20_DEP', 'name': '20 Mayores Depositantes', 'sign': '<=', 'value': 20.0, 'pct': True},
        {'code': 'INV_PE', 'name': 'Inversiones / Patrimonio Efectivo', 'sign': '<=', 'value': 15.0, 'pct': True},
        {'code': 'LOAN1Y_PE', 'name': 'Préstamos > 1 año / Patrimonio Efectivo', 'sign': '<=', 'value': 3.5, 'pct': False},
        {'code': 'GAP_NEG', 'name': 'Brechas Negativas', 'sign': 'N/A', 'value': 0.0, 'pct': False},
    ]
    
    for d in defaults:
        LiqSbsLimit.objects.get_or_create(
            code=d['code'],
            defaults={
                'name': d['name'],
                'sign': d['sign'],
                'limit_value': d['value'],
                'is_percentage': d['pct']
            }
        )

    if request.method == 'POST':
        for key, value in request.POST.items():
            if key.startswith('limit_'):
                code = key.replace('limit_', '')
                LiqSbsLimit.objects.filter(code=code).update(limit_value=Decimal(value))
        messages.success(request, "Parámetros actualizados correctamente.")
        return redirect('liquidity_risk:sbs_parameters')

    params = LiqSbsLimit.objects.all().order_by('id')
    return render(request, 'liquidity_risk/methodologies/sbs_parameters.html', {
        'page_title': 'Parametrización Normativa SBS',
        'params': params
    })

@login_required
def lar_methodology(request):
    period_str = request.GET.get('period')
    currency = request.GET.get('currency', 'MN')
    segment = request.GET.get('segment', 'TODOS')
    
    # Get products from either GET or POST
    if request.method == 'POST':
        selected_products = request.POST.getlist('products')
    else:
        selected_products = request.GET.getlist('products')
    
    if period_str:
        try:
            period = datetime.strptime(period_str, '%Y-%m-%d').date()
        except:
            period = get_latest_period()
    else:
        period = get_latest_period()
        
    # Get available segments and products from unified model
    from .models import LiqLiabilityDetail
    liab_qs = LiqLiabilityDetail.objects.all()
    segments = [s for s in liab_qs.values_list('liquidity_item', flat=True).distinct() if s]
    
    # Filter products based on selected segment
    prod_qs = liab_qs
    if segment and segment != 'TODOS':
        prod_qs = prod_qs.filter(liquidity_item=segment)
    all_products = [p for p in prod_qs.values_list('product', flat=True).distinct() if p]
    
    # Check if calculation was requested
    lar_data = None
    if request.method == 'POST':
        confidence = Decimal(request.POST.get('confidence', '0.95'))
        historical_depth = int(request.POST.get('depth', '12'))
        
        lar_data = calculate_lar(period, currency, segment, selected_products, confidence, historical_depth)
        
        if lar_data:
            # Save or update result
            # If products were selected, we might want to note it in the segment field or metadata
            res_segment = segment
            if selected_products and segment == 'TODOS':
                res_segment = f"PRODUCTOS: {', '.join(selected_products[:2])}"
                if len(selected_products) > 2: res_segment += "..."
                
            # Generate interpretative analysis
            analysis = generate_interpretative_analysis(lar_data, currency)
            lar_data['analysis'] = analysis

            lar_res, created = LiqLaRResult.objects.update_or_create(
                period=period, segment=res_segment, currency=currency,
                defaults={
                    'total_balance': lar_data['total_balance'],
                    'lar_amount': lar_data['lar_amount'],
                    'lar_percentage': lar_data['lar_percentage'],
                    'std_dev': lar_data['std_dev'],
                    'user': request.user,
                    'calculation_data': {
                        'history': [{**x, 'period': str(x['period'])} for x in lar_data['history']],
                        'projections': lar_data.get('projections', []),
                        'selected_products': selected_products,
                        'std_dev_day': str(lar_data.get('std_dev_day', 0)),
                        'avg_variation': str(lar_data.get('avg_variation', 0)),
                        'analysis': analysis
                    }
                }
            )
            lar_data['id'] = lar_res.id
            lar_data['is_official'] = lar_res.is_official
            messages.success(request, f"Cálculo LaR completado para {res_segment} ({currency})")
            # Refresh gap analysis cache
            from django.core.cache import cache
            cache.clear()
        else:
            messages.error(request, "No hay suficiente información histórica para calcular el LaR (mínimo 2 periodos).")

    # Fetch existing result if not just calculated
    if not lar_data:
        # If no specific selection, try to find a relevant one
        q_res = Q(period=period, currency=currency)
        q_res &= Q(segment=segment)
            
        res = LiqLaRResult.objects.filter(q_res).first()
        if res:
            calc_data = res.calculation_data or {}
            lar_data = {
                'id': res.id,
                'is_official': res.is_official,
                'total_balance': res.total_balance,
                'lar_amount': res.lar_amount,
                'lar_percentage': res.lar_percentage,
                'std_dev': res.std_dev,
                'history': calc_data.get('history', []),
                'projections': calc_data.get('projections', []),
                'std_dev_day': Decimal(calc_data.get('std_dev_day', str(float(res.std_dev) / 5.477))),
                'avg_variation': Decimal(calc_data.get('avg_variation', '0')),
                'analysis': calc_data.get('analysis')
            }
            if not lar_data['analysis']:
                lar_data['analysis'] = generate_interpretative_analysis(lar_data, currency)


    # Current results for the table
    results = LiqLaRResult.objects.all().order_by('-period', 'segment')
    
    context = {
        'page_title': 'Metodología de Saldo Volátil / LaR',
        'period': period,
        'currency': currency,
        'selected_segment': segment,
        'selected_products': selected_products,
        'segments': segments,
        'all_products': all_products,
        'lar_data': lar_data,
        'results': results,
        'all_periods': LiqBalanceUpload.objects.filter(status='SUCCESS').values_list('period', flat=True).distinct().order_by('-period')
    }
    return render(request, 'liquidity_risk/methodologies/lar_methodology.html', context)
    
@login_required
def delete_lar_result(request, pk):
    res = get_object_or_404(LiqLaRResult, pk=pk)
    # Allow both POST and a GET with confirm parameter for better compatibility
    if request.method == 'POST' or request.GET.get('confirm') == 'true':
        res.delete()
        messages.success(request, "Cálculo eliminado correctamente.")
    return redirect(f"{request.META.get('HTTP_REFERER', '/liquidez/lar-metodologia/')}?msg=deleted")

@login_required
def delete_lar_upload(request, upload_type, pk):
    model = None
    if upload_type == 'savings':
        model = LiqSavingsUpload
    elif upload_type == 'dpf':
        model = LiqTermDepositUpload
    elif upload_type == 'funding':
        model = LiqFundingUpload
    elif upload_type == 'investments':
        model = LiqInvestmentUpload
    elif upload_type == 'balance':
        model = LiqBalanceUpload
    else:
        return HttpResponse("Tipo de carga no válido", status=400)
        
    upload = get_object_or_404(model, pk=pk)
    # Allow POST or GET with confirm=true
    if request.method == 'POST' or request.GET.get('confirm') == 'true':
        upload.delete()
        messages.success(request, f"Carga de {upload_type} eliminada correctamente.")
    
    return redirect(request.META.get('HTTP_REFERER', 'liquidity_risk:dashboard'))

@login_required
def delete_account_mapping(request, pk):
    mapping = get_object_or_404(LiqAccountMapping, pk=pk)
    if request.method == 'POST' or request.GET.get('confirm') == 'true':
        mapping.delete()
        messages.success(request, "Mapeo de cuenta eliminado.")
    return redirect(request.META.get('HTTP_REFERER', 'liquidity_risk:account_mapping'))

@login_required
def apply_lar_to_gap(request, pk):
    """
    Marks a specific LaR result as 'official' for the Gap Analysis distribution.
    It unmarks other results for the same period/currency/segment to ensure uniqueness.
    """
    res = get_object_or_404(LiqLaRResult, pk=pk)
    
    # Unmark others
    LiqLaRResult.objects.filter(
        period=res.period, 
        currency=res.currency, 
        segment=res.segment
    ).update(is_official=False)
    
    # Mark this one
    res.is_official = True
    res.save()
    
    messages.success(request, f"Metodología aplicada exitosamente al Análisis de Brechas para el periodo {res.period}.")
    return redirect(request.META.get('HTTP_REFERER', '/liquidez/lar-metodologia/'))
def controls(request):
    from .models import LiqAlert, LiqLimit, LiqSbsLimit, LiqBalanceUpload
    
    # Get active alerts (last 30 days)
    alerts = LiqAlert.objects.all().order_by('-created_at')[:20]
    
    # Get internal limits (Risk Appetite)
    internal_limits = LiqLimit.objects.filter(is_active=True)
    
    # Get SBS limits
    sbs_limits = LiqSbsLimit.objects.all()
    
    # Get latest evaluation date
    latest_upload = LiqBalanceUpload.objects.filter(status='SUCCESS').order_by('-period').first()
    
    return render(request, 'liquidity_risk/controls.html', {
        'page_title': 'Límites y Alertas de Liquidez',
        'alerts': alerts,
        'internal_limits': internal_limits,
        'sbs_limits': sbs_limits,
        'latest_upload': latest_upload
    })
def contingency_plan(request): return render(request, 'liquidity_risk/contingency_plan.html', {'page_title': 'Plan de Contingencia'})
def reports(request): return render(request, 'liquidity_risk/reports.html', {'page_title': 'Reportes e Historial'})
def audit(request): return render(request, 'liquidity_risk/audit.html', {'page_title': 'Aprobaciones y Auditoría'})
