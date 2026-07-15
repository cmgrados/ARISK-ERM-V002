import sqlite3

def fix_decimals():
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    
    decimal_cols = [
        'monto', 'sld_aport', 'tim', 'tea', 'interes', 'mora', 'cuota', 'cap_atr',
        'saldo', 'prov_req_s', 'prov_const_s', 'def_exc', 'int_deveng', 'int_suspen',
        'mnto_capit1', 'mnto_capit2', 'cap_vigent', 'cap_reest', 'cap_refinanc',
        'cap_vencido', 'cap_cob_jud', 'monto_orig', 'gar_pref_s', 'gar_autoliq_s',
        'sald_cred_cast', 'ing_diferido_s', 'sald_cred_sin_cob', 'sald_cred_reprog'
    ]
    
    for col in decimal_cols:
        c.execute(f"UPDATE credit_risk_carteracreditocarga SET {col} = '0' WHERE {col} = '' OR {col} LIKE '%NaN%' OR {col} IS NULL")
    
    conn.commit()
    conn.close()
    print('Cleaned bad decimals in utilities_carteracreditocarga')

if __name__ == '__main__':
    fix_decimals()
