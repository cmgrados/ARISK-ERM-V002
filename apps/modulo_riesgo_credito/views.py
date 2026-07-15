from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from modulo_riesgo_credito.services.portfolio import get_portfolio_by_buckets, calculate_hhi_concentration
from modulo_riesgo_credito.services.sbs_reports import export_sbs_anexo_5
from django.utils import timezone
from credit_risk.models import CreditOperation
from django.core.cache import cache
import pandas as pd
from datetime import datetime
from django.db.models import Max, Min, Sum, Count, Avg, Q

@login_required
def dashboard_seguimiento(request):
    """
    Vista principal que agrupa métricas rápidas. 
    Se calcula con agregaciones del ORM en tiempo real (<2s).
    """
    # En un caso real se elegiría la fecha del último cierre de mes
    cut_off = CreditOperation.objects.order_by('-load_date').first()
    cut_off_date = cut_off.load_date if cut_off else timezone.now().date()
    
    buckets = get_portfolio_by_buckets(cut_off_date)
    hhi_actividad = calculate_hhi_concentration(cut_off_date, 'customer__economic_activity')
    
    # Cálculos globales rápidos
    total_portfolio = sum(b['total_balance'] or 0 for b in buckets)
    total_credits = sum(b['total_count'] or 0 for b in buckets)
    
    npl_balance = sum(b['total_balance'] or 0 for b in buckets if b['bucket_label'] not in ['Bucket 0', 'Bucket 1', 'Desconocido'])
    npl_ratio = (npl_balance / total_portfolio * 100) if total_portfolio > 0 else 0
    
    # Cartera Alto Riesgo (CAR) - Bucket 2, 3, 4
    car_balance = sum(b['total_balance'] or 0 for b in buckets if b['bucket_label'] in ['Bucket 2', 'Bucket 3', 'Bucket 4'])
    car_ratio = (car_balance / total_portfolio * 100) if total_portfolio > 0 else 0
    
    # Provisiones desde CreditOperation
    from django.db.models import Sum
    provisions = CreditOperation.objects.filter(load_date=cut_off_date).aggregate(
        req=Sum('required_provision'),
        est=Sum('established_provision')
    )
    total_prov_req = provisions['req'] or 0
    total_prov_est = provisions['est'] or 0
    
    # Extraer Expected Loss si el cron ya corrió para esta fecha o de las métricas generadas
    from credit_risk.models import CreditRiskMetrics
    total_el = CreditRiskMetrics.objects.filter(operation__load_date=cut_off_date).aggregate(
        total_el=Sum('expected_loss')
    )['total_el'] or 0
    
    coverage_ratio = (total_prov_est / npl_balance * 100) if npl_balance > 0 else 0
    
    refinanced_balance = CreditOperation.objects.filter(load_date=cut_off_date).aggregate(
        total_ref=Sum('refinanced_current')
    )['total_ref'] or 0
    
    # Clasificación SBS
    from django.db.models import Sum
    sbs_classifications_data = CreditOperation.objects.filter(load_date=cut_off_date).values('sbs_classification').annotate(
        total_balance=Sum('balance')
    ).order_by('sbs_classification')
    sbs_class = [
        {'label': str(item['sbs_classification'] or 'Sin Clasificar'), 'balance': float(item['total_balance'] or 0)}
        for item in sbs_classifications_data
    ]
    
    # Evolución de Cartera
    evolution_data = CreditOperation.objects.values('load_date').annotate(
        total_balance=Sum('balance')
    ).order_by('load_date')
    evolution = [
        {'date': item['load_date'].strftime('%Y-%m-%d'), 'balance': float(item['total_balance'] or 0)}
        for item in evolution_data
    ]
    
    context = {
        'buckets': buckets,
        'sbs_class': sbs_class,
        'evolution': evolution,
        'hhi_actividad': hhi_actividad,
        'cut_off_date': cut_off_date,
        'total_portfolio': total_portfolio,
        'total_credits': total_credits,
        'npl_balance': npl_balance,
        'npl_ratio': npl_ratio,
        'car_balance': car_balance,
        'car_ratio': car_ratio,
        'coverage_ratio': coverage_ratio,
        'refinanced_balance': refinanced_balance,
        'total_expected_loss': total_el,
        'total_required_provision': total_prov_req,
        'total_established_provision': total_prov_est,
    }
    return render(request, 'riesgo/seguimiento.html', context)

