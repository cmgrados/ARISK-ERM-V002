import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()
cursor.execute("SELECT id, plan_id, data FROM strategic_risk_strategicmatrix WHERE matrix_type='MPC';")
rows = cursor.fetchall()
for r in rows:
    print(f"ID: {r[0]}, Plan ID: {r[1]}, Data: {r[2]}")
