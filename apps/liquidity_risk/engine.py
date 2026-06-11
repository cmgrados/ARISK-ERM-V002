from decimal import Decimal
from django.db.models import Sum, Count, F, Q, StdDev, Avg
from django.utils import timezone
from .models import (
    LiqBalanceUpload, LiqBalanceDetail, LiqAccountMapping,
    LiqLiabilityDetail, LiqLiabilityUpload, # Unificado
    LiqFundingLine, LiqInvestment,
    LiqSbsLimit, LiqAlert, LiqContingencyActivation
)
from credit_risk.models import CreditOperation

def get_latest_period():
    latest = LiqBalanceUpload.objects.filter(status='SUCCESS').order_by('-period').first()
    return latest.period if latest else timezone.now().date()

def calculate_liquidity_metrics(period):
    """
    Calculates executive indicators using optimized single-query aggregation.
    """
    # Combined aggregation for all balance items - Filter by 2-digit codes to avoid double counting totals/subaccounts
    balance_metrics = LiqBalanceDetail.objects.filter(
        period=period, 
        account_code__regex=r'^\d{2}$'
    ).aggregate(
        assets_mn=Sum('balance', filter=Q(currency='MN', liquidity_item__icontains='DISPONIBLE')),
        assets_me=Sum('balance', filter=Q(currency='ME', liquidity_item__icontains='DISPONIBLE')),
        liab_mn=Sum('balance', filter=Q(currency='MN', liquidity_item__regex=r'DEPOSITOS|OBLIGACIONES')),
        liab_me=Sum('balance', filter=Q(currency='ME', liquidity_item__regex=r'DEPOSITOS|OBLIGACIONES'))
    )
    
    liquid_assets_mn = abs(balance_metrics['assets_mn'] or Decimal('0'))
    liquid_assets_me = abs(balance_metrics['assets_me'] or Decimal('0'))
    st_liabilities_mn = abs(balance_metrics['liab_mn'] or Decimal('1'))
    st_liabilities_me = abs(balance_metrics['liab_me'] or Decimal('1'))
    
    # Calculate totals efficiently using unified model
    liab_qs = LiqLiabilityDetail.objects.filter(period=period)
    total_savings = liab_qs.filter(funding_type='AHORRO').aggregate(s=Sum('balance'))['s'] or Decimal('0')
    total_dpf = liab_qs.filter(funding_type='PLAZO').aggregate(s=Sum('balance'))['s'] or Decimal('0')
    total_deposits = total_savings + total_dpf
    
    # Concentration (Unified)
    savings_totals = list(liab_qs.filter(funding_type='AHORRO')
                         .values('customer_id')
                         .annotate(total=Sum('balance'))
                         .order_by('-total')[:20])
    
    top_10_val = sum([x['total'] for x in savings_totals[:10]])
    top_20_val = sum([x['total'] for x in savings_totals[:20]])
    
    top_10_pct = (top_10_val / total_deposits * 100) if total_deposits > 0 else Decimal('0')
    top_20_pct = (top_20_val / total_deposits * 100) if total_deposits > 0 else Decimal('0')
    
    # Gaps from real data (Contractual MN)
    matrix_mn = generate_maturity_gap(period, 'MN')
    gap_30 = matrix_mn['gaps_accumulated'][0] if matrix_mn.get('gaps_accumulated') else Decimal('0')
    gap_90 = matrix_mn['gaps_accumulated'][2] if len(matrix_mn.get('gaps_accumulated', [])) > 2 else Decimal('0')

    # Combined stats for others
    other_stats = {
        'available_lines': LiqFundingLine.objects.filter(period=period).aggregate(Sum('available_amount'))['available_amount__sum'] or Decimal('0'),
        'alerts_count': LiqAlert.objects.filter(period=period).count(),
        'contingency_active': LiqContingencyActivation.objects.filter(status='OPEN').exists()
    }
    
    return {
        'period': period,
        'mn_index': (liquid_assets_mn / abs(st_liabilities_mn) * 100).quantize(Decimal('0.01')) if st_liabilities_mn else Decimal('0'),
        'me_index': (liquid_assets_me / abs(st_liabilities_me) * 100).quantize(Decimal('0.01')) if st_liabilities_me else Decimal('0'),
        'liquid_assets': liquid_assets_mn + liquid_assets_me,
        'short_term_liabilities': abs(st_liabilities_mn) + abs(st_liabilities_me),
        'gap_30': gap_30,
        'gap_90': gap_90,
        'top_10_depositors': top_10_pct.quantize(Decimal('0.01')),
        'top_20_depositors': top_20_pct.quantize(Decimal('0.01')),
        'available_lines': other_stats['available_lines'],
        'alerts_active': other_stats['alerts_count'],
        'contingency_status': 'ACTIVADO' if other_stats['contingency_active'] else 'NORMAL',
        'process_status': 'COMPLETO' if balance_metrics['assets_mn'] is not None else 'PENDIENTE'
    }

