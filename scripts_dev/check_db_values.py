import sqlite3
import decimal

def robust_fix():
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c2 = conn.cursor()
    
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in c.fetchall()]
    
    for table in tables:
        c.execute(f"PRAGMA table_info({table})")
        columns = c.fetchall()
        decimal_cols = []
        for col in columns:
            col_name = col[1]
            col_type = col[2].upper()
            if 'DECIMAL' in col_type or 'NUMERIC' in col_type or 'REAL' in col_type:
                decimal_cols.append(col_name)
        
        if not decimal_cols:
            continue
            
        c.execute(f"PRAGMA table_info({table})")
        pk_col = None
        for col in c.fetchall():
            if col[5] == 1:
                pk_col = col[1]
                break
                
        if not pk_col: continue
            
        select_cols = [pk_col] + decimal_cols
        c.execute(f"SELECT {', '.join(select_cols)} FROM {table}")
        
        for row in c.fetchall():
            pk_val = row[0]
            updates = []
            for idx, col_name in enumerate(decimal_cols):
                val = row[idx + 1]
                if val is None:
                    continue
                try:
                    d = decimal.Decimal(str(val))
                    if d.is_nan():
                        print(f"Table {table}, Row {pk_val}, Col {col_name}: val is NaN '{val}'")
                        updates.append((col_name, '0'))
                    elif d.is_infinite():
                        print(f"Table {table}, Row {pk_val}, Col {col_name}: val is Inf '{val}'")
                        updates.append((col_name, '0'))
                except decimal.InvalidOperation:
                    print(f"Table {table}, Row {pk_val}, Col {col_name}: val is invalid '{val}'")
                    updates.append((col_name, '0'))
                except Exception as e:
                    print(f"Table {table}, Row {pk_val}, Col {col_name}: other error '{val}' -> {e}")
                    updates.append((col_name, '0'))
                    
            if updates:
                set_clause = ', '.join([f"{u[0]} = ?" for u in updates])
                params = [u[1] for u in updates] + [pk_val]
                c2.execute(f"UPDATE {table} SET {set_clause} WHERE {pk_col} = ?", params)
                
    conn.commit()
    conn.close()
    print("Robust DB fix check completed")

if __name__ == "__main__":
    robust_fix()
