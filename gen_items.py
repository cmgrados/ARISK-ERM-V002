from liquidity_risk.models import LiqBalanceDetail
from django.db.models.functions import Length
import json

def get_category(code):
    if code.startswith('51'): return 'ING_FIN'
    if code.startswith('52'): return 'ING_SERV'
    if code.startswith('5'): return 'OTROS_ING'
    if code.startswith('41'): return 'GAS_FIN'
    if code.startswith('42'): return 'GAS_SERV'
    if code.startswith('43'): return 'PROV'
    if code.startswith('44'): return 'DEP_AMORT'
    if code.startswith('45'): return 'GAS_ADMIN'
    return 'OTROS_EG'

def get_defaults(code):
    calc_type = 'MANUAL'
    trend_variable = None
    
    if code.startswith('51') or code.startswith('52') or code.startswith('42'):
        calc_type = 'TREND'
        trend_variable = 'cartera'
    elif code.startswith('41'):
        calc_type = 'TREND'
        trend_variable = 'dpf'
    elif code.startswith('43'):
        calc_type = 'TREND'
        trend_variable = 'mora_soles'
    elif code == '4501' or code == '4505':
        calc_type = 'TREND'
        trend_variable = 'socios'
    elif code == '4503':
        calc_type = 'TREND'
        trend_variable = 'cartera'
        
    return calc_type, trend_variable

qs = LiqBalanceDetail.objects.annotate(l=Length('account_code')).filter(l=4).filter(
    account_code__startswith='4'
) | LiqBalanceDetail.objects.annotate(l=Length('account_code')).filter(l=4).filter(
    account_code__startswith='5'
)
qs = qs.values_list('account_code', 'account_name').distinct().order_by('account_code')

items = []
for code, name in qs:
    cat = get_category(code)
    calc, var = get_defaults(code)
    # clean name
    name = name.title().replace(' Y ', ' y ').replace(' De ', ' de ').replace(' Por ', ' por ').replace(' En ', ' en ')
    
    item = f"""    {{
        'code': 'ACC_{code}',
        'name': '{name}',
        'category': '{cat}',
        'account_prefix': '{code}',
        'calc_type': '{calc}',
        'trend_variable': {'"'+var+'"' if var else 'None'},
    }},"""
    items.append(item)

print("DEFAULT_BUDGET_ITEMS = [")
print("\n".join(items))
print("]")
