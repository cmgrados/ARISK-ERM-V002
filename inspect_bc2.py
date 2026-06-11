import sqlite3

conn = sqlite3.connect('db.sqlite3')
cur = conn.cursor()

# Analizar cuenta 410103 y sus hijos en diciembre 2023 y 2024
print("=== CUENTA 410103 - JERARQUIA COMPLETA ===")
rows = cur.execute(
    "SELECT account_code, account_name FROM liquidity_risk_liqbalancedetail "
    "WHERE account_code LIKE '410103%' GROUP BY account_code ORDER BY account_code"
).fetchall()
for r in rows:
    print(r)

print()
print("=== SALDOS DIC 2023 - Cuentas 410103 ===")
rows2 = cur.execute(
    "SELECT account_code, account_name, balance FROM liquidity_risk_liqbalancedetail "
    "WHERE account_code LIKE '410103%' AND period = '2023-12-31' ORDER BY account_code"
).fetchall()
for r in rows2:
    print(r)
# El saldo de 410103 en el BC
padre = [r for r in rows2 if r[0] == '410103']
hijos_directos = [r for r in rows2 if r[0].startswith('410103') and r[0] != '410103' and len(r[0]) == 8]
print(f"\nPadre 410103: {padre}")
print(f"Hijos directos (8 dig): {hijos_directos}")
sum_hijos = sum(r[2] for r in hijos_directos)
print(f"Suma hijos directos: {sum_hijos}")
print(f"Diferencia (padre - suma hijos): {padre[0][2] - sum_hijos if padre else 'N/A'}")

print()
print("=== SALDOS DIC 2024 - Cuentas 410103 ===")
rows3 = cur.execute(
    "SELECT account_code, account_name, balance FROM liquidity_risk_liqbalancedetail "
    "WHERE account_code LIKE '410103%' AND period = '2024-12-31' ORDER BY account_code"
).fetchall()
for r in rows3:
    print(r)

print()
print("=== CUENTA 41010201 - para ver profundidad ===")
rows4 = cur.execute(
    "SELECT DISTINCT account_code, account_name FROM liquidity_risk_liqbalancedetail "
    "WHERE account_code LIKE '41010201%' ORDER BY account_code"
).fetchall()
for r in rows4:
    print(r)

print()
print("=== CUENTAS CON CODIGO > 8 DIGITOS BAJO 4101 ===")
rows5 = cur.execute(
    "SELECT DISTINCT account_code, account_name FROM liquidity_risk_liqbalancedetail "
    "WHERE account_code LIKE '4101%' AND length(account_code) > 8 ORDER BY account_code"
).fetchall()
for r in rows5:
    print(r)