def calculate_lar(period, currency='MN', segment=None, products=None, confidence=0.95, historical_depth=12):
    """
    Calculates the volatile balance (LaR) based on historical variation.
    Returns a dictionary with metrics.
    """
    from .models import LiqLiabilityDetail, LiqLaRResult
    from scipy.stats import norm
    import pandas as pd
    import numpy as np

    # 1. Fetch Historical Series
    q = Q(currency=currency)
    if segment and segment != 'TODOS':
        q &= Q(liquidity_item=segment)
    
    if products:
        if isinstance(products, str):
            products = [products]
        q &= Q(product__in=products)
    
    # We look back 'historical_depth' months
    from dateutil.relativedelta import relativedelta
    start_date = period - relativedelta(months=historical_depth)
    
    series_qs = LiqLiabilityDetail.objects.filter(q, period__gte=start_date, period__lte=period)\
        .values('period')\
        .annotate(balance=Sum('balance'))\
        .order_by('period')
    
    if series_qs.count() < 2:
        return None # Not enough data for variation
    
    df = pd.DataFrame(list(series_qs))
    df['balance'] = df['balance'].astype(float)
    df['variation'] = df['balance'].diff()
    df_clean = df.dropna()
    
    if df_clean.empty:
        return None

    # Calculate percentage variations for better scale-invariance in growing portfolios
    df['pct_variation'] = df['balance'].pct_change()
    df_clean_pct = df.dropna(subset=['pct_variation'])
    
    if len(df_clean_pct) < 2:
        return None

    mean_pct = float(df_clean_pct['pct_variation'].mean())
    std_dev_pct = float(df_clean_pct['pct_variation'].std())
    
    # Z-score for confidence (e.g. 1.645 for 95%)
    z_score = float(norm.ppf(float(confidence)))
    
    current_balance = Decimal(str(df['balance'].iloc[-1]))
    
    # Saldo Volátil (LaR) = Volatilidad % * Saldo Actual * Z
    # We use the std_dev of percentages to get the relative risk
    lar_amount = Decimal(str(float(current_balance) * std_dev_pct * z_score))
    lar_pct = Decimal(str(std_dev_pct * z_score * 100))
    
    # Balance Projections (Trend-Adjusted Stable Balance)
    # Proj(T) = Balance * (1 + (Mean_Pct * T) - (Std_Pct * Z * sqrt(T)))
    projections = []
    target_months = [1, 2, 3, 4, 5, 6, 9, 12, 24, 60, 120]
    labels = {
        1: '1 Mes', 2: '2 Meses', 3: '3 Meses', 4: '4 Meses', 5: '5 Meses', 6: '6 Meses',
        9: '7-9 Meses', 12: '10-12 Meses', 24: '1-2 Años', 60: '2-5 Años', 120: '> 5 Años'
    }
    
    # 2. Contractual Maturities for the current period (Comparison)
    current_liabilities = LiqLiabilityDetail.objects.filter(q, period=period)
    mat_bands = {t: 0.0 for t in target_months}
    
    for liab in current_liabilities:
        m = 0
        if liab.due_date:
            # Months between period and due_date
            m = (liab.due_date.year - period.year) * 12 + liab.due_date.month - period.month
            m = max(0, m)
        else:
            m = 0 # No due_date -> Vista/Ahorro (Band 1)
            
        for t in target_months:
            if m <= t:
                mat_bands[t] += float(liab.balance)
                break
        else:
            # If greater than 120 months
            mat_bands[120] += float(liab.balance)

    cumulative_mat = 0.0
    for t in target_months:
        # Expected growth + unexpected withdrawal risk
        # Note: We cap growth at current balance if we want to measure "retention" of CURRENT funds, 
        # but usually in Gap Analysis we want the projected balance.
        # However, to be conservative, we can use: 
        # Net_Stability_Factor = (1 + (mean_pct * t) - (std_dev_pct * z_score * np.sqrt(t)))
        
        net_factor = 1.0 + (mean_pct * t) - (std_dev_pct * z_score * np.sqrt(t))
        rem_bal = max(0, float(current_balance) * net_factor)
        
        # Volatility in amount for this specific T
        vol_t = float(current_balance) * (std_dev_pct * z_score * np.sqrt(t))
        
        # Contractual comparison
        cumulative_mat += mat_bands.get(t, 0.0)
        rem_contractual = max(0, float(current_balance) - cumulative_mat)
        
        projections.append({
            'month': t,
            'label': labels.get(t, f"{t} Meses"),
            'volatility': vol_t,
            'remaining_balance': rem_bal,
            'retention_pct': (rem_bal / float(current_balance) * 100) if current_balance > 0 else 0,
            'contractual_discrete': mat_bands.get(t, 0.0),
            'contractual_remaining': rem_contractual
        })

    return {
        'total_balance': current_balance,
        'lar_amount': lar_amount,
        'lar_percentage': lar_pct,
        'std_dev': Decimal(str(std_dev_pct * float(current_balance))), # Absolute std dev for UI
        'std_dev_day': Decimal(str((std_dev_pct * float(current_balance)) / np.sqrt(30))),
        'avg_variation': Decimal(str(df_clean['variation'].mean())),
        'projections': projections,
        'history': df.fillna(0).to_dict('records')
    }

