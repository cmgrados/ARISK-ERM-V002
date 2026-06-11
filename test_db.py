import sqlite3
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

conn = sqlite3.connect('db.sqlite3')
df = pd.read_sql_query("SELECT account_code, account_name, balance FROM liquidity_risk_liqbalancedetail WHERE account_code LIKE '410103%';", conn)
print(df.groupby(['account_code', 'account_name']).sum())
conn.close()
