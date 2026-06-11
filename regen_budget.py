"""
Script para regenerar budget_data del plan financiero id=8
usando la nueva lógica de propagación bottom-up (sin nodos ficticios).
Ejecutar con: python manage.py shell < regen_budget.py
"""
import json
from apps.financial_planning.models import FinancialPlan
from apps.liquidity_risk.models import LiqBalanceDetail
from django.db.models import Max

plan = FinancialPlan.objects.get(id=8)

# Leer los períodos ya almacenados en budget_data
stored = plan.budget_data or {}
selected_periods = stored.get('selected_periods', [])
if not selected_periods:
    print("ERROR: No hay períodos en budget_data. Asigna primero desde el wizard.")
    exit()

print(f"Regenerando budget_data para plan '{plan.name}' con períodos: {selected_periods}")

# Obtener fechas reales
all_db_dates = {d.strftime('%Y-%m'): d for d in
                LiqBalanceDetail.objects.values_list('period', flat=True).distinct()}
matched_pairs = [(all_db_dates[p], p) for p in sorted(selected_periods) if p in all_db_dates]
if not matched_pairs:
    print("ERROR: Ningún período encontrado en la BD.")
    exit()

matching_dates, sel_periods = zip(*matched_pairs)
selected_periods = list(sel_periods)

# Construir accounts_dict
base_qs = LiqBalanceDetail.objects.filter(period__in=matching_dates)
all_accounts = base_qs.values('account_code').annotate(latest_name=Max('account_name'))

accounts_dict = {}
for row in all_accounts:
    code = (row['account_code'] or '').strip()
    if not code:
        continue
    accounts_dict[code] = {
        'code': code,
        'name': (row['latest_name'] or '').strip(),
        'balances': {p: 0.0 for p in selected_periods},
        'children': [],
        'has_children': False,
        'parent_code': None,
        'has_discrepancy': False,
        'discrepancy': {},
    }

# Llenar saldos
balances_by_date = {d: {} for d in matching_dates}
for row in base_qs.values('period', 'account_code', 'balance'):
    p_date = row['period']
    code = (row['account_code'] or '').strip()
    val = float(row['balance'] or 0.0)
    if code and code[0] in ('2', '3', '5'):
        val = -val
    balances_by_date[p_date][code] = val

for D, period_key in zip(matching_dates, selected_periods):
    for code in accounts_dict.keys():
        accounts_dict[code]['balances'][period_key] = balances_by_date[D].get(code, 0.0)

# Construir jerarquía
for code in sorted(accounts_dict.keys()):
    for i in range(len(code) - 1, 0, -1):
        prefix = code[:i]
        if prefix in accounts_dict:
            accounts_dict[code]['parent_code'] = prefix
            accounts_dict[prefix]['children'].append(code)
            accounts_dict[prefix]['has_children'] = True
            break

# Propagación bottom-up
def propagate_balance(code):
    node = accounts_dict[code]
    if not node['children']:
        return node['balances']
    for child_code in node['children']:
        propagate_balance(child_code)
    for p in selected_periods:
        children_sum = sum(accounts_dict[c]['balances'][p] for c in node['children'])
        if abs(node['balances'][p]) < 0.005:
            node['balances'][p] = children_sum
    return node['balances']

roots = sorted([n for n in accounts_dict.values() if not n['parent_code']], key=lambda x: x['code'])
for root in roots:
    propagate_balance(root['code'])

# Limpiar discrepancias (no más nodos ficticios)
for code, node in accounts_dict.items():
    node['has_discrepancy'] = False
    node['discrepancy'] = {}

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
        n_copy['depth'] = depth
        n_copy['level'] = len(n['code'])
        del n_copy['children']
        flat.append(n_copy)
        if child_nodes:
            flat.extend(flatten_tree(child_nodes, depth + 1))
    return flat

flat_bs = flatten_tree(balance_sheet)
flat_is = flatten_tree(income_statement)

plan.budget_data = {
    "selected_periods": selected_periods,
    "balance_sheet": flat_bs,
    "income_statement": flat_is
}
plan.save()

# Verificar cuenta 410103
is_nodes = [n for n in flat_is if n['code'].startswith('410103')]
print(f"\nCuentas 410103 en income_statement regenerado: {len(is_nodes)}")
for n in is_nodes:
    saldo_2023 = n['balances'].get('2023-12', 0)
    saldo_2024 = n['balances'].get('2024-12', 0)
    print(f"  {n['code']} | {n['name'][:45]} | 2023-12: {saldo_2023:>14.2f} | 2024-12: {saldo_2024:>14.2f}")

# Verificar que no hay nodos ficticios
dummy_nodes = [n for n in flat_is + flat_bs if 'Saldos no asignados' in n.get('name', '')]
print(f"\nNodos ficticios en el resultado: {len(dummy_nodes)}")
print("✅ Budget data regenerado correctamente.")
