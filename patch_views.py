import re
import os

file_path = r'c:\Users\VICTUS\Desktop\A.RISK ERM - V2\apps\financial_planning\views.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the duplicated definitions from my previous work (lines 192-270)
# We will just redefine the actual ones at the bottom correctly.
# Find the start of the first def api_historical_portfolio_data and remove it up to def api_save_trend_scenarios

pattern = r"def api_historical_portfolio_data\(request, plan_id=None\):.*?return JsonResponse\(\{.*?\}\)\n\n"
content = re.sub(pattern, "", content, count=1, flags=re.DOTALL)

# Now redefine the proper ones where the dummy ones are:
# We will use string replacement for the dummy functions

# dummy 1
dummy_historical_portfolio = """@login_required
def api_historical_portfolio_data(request, plan_id=None):
    return JsonResponse({'status': 'success', 'msg': 'Endpoint en construccion: api_historical_portfolio_data'})"""

proper_historical_portfolio = """@login_required
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
        monto_desemb=Sum('original_amount', filter=Q(disbursement_date__year=F('load_date__year'), disbursement_date__month=F('load_date__month')))
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
        
        if ag not in data_map:
            data_map[ag] = {}
            
        if ld not in data_map[ag]:
            data_map[ag][ld] = {
                'period': period_str,
                'advisors': overall_map.get(ld, {}).get(ag, {}).get('nro_analistas', 0),
                'types': {},
                'cartera_vencida': 0 # Optional, add logic if needed
            }
            
        if ct not in data_map[ag][ld]['types']:
            data_map[ag][ld]['types'][ct] = {
                'nro_des': 0,
                'mto_des': 0,
                'nro_car': 0,
                'sld_car': 0,
                'cob_est': 0
            }
            
        t_data = data_map[ag][ld]['types'][ct]
        t_data['nro_des'] += row['num_desemb'] or 0
        t_data['mto_des'] += float(row['monto_desemb'] or 0)
        t_data['nro_car'] += row['total_ops'] or 0
        t_data['sld_car'] += float(row['saldo'] or 0)
        
    # Convert data_map inner dicts to lists
    final_data = {}
    for ag, periods_dict in data_map.items():
        # Sort by load_date descending or ascending based on requirements
        final_data[ag] = [periods_dict[ld] for ld in sorted(periods_dict.keys())]

    return JsonResponse({
        'status': 'success',
        'data': final_data
    })"""

content = content.replace(dummy_historical_portfolio, proper_historical_portfolio)

# dummy 2
dummy_available_portfolio_dates = """@login_required
def api_available_portfolio_dates(request, plan_id=None):
    return JsonResponse({'status': 'success', 'msg': 'Endpoint en construccion: api_available_portfolio_dates'})"""

proper_available_portfolio_dates = """@login_required
def api_available_portfolio_dates(request, plan_id=None):
    from credit_risk.models import CreditOperation
    from django.http import JsonResponse
    dates = CreditOperation.objects.values_list('load_date', flat=True).distinct().order_by('-load_date')
    dates_str = [d.strftime('%Y-%m') for d in dates if d]
    return JsonResponse({'status': 'success', 'data': dates_str})"""

content = content.replace(dummy_available_portfolio_dates, proper_available_portfolio_dates)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
