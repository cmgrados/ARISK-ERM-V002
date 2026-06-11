import sqlite3
from decimal import Decimal

conn = sqlite3.connect('db.sqlite3')
cur = conn.cursor()
cur.execute("SELECT balance, days_past_due FROM credit_risk_creditoperation WHERE load_date = '2026-02-28'")

total_pe = Decimal('0.00')

for balance, dpd in cur.fetchall():
    if balance is None:
        continue
    balance = Decimal(str(balance))
    dpd = int(dpd) if dpd else 0
    
    if dpd <= 8:
        pd = Decimal('0.70')
    elif dpd <= 30:
        pd = Decimal('5.00')
    elif dpd <= 60:
        pd = Decimal('25.00')
    elif dpd <= 120:
        pd = Decimal('60.00')
    else:
        pd = Decimal('100.00')
        
    el = (pd / 100) * balance * Decimal('0.45')
    total_pe += el

print(f'Recalculated PE: {total_pe:,.2f}')