@login_required
def descargar_anexo5(request):
    """
    Controlador para descargar el archivo CSV validado.
    """
    cut_off = CreditOperation.objects.order_by('-load_date').first()
    cut_off_date = cut_off.load_date if cut_off else timezone.now().date()
    return export_sbs_anexo_5(cut_off_date)

@login_required
def transition_matrix_view(request):
    """
    Renderiza la matriz de transición y roll rates con soporte de filtrado dinámico.
    """
    from datetime import timedelta
    from modulo_riesgo_credito.analytics.transition import calculate_transition_matrix, calculate_roll_rates_matrix
    from credit_risk.models import CreditOperation
    from django.utils import timezone
    
    dates = list(CreditOperation.objects.values_list('load_date', flat=True).distinct().order_by('-load_date'))
    
    if len(dates) >= 2:
        date_t = dates[0]
        date_t_minus_1 = dates[1]
    elif len(dates) == 1:
        date_t = dates[0]
        date_t_minus_1 = dates[0] - timedelta(days=30)
    else:
        date_t = timezone.now().date()
        date_t_minus_1 = date_t - timedelta(days=30)
        
    # Construcción de filtros dinámicos
    filters = {}
    selected_asesor = request.GET.get('asesor', '')
    selected_producto = request.GET.get('producto', '')
    selected_tipo = request.GET.get('tipo_credito', '')
    selected_agencia = request.GET.get('agencia', '')
    
    if selected_asesor:
        filters['advisor'] = selected_asesor
    if selected_producto:
        filters['product_name'] = selected_producto
    if selected_tipo:
        filters['credit_type'] = selected_tipo
    if selected_agencia:
        filters['agency'] = selected_agencia

    matrix = calculate_transition_matrix(date_t_minus_1, date_t, filters=filters)
    roll_rates = calculate_roll_rates_matrix(date_t_minus_1, date_t, filters=filters)
    
    # Extraer opciones únicas para poblar los filtros en la vista
    # Consideramos el corte más reciente para mostrar las opciones vigentes
    opciones_qs = CreditOperation.objects.filter(load_date=date_t)
    opciones_asesores = list(opciones_qs.exclude(advisor__isnull=True).exclude(advisor='').values_list('advisor', flat=True).distinct().order_by('advisor'))
    opciones_productos = list(opciones_qs.exclude(product_name__isnull=True).exclude(product_name='').values_list('product_name', flat=True).distinct().order_by('product_name'))
    opciones_tipos = list(opciones_qs.exclude(credit_type__isnull=True).exclude(credit_type='').values_list('credit_type', flat=True).distinct().order_by('credit_type'))
    opciones_agencias = list(opciones_qs.exclude(agency__isnull=True).exclude(agency='').values_list('agency', flat=True).distinct().order_by('agency'))
    
    context = {
        'matrix': matrix,
        'roll_rates': roll_rates,
        'date_t': date_t,
        'date_t_minus_1': date_t_minus_1,
        # Opciones para el UI
        'asesores': opciones_asesores,
        'productos': opciones_productos,
        'tipos_credito': opciones_tipos,
        'agencias': opciones_agencias,
        # Seleccionados actualmente
        'sel_asesor': selected_asesor,
        'sel_producto': selected_producto,
        'sel_tipo': selected_tipo,
        'sel_agencia': selected_agencia,
    }
    return render(request, 'riesgo/transition_matrix.html', context)


