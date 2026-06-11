import sqlite3

conn = sqlite3.connect('db.sqlite3')
cur = conn.cursor()

cur.execute('SELECT id, days_past_due FROM credit_risk_creditoperation')
ops = cur.fetchall()

updates = []

for op_id, dpd in ops:
    dpd = int(dpd) if dpd else 0
    
    if dpd <= 8:
        new_class = 'NORMAL'
    elif dpd <= 30:
        new_class = 'CPP'
    elif dpd <= 60:
        new_class = 'DEFICIENTE'
    elif dpd <= 120:
        new_class = 'DUDOSO'
    else:
        new_class = 'PÉRDIDA'
        
    updates.append((new_class, op_id))

print(f"Executing {len(updates)} updates for sbs_classification...")
cur.executemany("UPDATE credit_risk_creditoperation SET sbs_classification = ? WHERE id = ?", updates)
conn.commit()
print("Done!")
