from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum

# Op Risk Models
from apps.op_risk.models import RiskEvent

# Market Risk Models
from apps.market_risk.models import MarketPosition, MarketTimeBand, MarketScenario, PositionType

# Credit Risk Models
from credit_risk.models import CreditOperation
from django.db.models import Q

@login_required
def home(request):
    # ==========================
    # 1. RIESGO OPERACIONAL
    # ==========================
    # 1. Indicadores de Riesgo Operacional
    total_incidents = RiskEvent.objects.count()
    open_incidents = RiskEvent.objects.exclude(date_discovered__isnull=True).count()
    total_losses = RiskEvent.objects.aggregate(Sum('amount'))['amount__sum'] or 0.00

    # ==========================
    # 2. RIESGO DE MERCADO
    # ==========================
    from apps.market_risk.views import _get_latest_market_data
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
        rate_impact = float(cumulative_gap) * (scen.rate_shock_bps / 10000.0)
        fx_impact = float(net_usd) * (float(scen.fx_shock_percent) / 100.0)
        total_impact = rate_impact + fx_impact
        if total_impact < worst_ear:
            worst_ear = total_impact
            
    # ==========================
    # 3. RIESGO DE CRÉDITO
    # ==========================
    # Calculate total balance and total NPL (Mora > 30 days)
    credit_agg = CreditOperation.objects.aggregate(
        total_balance=Sum('balance'),
        total_mora=Sum('balance', filter=Q(days_past_due__gt=30))
    )
    total_cartera = float(credit_agg['total_balance'] or 0)
    total_mora = float(credit_agg['total_mora'] or 0)
    npl_ratio = (total_mora / total_cartera * 100) if total_cartera > 0 else 0.0

    # Radar Chart Data (Scores out of 100 representing risk consumption)
    # These are illustrative formulas for the executive dashboard
    op_risk_score = min((open_incidents / max(total_incidents, 1)) * 100 + (float(total_losses) / 500000) * 50, 100)
    market_risk_score = min(abs(worst_ear) / 1000000 * 100, 100)
    liquidity_risk_score = 35 # Placeholder from Liquidity limits
    
    # Let's say an NPL ratio of 10% or more implies a 100% risk score
    credit_risk_score = min(npl_ratio * 10, 100)

    context = {
        # Op Risk
        'total_incidents': total_incidents,
        'open_incidents': open_incidents,
        'total_losses': total_losses,
        # Market Risk
        'cumulative_gap': abs(cumulative_gap),
        'net_usd': net_usd,
        'worst_ear': abs(worst_ear),
        # Credit Risk
        'total_cartera': total_cartera,
        'total_mora': total_mora,
        'npl_ratio': npl_ratio,
        # Radar Data
        'radar_data': [
            round(op_risk_score, 1), 
            round(market_risk_score, 1), 
            liquidity_risk_score, 
            credit_risk_score, 
            20 # Strategic Risk
        ]
    }
    return render(request, 'dashboards/home.html', context)