@login_required
def stress_testing_view(request):
    """
    Simulador de Estrés. Muestra la Pérdida Esperada actual y permite recalcular 
    basado en shocks simulados via POST o AJAX.
    """
    from modulo_riesgo_credito.models import RiskClassification
    from django.db.models import Sum
    from decimal import Decimal
    
    cut_off = CreditOperation.objects.order_by('-load_date').first()
    cut_off_date = cut_off.load_date if cut_off else timezone.now().date()
    
    metrics = CreditOperation.objects.filter(load_date=cut_off_date).aggregate(
        total_ead=Sum('balance'),
        total_el=Sum('required_provision'),
        total_prov=Sum('required_provision')
    )
    
    base_el = metrics['total_el'] or Decimal('0.0')
    base_prov = metrics['total_prov'] or Decimal('0.0')
    
    # Extraemos la distribución por clasificación SBS
    sbs_names = {'0': '0 - Normal', '1': '1 - CPP', '2': '2 - Deficiente', '3': '3 - Dudoso', '4': '4 - Pérdida'}
    sbs_rates = {'0': Decimal('0.01'), '1': Decimal('0.05'), '2': Decimal('0.25'), '3': Decimal('0.60'), '4': Decimal('1.00')}
    
    portfolio_breakdown = []
    qs_sbs = CreditOperation.objects.filter(load_date=cut_off_date).values('sbs_classification').annotate(saldo=Sum('balance'))
    
    calc_el = Decimal('0.0')
    for item in qs_sbs:
        cls_id = str(item['sbs_classification'])
        rate = sbs_rates.get(cls_id, Decimal('0.05'))
        saldo = item['saldo'] or Decimal('0.0')
        el_item = saldo * rate
        
        portfolio_breakdown.append({
            'clasificacion': sbs_names.get(cls_id, f'Clasif. {cls_id}'),
            'saldo': saldo,
            'tasa': rate * 100,
            'provision_base': el_item
        })
        calc_el += el_item
        
    portfolio_breakdown = sorted(portfolio_breakdown, key=lambda x: x['clasificacion'])

    # Fallback si no hay data de provisiones en la BD, calculamos usando tasas SBS estándar
    if base_el == Decimal('0.0'):
        base_el = calc_el
        base_prov = calc_el
    
    # Si recibimos un shock
    shock_pd = Decimal(request.POST.get('shock_pd', '0')) / Decimal('100')
    shock_lgd = Decimal(request.POST.get('shock_lgd', '0')) / Decimal('100')
    
    simulated_el = base_el
    pd_mult = Decimal('1.0')
    lgd_mult = Decimal('1.0')
    total_mult = Decimal('1.0')
    
    if shock_pd > 0 or shock_lgd > 0:
        # Aproximación gruesa: Incrementamos EL base asumiendo promedios
        # En realidad deberíamos iterar cada crédito, pero para el prototipo usamos multiplicadores
        pd_mult = Decimal('1.0') + shock_pd
        lgd_mult = Decimal('1.0') + shock_lgd
        total_mult = pd_mult * lgd_mult
        simulated_el = base_el * total_mult
        
    context = {
        'base_el': base_el,
        'base_prov': base_prov,
        'simulated_el': simulated_el,
        'difference_el': simulated_el - base_el,
        'pd_mult': pd_mult,
        'lgd_mult': lgd_mult,
        'total_mult': total_mult,
        'shock_pd': request.POST.get('shock_pd', '0'),
        'shock_lgd': request.POST.get('shock_lgd', '0'),
        'portfolio_breakdown': portfolio_breakdown
    }
    
    return render(request, 'riesgo/stress_testing.html', context)

@login_required
def overriding_view(request):
    """
    Vista para que el comité de riesgos registre una reclasificación manual (Upgrade/Downgrade).
    """
    from modulo_riesgo_credito.models import OverridingLog, RiskClassification
    from django.contrib import messages
    
    if request.method == 'POST':
        operation_id = request.POST.get('operation_id')
        new_classification = request.POST.get('new_classification')
        justification = request.POST.get('justification')
        
        try:
            op = CreditOperation.objects.get(pk=operation_id)
            cut_off = CreditOperation.objects.order_by('-load_date').first().load_date
            
            # Buscar clasificacion actual
            current_class = RiskClassification.objects.filter(operation=op, cut_off_date=cut_off).first()
            old_class = current_class.sbs_classification if current_class else 'Desconocida'
            
            # Registrar
            OverridingLog.objects.create(
                operation=op,
                user=request.user,
                original_classification=old_class,
                new_classification=new_classification,
                justification=justification,
                cut_off_date=cut_off
            )
            
            # Aplicar
            if current_class:
                current_class.sbs_classification = new_classification
                # Aqui podríamos recalcular provisiones
                current_class.save()
                
            messages.success(request, f"Reclasificación aplicada a {op.operation_code} exitosamente.")
        except CreditOperation.DoesNotExist:
            messages.error(request, "Operación no encontrada.")
            
    # Listar últimos overridings
    logs = OverridingLog.objects.all().order_by('-date_applied')[:20]
    ops = CreditOperation.objects.all().order_by('-load_date')[:50] # Top 50 para el select
    
    return render(request, 'riesgo/overriding.html', {'logs': logs, 'operations': ops})

