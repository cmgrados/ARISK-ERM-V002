"""
Regenera budget_data de TODOS los planes financieros via SQLite + Python puro.
Aplica propagación bottom-up: el saldo del padre = suma de sus hijos si el padre tiene 0.
Sin nodos ficticios.
"""
import sqlite3
import json
import sys

conn = sqlite3.connect('db.sqlite3')
cur = conn.cursor()

# ── Obtener todos los planes con budget_data ──────────────────────────────────
all_plans = cur.execute(
    "SELECT id, name, budget_data FROM financial_planning_financialplan "
    "WHERE budget_data IS NOT NULL AND budget_data != '{}' AND budget_data != 'null'"
).fetchall()

if not all_plans:
    plans = cur.execute("SELECT id, name FROM financial_planning_financialplan").fetchall()
    print("No hay planes con budget_data. Planes disponibles:")
    for p in plans:
        print(f"  {p}")
    sys.exit(1)

print(f"Planes a regenerar: {len(all_plans)}")

# ── Mapa de fechas disponibles ────────────────────────────────────────────────
all_db_dates_raw = cur.execute(
    "SELECT DISTINCT period FROM liquidity_risk_liqbalancedetail ORDER BY period"
).fetchall()
all_db_dates = {d[:7]: d for (d,) in all_db_dates_raw}  # 'YYYY-MM' → 'YYYY-MM-DD'

def propagate_balance(code, accounts_dict, sel_periods):
    node = accounts_dict[code]
    if not node['children']:
        return
    for child_code in node['children']:
        propagate_balance(child_code, accounts_dict, sel_periods)
    for p in sel_periods:
        children_sum = sum(accounts_dict[c]['balances'][p] for c in node['children'])
        if abs(node['balances'][p]) < 0.005:
            node['balances'][p] = children_sum

def has_movement(node, accounts_dict):
    if any(abs(v) > 0.005 for v in node['balances'].values()):
        return True
    return any(has_movement(accounts_dict[c], accounts_dict) for c in node['children'])

def flatten_tree(nodes, accounts_dict, sel_periods, depth=1):
    flat = []
    for n in sorted(nodes, key=lambda x: x['code']):
        if not has_movement(n, accounts_dict):
            continue
        n_copy = dict(n)
        child_nodes = [accounts_dict[c] for c in n['children']]
        n_copy['children_codes'] = [
            c for c in n['children'] if has_movement(accounts_dict[c], accounts_dict)
        ]
        n_copy['depth'] = depth
        n_copy['level'] = len(n['code'])
        del n_copy['children']

        # period-over-period delta for "ER Mensual" view
        monthly = {}
        prev_val = 0.0
        for p in sel_periods:
            curr_val = n_copy['balances'].get(p, 0.0)
            monthly[p] = round(curr_val - prev_val, 2)
            prev_val = curr_val
        n_copy['monthly_balances'] = monthly

        flat.append(n_copy)
        if child_nodes:
            flat.extend(flatten_tree(child_nodes, accounts_dict, sel_periods, depth + 1))
    return flat

for plan_row in all_plans:
    plan_id, plan_name, budget_data_raw = plan_row
    print(f"\n{'='*60}")
    print(f"Plan: '{plan_name}' (id={plan_id})")

    stored = json.loads(budget_data_raw) if budget_data_raw else {}
    selected_periods = stored.get('selected_periods', [])

    if not selected_periods:
        print("  SKIP: No hay períodos en budget_data.")
        continue

    # Mapear períodos a fechas
    matched_pairs = [(all_db_dates[p], p) for p in sorted(selected_periods) if p in all_db_dates]
    if not matched_pairs:
        print(f"  SKIP: Ninguno de los períodos {selected_periods} encontrado en la BD.")
        continue

    matching_date_strs = [m[0] for m in matched_pairs]
    sel_periods = [m[1] for m in matched_pairs]
    print(f"  Períodos encontrados: {sel_periods}")

    # Construir accounts_dict
    placeholders = ','.join(['?'] * len(matching_date_strs))
    acct_rows = cur.execute(
        f"SELECT account_code, MAX(account_name) FROM liquidity_risk_liqbalancedetail "
        f"WHERE period IN ({placeholders}) GROUP BY account_code",
        matching_date_strs
    ).fetchall()

    accounts_dict = {}
    for code, name in acct_rows:
        code = (code or '').strip()
        if not code:
            continue
        accounts_dict[code] = {
            'code': code,
            'name': (name or '').strip(),
            'balances': {p: 0.0 for p in sel_periods},
            'children': [],
            'has_children': False,
            'parent_code': None,
            'has_discrepancy': False,
            'discrepancy': {},
        }

    print(f"  Cuentas en catálogo: {len(accounts_dict)}")

    # Llenar saldos
    for date_str, period_key in zip(matching_date_strs, sel_periods):
        bal_rows = cur.execute(
            "SELECT account_code, SUM(balance) FROM liquidity_risk_liqbalancedetail "
            "WHERE period = ? GROUP BY account_code", (date_str,)
        ).fetchall()
        for code, bal in bal_rows:
            code = (code or '').strip()
            val = float(bal or 0.0)
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
    roots = sorted([n for n in accounts_dict.values() if not n['parent_code']], key=lambda x: x['code'])
    for root in roots:
        propagate_balance(root['code'], accounts_dict, sel_periods)

    # Aplanar árboles
    bs_roots = [r for r in roots if r['code'][0] in ('1', '2', '3')]
    is_roots = [r for r in roots if r['code'][0] not in ('1', '2', '3')]

    flat_bs = flatten_tree(bs_roots, accounts_dict, sel_periods)
    flat_is = flatten_tree(is_roots, accounts_dict, sel_periods)

    # Guardar
    new_budget_data = json.dumps({
        "selected_periods": sel_periods,
        "balance_sheet": flat_bs,
        "income_statement": flat_is
    })
    cur.execute(
        "UPDATE financial_planning_financialplan SET budget_data = ? WHERE id = ?",
        (new_budget_data, plan_id)
    )
    conn.commit()
    print(f"  [OK] Guardado: {len(flat_bs)} cuentas Balance | {len(flat_is)} cuentas Estado de Resultados")

    # Verificación rápida
    nodes_410103 = [n for n in flat_is if n['code'].startswith('410103')]
    if nodes_410103:
        print(f"  Cuenta 410103 y sub-cuentas:")
        for n in nodes_410103:
            vals = ' | '.join(f"{p}: {n['balances'].get(p, 0):>12.2f}" for p in sel_periods[:3])
            print(f"    {n['code']} | {n['name'][:40]:<40} | {vals}")
    else:
        print("  Cuenta 410103: no tiene movimiento en los períodos seleccionados.")

    dummy = [n for n in flat_is + flat_bs if 'Saldos no asignados' in n.get('name', '')]
    print(f"  Nodos ficticios: {len(dummy)}")

conn.close()
print(f"\n{'='*60}")
print("Proceso completado.")
