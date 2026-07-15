import sqlite3
from datetime import datetime
import pandas as pd

def parse_date(date_val):
    if pd.isna(date_val) or date_val is None or str(date_val).strip().lower() in ('', 'nan', 'none', 'nat'): return None
    try:
        return pd.to_datetime(date_val, dayfirst=True).date()
    except: return None

conn = sqlite3.connect('db.sqlite3')
c = conn.cursor()
c.execute('SELECT cut_off_dates FROM utilities_bulkloadlog WHERE id=175')
res = c.fetchone()
if res and res[0]:
    raw_dates = [d.strip() for d in res[0].split(',') if d.strip() and d.strip().upper() != 'N/A']
    print('Dates to delete:', raw_dates)
    for rd in raw_dates:
        clean_rd = rd.replace('"', '').strip()
        parsed = parse_date(clean_rd)
        if parsed:
            d_str = parsed.strftime('%Y-%m-%d')
            c.execute('DELETE FROM credit_risk_creditoperation WHERE load_date = ?', (d_str,))
            c.execute('DELETE FROM credit_risk_carteracreditocarga WHERE fecha_corte = ?', (d_str,))
            c.execute('DELETE FROM credit_risk_creditriskperiodparameter WHERE load_date = ?', (d_str,))
            print(f'Deleted records for date {d_str}')
    c.execute('DELETE FROM utilities_bulkloadlog WHERE id=175')
    conn.commit()
    print('Log 175 deleted manually!')
else:
    # Si no tiene fechas, borrar el log igual
    c.execute('DELETE FROM utilities_bulkloadlog WHERE id=175')
    conn.commit()
    print('Log 175 (no dates) deleted manually!')
