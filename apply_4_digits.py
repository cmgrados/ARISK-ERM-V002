import os
import re
from liquidity_risk.models import LiqBalanceDetail
from django.db.models.functions import Length

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
    calc_type = 'HISTORICAL'
    trend_variable = None
    
    if code == '5104':
        calc_type = 'TREND'
        trend_variable = 'rendimiento_cartera'
    elif code.startswith('51') or code.startswith('52') or code.startswith('42'):
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

new_default = "DEFAULT_BUDGET_ITEMS = [\n" + "\n".join(items) + "\n]"

budget_engine_path = r'c:\Users\VICTUS\Desktop\A.RISK ERM - V2\apps\financial_planning\services\budget_engine.py'
with open(budget_engine_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace DEFAULT_BUDGET_ITEMS = [ ... ]
pattern = re.compile(r'DEFAULT_BUDGET_ITEMS\s*=\s*\[.*?\]', re.DOTALL)
new_content = pattern.sub(new_default, content)

with open(budget_engine_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Updated DEFAULT_BUDGET_ITEMS successfully.")

# Now clean up DB and reinitialize
from financial_planning.models import PlanFinanciero, BudgetItem, BudgetLine, BudgetCalculationRule
from financial_planning.services.budget_engine import BudgetEngine
from users.models import Organization, User

plan = PlanFinanciero.objects.first()
org = Organization.objects.first()
user = User.objects.first()

print("Deleting old BudgetItems, BudgetLines, BudgetCalculationRules...")
BudgetItem.objects.all().delete()
BudgetLine.objects.all().delete()
BudgetCalculationRule.objects.all().delete()

print("Reinitializing budget engine with new items...")
engine = BudgetEngine(plan, org, user)
engine._ensure_default_items()
engine.sync_with_trends()

print("Done!")
