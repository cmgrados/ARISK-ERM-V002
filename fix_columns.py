import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

try:
    with connection.cursor() as cursor:
        cursor.execute("ALTER TABLE liquidity_risk_liqtimeband ADD COLUMN days_start INTEGER NULL")
        cursor.execute("ALTER TABLE liquidity_risk_liqtimeband ADD COLUMN days_end INTEGER NULL")
    print("Columns added successfully!")
except Exception as e:
    print(f"Error: {e}")