@login_required
def get_vintage_context(request):
    import json
    from django.db.models.functions import Coalesce, TruncMonth, ExtractYear, ExtractMonth
    from django.db.models import Value, CharField
    
    # Available cut-off dates
    dates = CreditOperation.objects.dates('load_date', 'day', order='DESC')
    selected_date = request.GET.get('load_date')
    
    if not selected_date and dates:
        selected_date = dates[0].strftime('%Y-%m-%d')
    
    if not selected_date:
        return {
            'page_title': 'Análisis de Cosechas',
            'error': 'No hay fechas de corte disponibles.',
            'dates': dates
        }
    
    # Available filters (unique values from the last 12 months for efficiency)
    filter_base_qs = CreditOperation.objects.filter(load_date=dates[0] if dates else None)
    products_list = sorted(list(filter_base_qs.values_list('product_name', flat=True).distinct()))
    agencies_list = sorted(list(filter_base_qs.values_list('agency', flat=True).distinct()))
    TCR_MAPPING = {
        '06': '06 - Créditos Corporativos',
        '07': '07 - Créditos a Grandes Empresas',
        '08': '08 - Créditos a Medianas Empresas',
        '09': '09 - Créditos a Pequeñas Empresas',
        '10': '10 - Créditos a Microempresas',
        '11': '11 - Créditos de Consumo revolventes',
        '12': '12 - Créditos de Consumo no revolventes',
        '13': '13 - Créditos Hipotecarios para vivienda',
        '20': '20 - Créditos a COOPAC'
    }
    types_list = sorted(list(filter_base_qs.values_list('credit_type', flat=True).distinct()))
    types_mapped = [(t, TCR_MAPPING.get(str(t).strip().zfill(2), t)) for t in types_list if t]
    advisors_list = sorted(list(filter_base_qs.values_list('advisor', flat=True).distinct()))

    # Get selected filter values
    sel_products = request.GET.getlist('product')
    sel_agencies = request.GET.getlist('agency')
    sel_types = request.GET.getlist('type')
    sel_advisors = request.GET.getlist('advisor')
    include_historical = request.GET.get('include_historical', 'on') == 'on'

    # Check cache first (include filters in key)
    filters_slug = f"p{','.join(sel_products)}_a{','.join(sel_agencies)}_t{','.join(sel_types)}_ad{','.join(sel_advisors)}_h{include_historical}"
    cache_key = f"vintage_analysis_{selected_date}_{filters_slug}"
    cached = cache.get(cache_key)
    if cached:
        cached['dates'] = dates
        return cached
    
    context = {
        'dates': dates,
        'selected_date': selected_date,
        'sel_products': sel_products,
        'sel_agencies': sel_agencies,
        'sel_types': sel_types,
        'sel_advisors': sel_advisors,
        'include_historical': include_historical,
        'filter_options': {
            'products': products_list, 'agencies': agencies_list, 
            'types': types_mapped, 'advisors': advisors_list
        }
    }
    
    selected_date_obj = datetime.strptime(selected_date, '%Y-%m-%d').date()
    start_date = selected_date_obj - pd.DateOffset(months=12)
    start_date = start_date.date() if hasattr(start_date, 'date') else start_date
    
    # =========================================================================
    # STEP 1: Build cohort lookup (SQL-level with Coalesce)
    # Only for operations whose cohort falls within the 12-month window
    # =========================================================================
    cohort_qs = CreditOperation.objects.values('operation_code').annotate(
        cohort_date=Coalesce(Max('disbursement_date'), Min('load_date'))
    )

    # Apply filters to cohort lookup
    if sel_products: cohort_qs = cohort_qs.filter(product_name__in=sel_products)
    if sel_agencies: cohort_qs = cohort_qs.filter(agency__in=sel_agencies)
    if sel_types: cohort_qs = cohort_qs.filter(credit_type__in=sel_types)
    if sel_advisors: cohort_qs = cohort_qs.filter(advisor__in=sel_advisors)

    # 1. Fetch ALL cohorts for the composition snapshot (include historical if selected)
    cohort_qs_all = cohort_qs.filter(cohort_date__lte=selected_date_obj)
    if not include_historical:
        cohort_qs_all = cohort_qs_all.filter(cohort_date__gte=start_date)
    
    # 2. Fetch filtered cohorts for the 12-month maturation window
    cohort_qs_window = cohort_qs_all.filter(cohort_date__gte=start_date)
    
    # Build a full map for composition snapshot
    cohort_map_full = {}
    for row in cohort_qs_all.iterator():
        cohort_map_full[row['operation_code']] = row['cohort_date']
    
    # Build a window map for maturation logic
    cohort_map_window = {}
    for row in cohort_qs_window.iterator():
        cohort_map_window[row['operation_code']] = row['cohort_date']
    
    if not cohort_map_full:
        return {
            'page_title': 'Análisis de Cosechas',
            'error': 'No hay cosechas en la ventana de 12 meses.',
            'dates': dates, 'selected_date': selected_date
        }
    
    # =========================================================================
    # STEP 2: Fetch ONLY relevant records (filtered by operation codes + dates)
    # Use only_fields to minimize memory
    # =========================================================================
    # Use subquery for operation_code filter to avoid SQLite's 999 variables limit
    relevant_ops_subquery = cohort_qs_all.values('operation_code')
    
    records_qs = CreditOperation.objects.filter(
        operation_code__in=relevant_ops_subquery,
        load_date__lte=selected_date_obj
    )

    # Re-apply filters to records (to ensure current snapshot matches criteria)
    if sel_products: records_qs = records_qs.filter(product_name__in=sel_products)
    if sel_agencies: records_qs = records_qs.filter(agency__in=sel_agencies)
    if sel_types: records_qs = records_qs.filter(credit_type__in=sel_types)
    if sel_advisors: records_qs = records_qs.filter(advisor__in=sel_advisors)

    records = records_qs.values_list(
        'operation_code', 'load_date', 'balance', 'days_past_due',
        'required_provision', 'original_amount', 'sbs_classification',
        named=True
    ).iterator(chunk_size=5000)
    
    # =========================================================================
    # STEP 3: Process in-memory with minimal footprint
    # Build aggregation dicts directly instead of DataFrames
    # =========================================================================
    
    # SBS normalization function (cached for performance)
    def normalize_sbs(val):
        if not val: return 'NORMAL'
        v = str(val).strip().upper()
        if 'PERDIDA' in v or 'PÉRDIDA' in v or 'PRDIDA' in v or v == '4': return 'PÉRDIDA'
        if 'CPP' in v or 'PROBLEMAS' in v or v == '1': return 'CPP'
        if 'DUDOSO' in v or v == '3': return 'DUDOSO'
        if 'DEFICIENTE' in v or v == '2': return 'DEFICIENTE'
        return 'NORMAL'
    
    sbs_cats_order = ['NORMAL', 'CPP', 'DEFICIENTE', 'DUDOSO', 'PÉRDIDA']
    sbs_days_labels = {
        'NORMAL': '<0 A 8>',
        'CPP': '<9 A 30>',
        'DEFICIENTE': '<31 A 60>',
        'DUDOSO': '<61 A 120>',
        'PÉRDIDA': '<121 A MAS>'
    }
    
    # Aggregation accumulators
    # For maturation: key=(cohort_month_str, age) -> {count, mora_8, mora_30, mora_60, mora_120, prov_sum, orig_sum}
    maturation = {}
    # For SBS composition: use ONLY the cutoff date snapshot to match portfolio totals
    # cutoff_snapshot stores: op_code -> (cohort_month, balance, sbs_cat) at the cutoff date
    cutoff_snapshot = {}
    
    for rec in records:
        op_code = rec.operation_code
        cohort_date = cohort_map_full.get(op_code)
        if not cohort_date:
            continue
            
        load_date = rec.load_date
        bal = float(rec.balance or 0)
        dpd = rec.days_past_due or 0
        
        # SBS composition: ONLY use records at the exact cutoff date
        # This covers ALL operations (historical + window)
        if load_date == selected_date_obj:
            age_for_comp = (load_date.year - cohort_date.year) * 12 + (load_date.month - cohort_date.month)
            if age_for_comp > 12:
                cohort_label = "HISTÓRICO (>12m)"
            else:
                cohort_label = f"{cohort_date.year}-{cohort_date.month:02d}"
            
            cutoff_snapshot[op_code] = (cohort_label, bal, normalize_sbs(rec.sbs_classification))

        # Maturation logic: ONLY for operations within the 12-month window
        if op_code in cohort_map_window:
            # Calculate age in months relative to cohort date
            age = (load_date.year - cohort_date.year) * 12 + (load_date.month - cohort_date.month)
            
            # For maturation curves, we only track the first 12 months of development
            if 0 <= age <= 12:
                cohort_month = f"{cohort_date.year}-{cohort_date.month:02d}"
                mat_key = (cohort_month, age)
                
                if mat_key not in maturation:
                    maturation[mat_key] = {
                        'count': 0, 'mora_8': 0, 'mora_30': 0, 'mora_60': 0, 'mora_120': 0,
                        'prov_sum': 0.0, 'orig_sum': 0.0
                    }
                m = maturation[mat_key]
                m['count'] += 1
                if dpd > 8: m['mora_8'] += 1
                if dpd > 30: m['mora_30'] += 1
                if dpd > 60: m['mora_60'] += 1
                if dpd > 120: m['mora_120'] += 1
                m['prov_sum'] += float(rec.required_provision or 0)
                m['orig_sum'] += float(rec.original_amount or 0)

        # Historical inclusion for maturation: Key for HISTÓRICO is ALWAYS at age 12 for comparative visibility
        if load_date == selected_date_obj and include_historical:
            age_for_comp = (load_date.year - cohort_date.year) * 12 + (load_date.month - cohort_date.month)
            if age_for_comp > 12:
                cohort_month = "HISTÓRICO (>12m)"
                mat_key = (cohort_month, 12) # Pin to max window for visibility in heatmap/curves
                
                if mat_key not in maturation:
                    maturation[mat_key] = {
                        'count': 0, 'mora_8': 0, 'mora_30': 0, 'mora_60': 0, 'mora_120': 0,
                        'prov_sum': 0.0, 'orig_sum': 0.0
                    }
                m = maturation[mat_key]
                m['count'] += 1
                if dpd > 8: m['mora_8'] += 1
                if dpd > 30: m['mora_30'] += 1
                if dpd > 60: m['mora_60'] += 1
                if dpd > 120: m['mora_120'] += 1
                m['prov_sum'] += float(rec.required_provision or 0)
                m['orig_sum'] += float(rec.original_amount or 0)
    
    # =========================================================================
    # SECTION 1: SBS Composition from cutoff date snapshot
    # This ensures totals match the portfolio dashboard (74M, not 87M)
    # =========================================================================
    sbs_comp_agg = {}  # cohort_month -> {cat -> saldo, 'total' -> saldo}
    
    for op_code, (cohort_month, bal, sbs_cat) in cutoff_snapshot.items():
        if cohort_month not in sbs_comp_agg:
            sbs_comp_agg[cohort_month] = {cat: 0.0 for cat in sbs_cats_order}
            sbs_comp_agg[cohort_month]['total'] = 0.0
        sbs_comp_agg[cohort_month][sbs_cat] += bal
        sbs_comp_agg[cohort_month]['total'] += bal
    
    # Sort months chronologically, but put 'HISTÓRICO' at the top if present
    cohort_months_sorted = sorted([m for m in sbs_comp_agg.keys() if m != 'HISTÓRICO (>12m)'])
    if 'HISTÓRICO (>12m)' in sbs_comp_agg:
        cohort_months_sorted = ['HISTÓRICO (>12m)'] + cohort_months_sorted
    sbs_composition = []
    grand_totals = {cat: {'saldo': 0.0, 'pct': 0.0} for cat in sbs_cats_order}
    grand_total_balance = 0.0
    
    for month in cohort_months_sorted:
        agg = sbs_comp_agg[month]
        total_bal = agg['total']
        grand_total_balance += total_bal
        
        row = {'month': month, 'total': total_bal, 'cats': {}}
        for cat in sbs_cats_order:
            saldo = agg[cat]
            pct = (saldo / total_bal * 100) if total_bal > 0 else 0
            row['cats'][cat] = {'saldo': saldo, 'pct': pct}
            grand_totals[cat]['saldo'] += saldo
        sbs_composition.append(row)
    
    for cat in sbs_cats_order:
        grand_totals[cat]['pct'] = (grand_totals[cat]['saldo'] / grand_total_balance * 100) if grand_total_balance > 0 else 0
    
    # =========================================================================
    # SECTION 2: Build maturation tables from aggregated data
    # =========================================================================
    thresholds = [
        {'key': '8', 'label': '> 8 días'},
        {'key': '30', 'label': '> 30 días'},
        {'key': '60', 'label': '> 60 días'},
        {'key': '120', 'label': '> 120 días'}
    ]
    
    # Collect all unique cohort months and ages
    all_cohort_months = [m for m in sorted(set(k[0] for k in maturation.keys() if k[0] != "HISTÓRICO (>12m)"), reverse=True)]
    if "HISTÓRICO (>12m)" in [k[0] for k in maturation.keys()]:
        all_cohort_months = ["HISTÓRICO (>12m)"] + all_cohort_months
    all_ages = sorted(set(k[1] for k in maturation.keys()))
    
    vintage_tables = []
    for t in thresholds:
        mora_key = f"mora_{t['key']}"
        
        # Build the pivot dict: {cohort_month -> {age -> mora_pct}}
        v_dict = {}
        for month in all_cohort_months:
            row = {}
            for age in all_ages:
                mat = maturation.get((month, age))
                if mat and mat['count'] > 0:
                    row[age] = round(mat[mora_key] / mat['count'] * 100, 4)
                else:
                    row[age] = None
            v_dict[month] = row
        
        vintage_tables.append({
            'label': t['label'],
            'key': t['key'],
            'data': v_dict,
            'json_data': json.dumps(v_dict)
        })
    
    # =========================================================================
    # SECTION 3: Expected Loss (EL) - lightweight
    # =========================================================================
    el_dict = {}
    for month in all_cohort_months:
        row = {}
        for age in all_ages:
            mat = maturation.get((month, age))
            if mat and mat['orig_sum'] > 0:
                row[age] = round(mat['prov_sum'] / mat['orig_sum'] * 100, 4)
            else:
                row[age] = None
        el_dict[month] = row
    
    context = {
        'page_title': 'Análisis de Cosechas (Vintages)',
        'vintage_tables': vintage_tables,
        'el_json_data': json.dumps(el_dict),
        'ages': all_ages,
        'dates': dates,
        'selected_date': selected_date,
        # SBS composition data
        'sbs_composition': sbs_composition,
        'sbs_cats_order': sbs_cats_order,
        'sbs_days_labels': sbs_days_labels,
        'sbs_grand_totals': grand_totals,
        'sbs_grand_total_balance': grand_total_balance,
        'sbs_composition_json': json.dumps([{
            'month': r['month'],
            'total': r['total'],
            'cats': {k: v['saldo'] for k, v in r['cats'].items()}
        } for r in sbs_composition]),
        # Filter context
        'filter_options': {
            'products': products_list, 'agencies': agencies_list, 
            'types': types_mapped, 'advisors': advisors_list
        },
        'sel_products': sel_products,
        'sel_agencies': sel_agencies,
        'sel_types': sel_types,
        'sel_advisors': sel_advisors,
    }
    
    # Cache for 30 minutes
    cache.set(cache_key, {k: v for k, v in context.items() if k != 'dates'}, 1800)
    return context

@login_required
def vintage_view(request):
    context = get_vintage_context(request)
    return render(request, 'riesgo/vintage.html', context)

