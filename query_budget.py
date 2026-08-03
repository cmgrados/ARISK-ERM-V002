import sqlite3
conn = sqlite3.connect('db.sqlite3')
cur = conn.cursor()
cur.execute("""
SELECT bl.id, bld.period_index, bld.amount
FROM financial_planning_budgetlinedetail bld
JOIN financial_planning_budgetline bl ON bld.budget_line_id = bl.id
JOIN financial_planning_budgetitem bi ON bl.item_id = bi.id
WHERE bi.code = 'ACC_4302'
ORDER BY bl.id DESC, bld.period_index ASC LIMIT 12
""")
rows = cur.fetchall()
for r in rows:
    print(r)
conn.close()
