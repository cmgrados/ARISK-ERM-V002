import sqlite3
import json

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()
cursor.execute("SELECT budget_data FROM financial_planning_financialplan ORDER BY id DESC LIMIT 1;")
row = cursor.fetchone()
if not row or not row[0]:
    print("No budget_data")
else:
    budget_data = json.loads(row[0])
    income_statement = budget_data.get('income_statement', [])
    print(f"Total nodes: {len(income_statement)}")
    dummy_nodes = [node for node in income_statement if node['name'] == 'Saldos no asignados a subcuentas']
    print(f"Found {len(dummy_nodes)} dummy nodes:")
    for d in dummy_nodes:
        print(f"- {d['code']} (Parent: {d['parent_code']})")

    for n in income_statement:
        if n['code'] == '41010303':
            print(f"41010303 children: {n.get('children_codes')}")
            print(f"41010303 has_discrepancy: {n.get('has_discrepancy')}")
            break
conn.close()
