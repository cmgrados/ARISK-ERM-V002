import sqlite3
import json

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()
cursor.execute("SELECT id, budget_data FROM financial_planning_financialplan WHERE id=8;")
row = cursor.fetchone()
if not row or not row[1]:
    print("No budget_data")
    conn.close()
    exit()

budget_data = json.loads(row[1])
income_statement = budget_data.get('income_statement', [])

def has_movement(node):
    if any(abs(v) > 0.005 for v in node['balances'].values()):
        return True
    return any(has_movement(c) for c in node.get('children', []))

# Re-flatten using the existing structure but injecting dummy nodes correctly
def re_flatten(nodes, depth=1):
    flat = []
    for n in sorted(nodes, key=lambda x: x['code']):
        n_copy = dict(n)
        
        # We don't have children objects, we only have the flat list.
        # So we need to reconstruct the tree first!
        pass

# Actually, the easiest way is to modify the flat list directly!
new_is = []
dummy_nodes_to_add = []

for n in income_statement:
    new_is.append(n)
    if n.get('has_discrepancy'):
        dummy_code = n['code'] + '99'
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
            'depth': n['depth'] + 1,
            'level': len(dummy_code)
        }
        dummy_nodes_to_add.append(dummy_node)

for d in dummy_nodes_to_add:
    new_is.append(d)

# Sort the flat list by code
new_is.sort(key=lambda x: x['code'])
budget_data['income_statement'] = new_is

cursor.execute("UPDATE financial_planning_financialplan SET budget_data=? WHERE id=8;", (json.dumps(budget_data),))
conn.commit()
conn.close()
print("Success! Injected dummy nodes into sqlite.")
