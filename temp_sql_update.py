import sqlite3
from decimal import Decimal

conn = sqlite3.connect('db.sqlite3')
cur = conn.cursor()

# Get mapping
pd_map = {
    'NORMAL': Decimal('0.70'), '0': Decimal('0.70'), 'A': Decimal('0.70'),
    'CPP': Decimal('5.00'), 'B': Decimal('5.00'), '1': Decimal('5.00'),
    'DEFICIENTE': Decimal('25.00'), 'C': Decimal('25.00'), '2': Decimal('25.00'),
    'DUDOSO': Decimal('60.00'), 'D': Decimal('60.00'), '3': Decimal('60.00'),
    'PERDIDA': Decimal('100.00'), 'E': Decimal('100.00'), '4': Decimal('100.00')
}

cur.execute('SELECT id, sbs_classification, balance, days_past_due FROM credit_risk_creditoperation')
ops = cur.fetchall()

updates = []

for op_id, classification, balance, dpd in ops:
    if balance is None:
        continue
        
    c = (classification or '').upper()
    pd_val = Decimal('0.70')
    if c in pd_map:
        pd_val = pd_map[c]
        
    dpd = int(dpd) if dpd else 0
    dpd_pd = Decimal('0.70')
    if dpd > 120:
        dpd_pd = Decimal('100.00')
    elif dpd > 60:
        dpd_pd = Decimal('60.00')
    elif dpd > 30:
        dpd_pd = Decimal('25.00')
    elif dpd > 8:
        dpd_pd = Decimal('5.00')
        
    final_pd = max(pd_val, dpd_pd)
    balance_dec = Decimal(str(balance))
    el_val = (final_pd / Decimal('100')) * balance_dec * Decimal('0.45')
    
    updates.append((float(final_pd), float(el_val), op_id))

print(f"Executing {len(updates)} updates...")
cur.executemany("UPDATE credit_risk_creditriskmetrics SET pd = ?, expected_loss = ? WHERE operation_id = ?", updates)
conn.commit()
print("Done!")
