import sqlite3
import json
conn = sqlite3.connect('db.sqlite3')
cur = conn.cursor()
cur.execute("SELECT id, name, plan_type, budget_data FROM financial_planning_financialplan WHERE plan_type='INSTITUTIONAL'")
rows = cur.fetchall()
for row in rows:
    print(f'ID: {row[0]}, Name: {row[1]}, Type: {row[2]}, HasBudget: {bool(row[3])}')
    if row[3]:
        data = json.loads(row[3])
        print(f'  Keys: {list(data.keys())}')
        print(f'  Selected Periods: {data.get("selected_periods", [])}')
