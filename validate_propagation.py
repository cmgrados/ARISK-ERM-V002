"""
Simula el proceso assign_institutional_budget_to_plan para el plan 8
y verifica que no haya nodos duplicados ni saldos negativos incorrectos.
"""
import sqlite3

conn = sqlite3.connect('db.sqlite3')
cur = conn.cursor()

# Simular los períodos seleccionados: dic-2023 y dic-2024
selected_periods = ['2023-12', '2024-12']
matching_dates_str = ['2023-12-31', '2024-12-31']

# Construir accounts_dict
rows = cur.execute(
    "SELECT account_code, MAX(account_name) FROM liquidity_risk_liqbalancedetail "
    "WHERE period IN ('2023-12-31', '2024-12-31') GROUP BY account_code ORDER BY account_code"
).fetchall()

accounts_dict = {}
for code, name in rows:
    code = (code or '').strip()
    if not code:
        continue
    accounts_dict[code] = {
        'code': code,
        'name': (name or '').strip(),
        'balances': {p: 0.0 for p in selected_periods},
        'children': [],
        'has_children': False,
        'parent_code': None,
    }

# Llenar saldos
for date_str, period_key in zip(matching_dates_str, selected_periods):
    rows2 = cur.execute(
        "SELECT account_code, SUM(balance) FROM liquidity_risk_liqbalancedetail "
        "WHERE period = ? GROUP BY account_code", (date_str,)
    ).fetchall()
    for code, bal in rows2:
        code = (code or '').strip()
        val = float(bal or 0.0)
        # inversión de signo para cuentas 2, 3, 5
        if code and code[0] in ('2', '3', '5'):
            val = -val
        if code in accounts_dict:
            accounts_dict[code]['balances'][period_key] = val

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

# Verificar la cuenta 410103
print("=== RESULTADO FINAL CUENTA 410103 ===")
for code in sorted([c for c in accounts_dict if c.startswith('410103')]):
    n = accounts_dict[code]
    print(f"  {code} | {n['name'][:50]} | 2023-12: {n['balances']['2023-12']:>14.2f} | 2024-12: {n['balances']['2024-12']:>14.2f}")

print()
print("=== CUENTA 41010201 (ahorros) ===")
for code in sorted([c for c in accounts_dict if c.startswith('410102')]):
    n = accounts_dict[code]
    print(f"  {code} | {n['name'][:50]} | 2023-12: {n['balances']['2023-12']:>14.2f} | 2024-12: {n['balances']['2024-12']:>14.2f}")

print()
print("=== TOTALES RAIZ 4 (INGRESOS/GASTOS) ===")
root4 = accounts_dict.get('4')
if root4:
    print(f"  4 | {root4['name'][:50]} | 2023-12: {root4['balances']['2023-12']:>14.2f} | 2024-12: {root4['balances']['2024-12']:>14.2f}")

# Contar nodos con saldo negativo en cuentas tipo 4 (deberían ser positivos)
neg_nodes = [(c, accounts_dict[c]['balances']['2023-12']) for c in accounts_dict 
             if c.startswith('4') and accounts_dict[c]['balances']['2023-12'] < -0.05]
print(f"\nCuentas tipo 4 con saldo negativo (incorrecto): {len(neg_nodes)}")
for c, v in neg_nodes[:10]:
    print(f"  {c}: {v:.2f}")
