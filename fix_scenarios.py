import sqlite3

conn = sqlite3.connect('db.sqlite3')
c = conn.cursor()

c.execute("UPDATE financial_planning_projectedbalanceadjustment SET scenario='OPTIMISTIC' WHERE scenario='OPTIMISTA'")
c.execute("UPDATE financial_planning_projectedbalanceadjustment SET scenario='PESSIMISTIC' WHERE scenario='PESIMISTA'")
c.execute("UPDATE financial_planning_projectedbalanceadjustment SET scenario='MC_OPTIMISTIC' WHERE scenario='MC_OPTIMISTA'")
c.execute("UPDATE financial_planning_projectedbalanceadjustment SET scenario='MC_PESSIMISTIC' WHERE scenario='MC_PESIMISTA'")

conn.commit()
print("Updated scenarios in DB directly.")
conn.close()
