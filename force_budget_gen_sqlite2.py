import sqlite3
import json

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()
cursor.execute("SELECT id, historical_data, budget_data FROM financial_planning_financialplan WHERE id=8;")
row = cursor.fetchone()

historical_data = json.loads(row[1])
budget_data = json.loads(row[2] or '{}')

income_statement = historical_data.get('income_statement', [])
balance_sheet = historical_data.get('balance_sheet', [])

def process_flat_tree(flat_list):
    new_list = []
    dummy_nodes_to_add = []

    for n in flat_list:
        new_list.append(n)
        if n.get('has_discrepancy'):
            dummy_code = n['code'] + '99'
            
            # ensure children_codes exists
            if 'children_codes' not in n:
                n['children_codes'] = []
                
            n['children_codes'].append(dummy_code)
            dummy_node = {
                'code': dummy_code,
                'name': 'Saldos no asignados a subcuentas',
                'parent_code': n['code'],
                'has_children': False,
                'balances': dict(n.get('discrepancy', {})),
                'monthly_balances': {},
                'has_discrepancy': False,
                'discrepancy': {},
                'children_codes': [],
                'depth': n.get('depth', 1) + 1,
                'level': len(dummy_code)
            }
            dummy_nodes_to_add.append(dummy_node)

    for d in dummy_nodes_to_add:
        new_list.append(d)

    new_list.sort(key=lambda x: x['code'])
    return new_list

budget_data['selected_periods'] = historical_data.get('selected_periods', [])
budget_data['income_statement'] = process_flat_tree(income_statement)
budget_data['balance_sheet'] = process_flat_tree(balance_sheet)

cursor.execute("UPDATE financial_planning_financialplan SET budget_data=? WHERE id=8;", (json.dumps(budget_data),))
conn.commit()
conn.close()
print("Success! Copied from historical and injected dummy nodes into sqlite.")
