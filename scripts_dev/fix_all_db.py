import sqlite3

def fix_all_decimals():
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in c.fetchall()]
    
    for table in tables:
        c.execute(f"PRAGMA table_info({table})")
        columns = c.fetchall()
        for col in columns:
            col_name = col[1]
            col_type = col[2].upper()
            if 'DECIMAL' in col_type or 'NUMERIC' in col_type or 'REAL' in col_type:
                # Update bad strings to '0'
                query = f"UPDATE {table} SET {col_name} = '0' WHERE {col_name} IN ('', 'nan', 'NaN', 'NAN', 'None', '<NA>') OR {col_name} LIKE '%NaN%'"
                c.execute(query)
                
    conn.commit()
    conn.close()
    print('Cleaned all bad decimals in all tables')

if __name__ == '__main__':
    fix_all_decimals()
