import sqlite3
import json

conn = sqlite3.connect('db.sqlite3')
cur = conn.cursor()

# Get the mora_soles sim
cur.execute("SELECT id FROM financial_planning_simulacionescenario WHERE variable_id = 'mora_soles'")
sim_id = cur.fetchone()[0]

cur.execute(f"SELECT mes_proyeccion, valor_base FROM financial_planning_proyeccionmensual WHERE escenario_id = {sim_id} ORDER BY mes_proyeccion LIMIT 12")
rows = cur.fetchall()
print("mora_soles Y1 projections:", rows)

conn.close()
