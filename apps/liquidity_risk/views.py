from django.shortcuts import render, redirect
from django.utils import timezone
from .engine.cashflow import get_cashflow_projections
from .engine.validator import validar_cruce_maestro
from liquidity_risk.models import CarteraPasivoCarga, VolatileBalanceLar, SbsParameter, LiqBalanceDetail
from credit_risk.models import CarteraCreditoCarga
from datetime import datetime
from decimal import Decimal

def validacion_maestra(request):
    pasivos_periods = list(CarteraPasivoCarga.objects.values_list('fecha_corte', flat=True).distinct())
    creditos_periods = list(CarteraCreditoCarga.objects.values_list('fecha_corte', flat=True).distinct())
    contabilidad_periods = list(LiqBalanceDetail.objects.values_list('period', flat=True).distinct())
    periods = sorted(list(set(pasivos_periods + creditos_periods + contabilidad_periods)), reverse=True)
    
    cutoff_date = periods[0] if periods else timezone.now().date()
    if 'period' in request.GET:
        try:
            cutoff_date = datetime.strptime(request.GET['period'], '%Y-%m-%d').date()
        except:
            pass
            
    validacion = None
    if cutoff_date:
        validacion = validar_cruce_maestro(cutoff_date)
        
    context = {
        'periods': periods,
        'cutoff_date': cutoff_date,
        'selected_period': cutoff_date.strftime('%Y-%m-%d') if cutoff_date else '',
        'validacion': validacion
    }
    return render(request, 'liquidity_risk/validacion.html', context)

def dashboard(request):
    pasivos_periods = list(CarteraPasivoCarga.objects.values_list('fecha_corte', flat=True).distinct())
    creditos_periods = list(CarteraCreditoCarga.objects.values_list('fecha_corte', flat=True).distinct())
    contabilidad_periods = list(LiqBalanceDetail.objects.values_list('period', flat=True).distinct())
    periods = sorted(list(set(pasivos_periods + creditos_periods + contabilidad_periods)), reverse=True)
    
    cutoff_date = periods[0] if periods else timezone.now().date()
    if 'period' in request.GET:
        try:
            cutoff_date = datetime.strptime(request.GET['period'], '%Y-%m-%d').date()
        except:
            pass

    try:
        report = get_cashflow_projections(cutoff_date)
    except Exception as e:
        report = None
        error = str(e)
        
    validacion = None
    if cutoff_date:
        validacion = validar_cruce_maestro(cutoff_date)
        
    context = {
        'periods': periods,
        'cutoff_date': cutoff_date,
        'selected_period': cutoff_date.strftime('%Y-%m-%d') if cutoff_date else '',
        'report': report,
        'validacion': validacion,
        'error': error if 'error' in locals() else None
    }
    return render(request, 'liquidity_risk/dashboard_sbs.html', context)

def metodologia_lar(request):
    if request.method == 'POST':
        # Simple save
        period_str = request.POST.get('period')
        segment = request.POST.get('segment')
        currency = request.POST.get('currency', 'MN')
        vol_pct = request.POST.get('volatility', 0)
        
        try:
            period_date = datetime.strptime(period_str, '%Y-%m-%d').date()
            VolatileBalanceLar.objects.update_or_create(
                period=period_date,
                segment=segment,
                currency=currency,
                defaults={
                    'volatility_percentage': Decimal(vol_pct),
                    'executed_by': request.user.username if request.user.is_authenticated else 'admin'
                }
            )
        except Exception as e:
            pass
        return redirect('liquidity_risk:metodologia_lar')

    records = VolatileBalanceLar.objects.all().order_by('-period')
    
    # Periods for dropdown
    pasivos_periods = list(CarteraPasivoCarga.objects.values_list('fecha_corte', flat=True).distinct())
    creditos_periods = list(CarteraCreditoCarga.objects.values_list('fecha_corte', flat=True).distinct())
    periods = sorted(list(set(pasivos_periods + creditos_periods)), reverse=True)

    return render(request, 'liquidity_risk/metodologia_lar.html', {
        'records': records,
        'periods': periods
    })

def parametrizacion_sbs(request):
    if request.method == 'POST':
        # Simple save all parameters from form
        for key, value in request.POST.items():
            if key.startswith('param_'):
                code = key.replace('param_', '')
                try:
                    param = SbsParameter.objects.get(code=code)
                    param.limit_value = Decimal(value)
                    param.save()
                except SbsParameter.DoesNotExist:
                    pass
        return redirect('liquidity_risk:parametrizacion_sbs')

    parameters = SbsParameter.objects.all()
    if not parameters.exists():
        # Create default ones matching the screenshot
        defaults = [
            ('Indicador de Liquidez MN', 'IL_MN', '>=', 8.00, 'Porcentaje'),
            ('Indicador de Liquidez ME', 'IL_ME', '>=', 20.00, 'Porcentaje'),
            ('10 Mayores Acreedores', 'TOP10_ACR', '<=', 20.00, 'Porcentaje'),
            ('20 Mayores Depositantes', 'TOP20_DEP', '<=', 20.00, 'Porcentaje'),
            ('Inversiones / Patrimonio Efectivo', 'INV_PE', '<=', 15.00, 'Porcentaje'),
            ('Préstamos > 1 año / Patrimonio Efectivo', 'LOAN1Y_PE', '<=', 3.50, 'Ratio / Valor'),
            ('Brechas Negativas', 'GAP_NEG', 'N/A', 0.00, 'Ratio / Valor'),
        ]
        for ind, code, sign, val, t in defaults:
            SbsParameter.objects.create(
                indicator=ind, code=code, sign=sign, limit_value=Decimal(val), limit_type=t
            )
        parameters = SbsParameter.objects.all()

    return render(request, 'liquidity_risk/parametrizacion_sbs.html', {
        'parameters': parameters
    })
