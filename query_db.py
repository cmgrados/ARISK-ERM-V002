import sqlite3
conn = sqlite3.connect('db.sqlite3')
cur = conn.cursor()
cur.execute("SELECT s.variable_id, pm.mes_proyeccion, pm.valor_base FROM financial_planning_proyeccionmensual pm JOIN financial_planning_simulacionescenario s ON pm.escenario_id = s.id WHERE s.variable_id = 'mora_soles' ORDER BY s.id DESC, pm.mes_proyeccion ASC LIMIT 12")
rows = cur.fetchall()
for r in rows:
    print(r)
conn.close()
