import sqlite3
import os

db_path = 'db.sqlite3'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM django_migrations WHERE app='compliance_risk'")
        cursor.execute("DROP TABLE IF EXISTS compliance_risk_regulation")
        cursor.execute("DROP TABLE IF EXISTS compliance_risk_complianceassessment")
        cursor.execute("DROP TABLE IF EXISTS compliance_risk_compliancefinding")
        conn.commit()
        print("Successfully cleaned compliance_risk from database.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()
else:
    print("Database not found.")
