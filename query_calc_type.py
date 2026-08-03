import sqlite3
conn = sqlite3.connect('db.sqlite3')
cur = conn.cursor()
cur.execute("SELECT applied_calculation_type FROM financial_planning_budgetline WHERE id = 2295")
print(cur.fetchone())
conn.close()
