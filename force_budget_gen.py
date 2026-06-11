import json
from django.db.models import Max
from apps.financial_planning.models import FinancialPlan
from apps.liquidity_risk.models import LiqBalanceDetail

plan = FinancialPlan.objects.get(id=8)
periods = plan.budget_data.get('selected_periods', [])
if not periods:
    print("No periods found in plan")

db_periods = LiqBalanceDetail.objects.values_list('period', flat=True).distinct()
period_map = {p.strftime('%Y-%m'): p for p in db_periods}

matching_dates = []
for p in periods:
    if p in period_map:
        matching_dates.append(period_map[p])

all_db_dates = {d.strftime('%Y-%m'): d for d in db_periods}

accounts_dict = {}
base_qs = LiqBalanceDetail.objects.filter(period__in=matching_dates)

all_accounts = base_qs.values('account_code').annotate(latest_name=Max('account_name'))

for row in all_accounts:
    code = (row['account_code'] or '').strip()
    if not code: continue
    accounts_dict[code] = {
        'code': code,
        'name': (row['latest_name'] or '').strip(),
        'balances': {p: 0.0 for p in periods},
        'children': [],
        'has_children': False,
        'parent_code': None,
        'has_discrepancy': False,
        'discrepancy': {p: 0.0 for p in periods},
    }

balances_by_date = {d: {} for d in matching_dates}
for row in base_qs.values('period', 'account_code', 'balance'):
    p_date = row['period']
    code = (row['account_code'] or '').strip()
    val = float(row['balance'] or 0.0)
    if code and code[0] in ('2', '3', '5'):
        val = -val
    balances_by_date[p_date][code] = val

for D, period_key in zip(matching_dates, periods):
    for code in accounts_dict.keys():
        accounts_dict[code]['balances'][period_key] = balances_by_date[D].get(code, 0.0)

for code in sorted(accounts_dict.keys()):
    for i in range(len(code) - 1, 0, -1):
        prefix = code[:i]
        if prefix in accounts_dict:
            accounts_dict[code]['parent_code'] = prefix
            accounts_dict[prefix]['children'].append(code)
            accounts_dict[prefix]['has_children'] = True
            break

for code, node in accounts_dict.items():
    if node['has_children']:
        for p in periods:
            children_sum = sum(accounts_dict[c]['balances'][p] for c in node['children'])
            diff = node['balances'][p] - children_sum
            node['discrepancy'][p] = diff
            if abs(diff) > 0.05:
                node['has_discrepancy'] = True

roots = sorted([n for n in accounts_dict.values() if not n['parent_code']], key=lambda x: x['code'])
balance_sheet, income_statement = [], []
for r in roots:
    (balance_sheet if r['code'][0] in ('1', '2', '3') else income_statement).append(r)

def has_movement(node):
    if any(abs(v) > 0.005 for v in node['balances'].values()):
        return True
    return any(has_movement(accounts_dict[c]) for c in node['children'])

def flatten_tree(nodes, depth=1):
    flat = []
    for n in sorted(nodes, key=lambda x: x['code']):
        if not has_movement(n):
            continue
        n_copy = dict(n)
        child_nodes = [accounts_dict[c] for c in n['children']]
        n_copy['children_codes'] = [c for c in n['children'] if has_movement(accounts_dict[c])]
        
        dummy_node = None
        if n_copy.get('has_discrepancy'):
            dummy_code = n['code'] + '99'
            while dummy_code in accounts_dict:
                dummy_code += '9'
            n_copy['children_codes'].append(dummy_code)
            dummy_node = {
                'code': dummy_code,
                'name': 'Saldos no asignados a subcuentas',
                'parent_code': n['code'],
                'children': [],
                'has_children': False,
                'balances': dict(n.get('discrepancy', {})),
                'monthly_balances': {},
                'has_discrepancy': False,
                'discrepancy': {},
                'children_codes': [],
                'depth': depth + 1,
                'level': len(dummy_code)
            }
            
        n_copy['depth'] = depth
        n_copy['level'] = len(n['code'])
        del n_copy['children']
        flat.append(n_copy)
        
        if child_nodes:
            flat.extend(flatten_tree(child_nodes, depth + 1))
            
        if dummy_node:
            flat.append(dummy_node)
    return flat

flat_bs = flatten_tree(balance_sheet)
flat_is = flatten_tree(income_statement)

plan.budget_data = {
    "selected_periods": periods,
    "balance_sheet": flat_bs,
    "income_statement": flat_is
}
plan.save()
print("Success! Assigned dummy nodes.")