def generate_interpretative_analysis(lar_data, currency):
    total = float(lar_data['total_balance'])
    lar = float(lar_data['lar_amount'])
    pct = float(lar_data['lar_percentage'])
    avg_var = float(lar_data.get('avg_variation', 0))
    std_dev = float(lar_data['std_dev'])
    
    projections = lar_data.get('projections', [])
    # Find the specific 12-month projection for resilience analysis
    retention_12m = next((p['retention_pct'] for p in projections if p['month'] == 12), 0)
    
    analysis = []
    
    # 1. Magnitud del Saldo Volátil (Nivel de Riesgo)
    if pct < 5:
        risk_level = "Bajo"
        risk_color = "success"
        desc = "Estructura de fondeo altamente estable. La base de depósitos muestra una baja sensibilidad a retiros masivos inesperados."
    elif pct < 15:
        risk_level = "Moderado"
        risk_color = "warning"
        desc = "Exposición moderada a la volatilidad. Se observa una base mixta de depositantes que requiere un colchón de liquidez prudencial."
    else:
        risk_level = "Significativo"
        risk_color = "danger"
        desc = "Alta dependencia de saldos volátiles. Existe riesgo de salidas abruptas que podrían presionar los ratios de liquidez regulatorios."
        
    analysis.append({
        'title': 'Nivel de Riesgo',
        'value': f"{risk_level} ({pct:.2f}%)",
        'text': desc,
        'color': risk_color,
        'icon': 'fa-shield-alt'
    })
    
    # 2. Tendencia y Estabilidad
    if avg_var > 0:
        trend = "Creciente"
        trend_text = f"La captación neta es positiva (promedio {currency} {abs(avg_var):,.0f}/mes), lo que fortalece la posición de liquidez estructural."
        trend_color = "success"
    else:
        trend = "Salida Neta"
        trend_text = f"Se observa una desintermediación promedio de {currency} {abs(avg_var):,.0f} mensual. Requiere revisar estrategias de captación."
        trend_color = "danger"
        
    analysis.append({
        'title': 'Tendencia',
        'value': trend,
        'text': trend_text,
        'color': trend_color,
        'icon': 'fa-chart-line'
    })
    
    # 3. Volatilidad Extrema (Stress Test)
    peak_vol = std_dev * 1.645 # 95% confidence
    analysis.append({
        'title': 'Variación Máxima (95%)',
        'value': f"{currency} {peak_vol:,.0f}",
        'text': f"Existe un 5% de probabilidad de que en un solo mes el saldo disminuya más de {currency} {peak_vol:,.0f} por comportamiento del mercado.",
        'color': 'warning',
        'icon': 'fa-exclamation-triangle'
    })
    
    # 4. Resiliencia a 12 meses
    analysis.append({
        'title': 'Resiliencia (12M)',
        'value': f"{retention_12m:.1f}%",
        'text': f"Bajo un escenario de retiro sostenido, se estima que el {retention_12m:.1f}% del saldo actual se mantendrá estable tras un año de operaciones.",
        'color': 'info',
        'icon': 'fa-anchor'
    })
    
    # 5. Cobertura Sugerida
    suggested_buffer = lar * 1.1 # 10% safety margin
    analysis.append({
        'title': 'Cobertura Sugerida',
        'value': f"{currency} {suggested_buffer:,.0f}",
        'text': f"Se recomienda mantener un fondo de reserva de al menos {currency} {suggested_buffer:,.0f} para cubrir la volatilidad esperada con un margen del 10%.",
        'color': 'dark',
        'icon': 'fa-piggy-bank'
    })
    
    return analysis


