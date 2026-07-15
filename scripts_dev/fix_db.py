import sqlite3

def fix_decimals():
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    
    decimal_cols = [
        'original_amount', 'balance', 'rate', 'generic_provision', 
        'specific_provision', 'required_provision', 'established_provision', 
        'interest_receivable', 'interest_suspended', 'current_portfolio', 
        'past_due_portfolio', 'refinanced_current', 'refinanced_past_due', 
        'restructured_current', 'restructured_past_due', 'judicial_portfolio', 
        'guarantee_value', 'provision'
    ]
    
    for col in decimal_cols:
        c.execute(f"UPDATE credit_risk_creditoperation SET {col} = '0' WHERE {col} = '' OR {col} LIKE '%NaN%' OR {col} IS NULL")
    
    conn.commit()
    conn.close()
    print('Cleaned bad decimals in credit_risk_creditoperation')

if __name__ == '__main__':
    fix_decimals()
