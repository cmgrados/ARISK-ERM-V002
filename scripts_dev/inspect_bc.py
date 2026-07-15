import sqlite3, json

conn = sqlite3.connect('db.sqlite3')
cur = conn.cursor()

# 1. Listar cuentas que empiezan con 4101 (Estado de Resultados - Gastos Financieros)
print("=== CUENTAS 4101xx EN EL BALANCE DE COMPROBACION ===")
rows = cur.execute(
    "SELECT DISTINCT account_code, account_name FROM liquidity_risk_liqbalancedetail "
    "WHERE account_code LIKE '4101%' ORDER BY account_code"
).fetchall()
for r in rows:
    print(r)

print()
print("=== BALANCES DE LA CUENTA 410103 POR PERIODO ===")
rows2 = cur.execute(
    "SELECT period, account_code, account_name, balance FROM liquidity_risk_liqbalancedetail "
    "WHERE account_code LIKE '410103%' ORDER BY account_code, period"
).fetchall()
for r in rows2:
    print(r)

print()
print("=== CUENTAS 2101xx EN EL BALANCE DE COMPROBACION ===")
rows3 = cur.execute(
    "SELECT DISTINCT account_code, account_name FROM liquidity_risk_liqbalancedetail "
    "WHERE account_code LIKE '2101%' ORDER BY account_code"
).fetchall()
for r in rows3:
    print(r)

print()
print("=== PERIODOS DISPONIBLES ===")
rows4 = cur.execute(
    "SELECT DISTINCT period FROM liquidity_risk_liqbalancedetail ORDER BY period"
).fetchall()
for r in rows4:
    print(r)
