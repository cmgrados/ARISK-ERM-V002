import psycopg2
import os
import sys

# Try to find .env
env_path = 'c:/Users/VICTUS/Desktop/A.RISK ERM/.env'
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        for line in f:
            if '=' in line:
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

db_url = os.getenv('DATABASE_URL')
if not db_url:
    print("DATABASE_URL not found in environment")
    sys.exit(1)

print(f"Connecting to: {db_url[:20]}...")
try:
    conn = psycopg2.connect(db_url, connect_timeout=10)
    print("Connection successful!")
    conn.close()
except Exception as e:
    print(f"Connection failed: {str(e)}")
    sys.exit(1)