def generate_maturity_gap(period, currency='MN'):
    """
    Constructs the maturity gap matrix using rows for items and columns for bands.
    Aligned with the regulatory horizontal structure.
    """
    from .models import LiqTimeBand, LiqBalanceDetail, LiqLiabilityDetail
    from credit_risk.models import CreditOperation
    from decimal import Decimal
    from django.db.models import Sum

    bands = list(LiqTimeBand.objects.all().order_by('order'))
    if not bands:
        return {}

    credit_currency = 'PEN' if currency == 'MN' else 'USD'
    
    # 1. Fetch Raw Data
    credits = CreditOperation.objects.filter(load_date=period, currency=credit_currency)
    liabilities = LiqLiabilityDetail.objects.filter(period=period, currency=currency)
    balance = LiqBalanceDetail.objects.filter(period=period, currency=currency)

    # 2. Define Asset Rows
    asset_rows = [
        {'name': 'Disponible', 'codes': ['11'], 'type': 'BALANCE'},
        {'name': 'Créditos - deudores no minoristas', 'type': 'CREDIT', 'tag': 'NO_MINORISTA'},
        {'name': 'Créditos - pequeñas empresas y micro-empresas', 'type': 'CREDIT', 'tag': 'PYME'},
        {'name': 'Créditos - hipotecarios para vivienda', 'type': 'CREDIT', 'tag': 'HIPOTECARIO'},
        {'name': 'Créditos - consumo', 'type': 'CREDIT', 'tag': 'CONSUMO'},
        {'name': 'Cuentas por cobrar - otros', 'codes': ['15'], 'type': 'BALANCE'},
    ]

    # 3. Define Liability Rows
    liab_rows = [
        {'name': 'Obligaciones por cuentas de ahorro', 'type': 'SAVINGS'},
        {'name': 'Obligaciones por cuentas a plazo', 'type': 'DPF'},
        {'name': 'Depósitos de empresas del sistema financiero', 'codes': ['23'], 'type': 'BALANCE'},
        {'name': 'Adeudados y obligaciones financieras del país', 'codes': ['24'], 'type': 'BALANCE'},
        {'name': 'Adeudados y obligaciones financieras del exterior', 'codes': ['26'], 'type': 'BALANCE'},
        {'name': 'Cuentas por pagar - otros', 'codes': ['25'], 'type': 'BALANCE'},
    ]
    
    # 4. Pre-calculate Flows per Band for all categories
    asset_band_flows = {r['name']: [Decimal('0')] * len(bands) for r in asset_rows}
    liab_band_flows = {r['name']: [Decimal('0')] * len(bands) for r in liab_rows}
    
    # 4a. Credit Amortization Flows (Assets)
    credit_tag_map = {
        'NO_MINORISTA': 'Créditos - deudores no minoristas',
        'PYME': 'Créditos - pequeñas empresas y micro-empresas',
        'HIPOTECARIO': 'Créditos - hipotecarios para vivienda',
        'CONSUMO': 'Créditos - consumo'
    }
    
    for c in credits:
        tag = 'NO_MINORISTA'
        ctype = (c.credit_type or '').upper()
        if 'HIPO' in ctype: tag = 'HIPOTECARIO'
        elif 'CONS' in ctype: tag = 'CONSUMO'
        elif 'PYME' in ctype or 'MICRO' in ctype or 'PEQUE' in ctype or 'MES' in ctype: tag = 'PYME'
        
        row_name = credit_tag_map[tag]
        
        if c.disbursement_date and c.term:
            n = (c.disbursement_date.year - period.year) * 12 + c.disbursement_date.month - period.month + c.term
        elif c.maturity_date:
            n = (c.maturity_date.year - period.year) * 12 + c.maturity_date.month - period.month
        else:
            n = 0
            
        if n <= 0:
            asset_band_flows[row_name][0] += c.balance
        else:
            tea = Decimal(str(c.rate)) / 100
            tem = Decimal(str((1 + float(tea))**(1/12) - 1))
            if tem > 0:
                pmt = c.balance * (tem / (1 - (1+tem)**(-n)))
            else:
                pmt = c.balance / n
            
            curr_bal = c.balance
            for m in range(n):
                interest = curr_bal * tem
                capital = pmt - interest
                if m == n - 1 or capital > curr_bal: capital = curr_bal
                
                d_until = (m + 1) * 30
                for idx, b in enumerate(bands):
                    if b.start_days <= d_until <= b.end_days:
                        asset_band_flows[row_name][idx] += capital
                        break
                else:
                    asset_band_flows[row_name][-1] += capital
                
                curr_bal -= capital
                if curr_bal <= 0.01: break

    # 4b. Unified Liability Flows (Savings & DPF)
    from .models import LiqLaRResult
    
    # Savings (Volatility Methodology)
    # Prefer results marked as official, otherwise take the most recent for that segment
    lar_res = LiqLaRResult.objects.filter(period=period, currency=currency, is_official=True).first()
    if not lar_res:
        lar_res = LiqLaRResult.objects.filter(period=period, currency=currency).order_by('-executed_at').first()
        
    savings_details = liabilities.filter(funding_type='AHORRO')
    
    # Pre-calculate marginal percentages if LaR result is available
    marginal_dist = []
    if lar_res and 'projections' in lar_res.calculation_data:
        projections = lar_res.calculation_data['projections']
        prev_retention = 100.0
        for proj in projections:
            # Force conservative monotonic decrease: retention can never go up
            curr_retention = min(prev_retention, float(proj['retention_pct']))
            # The outflow for this band is the difference
            marginal_outflow = prev_retention - curr_retention
            marginal_dist.append(Decimal(str(marginal_outflow / 100.0)))
            prev_retention = curr_retention
            
        # The remaining 'prev_retention' is the core stable balance that never leaves.
        # We assign 100% of this stable balance to the final maturity band (> 5 años).
        if marginal_dist:
            marginal_dist[-1] += Decimal(str(prev_retention / 100.0))
    else:
        # Default fallback distribution (20% volatile, rest distributed)
        marginal_dist = [Decimal('0.20'), Decimal('0.10'), Decimal('0.10'), Decimal('0.10'), Decimal('0.10'), Decimal('0.10'), Decimal('0.15'), Decimal('0.15')]

    for s in savings_details:
        val = s.balance or Decimal('0')
        if val <= 0: continue
        
        for i, p in enumerate(marginal_dist):
            if i < len(bands):
                liab_band_flows['Obligaciones por cuentas de ahorro'][i] += (val * p)
            else:
                # Accumulate in the last available band if projections are longer than bands
                liab_band_flows['Obligaciones por cuentas de ahorro'][-1] += (val * p)

    # DPF (Maturity Analysis - using pre-calculated band)
    term_details = liabilities.filter(funding_type='PLAZO')
    band_name_to_idx = {b.name: i for i, b in enumerate(bands)}
    
    for d in term_details:
        val = d.balance or Decimal('0')
        if val <= 0: continue
        
        idx = band_name_to_idx.get(d.liquidity_band, 0)
        liab_band_flows['Obligaciones por cuentas a plazo'][idx] += val

    # 4d. Balance Items (Assets & Liabilities)
    for r in asset_rows:
        if r['type'] == 'BALANCE':
            # Balance items usually go to the first band (Disponible, etc.)
            for code in r['codes']:
                # Try exact match first (total account), fallback to summing children if not found
                val = balance.filter(account_code=code).aggregate(s=Sum('balance'))['s']
                if val is None:
                    # Sum only sub-accounts of the same length + 2 to avoid multi-level double counting if possible
                    # or just sum all if it's a granular balance. 
                    # For safety in varied trial balances, we sum all starting with code
                    val = balance.filter(account_code__startswith=code).aggregate(s=Sum('balance'))['s'] or Decimal('0')
                asset_band_flows[r['name']][0] += abs(val)

    for r in liab_rows:
        if r['type'] == 'BALANCE':
            for code in r['codes']:
                val = balance.filter(account_code=code).aggregate(s=Sum('balance'))['s']
                if val is None:
                    val = balance.filter(account_code__startswith=code).aggregate(s=Sum('balance'))['s'] or Decimal('0')
                liab_band_flows[r['name']][0] += abs(val)

    # 5. Build Matrix
    matrix = {
        'bands': [b.name for b in bands],
        'assets': [],
        'liabilities': [],
        'totals_in': [Decimal('0')] * len(bands),
        'totals_out': [Decimal('0')] * len(bands),
        'gaps_marginal': [],
        'gaps_accumulated': []
    }

    for r in asset_rows:
        flows = asset_band_flows[r['name']]
        matrix['assets'].append({'name': r['name'], 'values': flows, 'total': sum(flows)})
        for i, v in enumerate(flows): matrix['totals_in'][i] += v

    for r in liab_rows:
        flows = liab_band_flows[r['name']]
        matrix['liabilities'].append({'name': r['name'], 'values': flows, 'total': sum(flows)})
        for i, v in enumerate(flows): matrix['totals_out'][i] += v

    matrix['total_assets'] = sum(matrix['totals_in'])
    matrix['total_liab'] = sum(matrix['totals_out'])

    # Gaps
    acc = Decimal('0')
    for i in range(len(bands)):
        marginal = matrix['totals_in'][i] - matrix['totals_out'][i]
        acc += marginal
        matrix['gaps_marginal'].append(marginal)
        matrix['gaps_accumulated'].append(acc)

    return matrix
