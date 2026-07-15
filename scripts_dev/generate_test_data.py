import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

def generate_liquidity_test_data(filename='data_prueba_liquidez_2026.xlsx'):
    months = [
        '2025-12-31',
        '2026-01-31',
        '2026-02-28',
        '2026-03-31'
    ]
    
    # 1. PASIVOS (1000 per month)
    liab_data = []
    products = ['AHORRO CORRIENTE', 'PLAZO FIJO 180', 'PLAZO FIJO 360', 'CTS', 'AHORRO PROGRAMADO']
    agencies = ['AGENCIA CENTRAL', 'AGENCIA SUR', 'AGENCIA NORTE', 'AGENCIA ESTE']
    currencies = ['S/', '$']
    
    for month_str in months:
        dt = datetime.strptime(month_str, '%Y-%m-%d').date()
        for i in range(1000):
            customer_id = f'CUST-{random.randint(100000, 999999)}'
            name = f'SOCIO PRUEBA {random.randint(1, 5000)}'
            op_code = f'OP-{dt.month}-{i:04d}'
            opening_date = dt - timedelta(days=random.randint(30, 730))
            due_date = dt + timedelta(days=random.randint(0, 360)) if 'PLAZO' in products[i % len(products)] else None
            
            amount = round(random.uniform(500, 50000), 2)
            balance = amount # Simplification
            tasa = round(random.uniform(0.5, 12.0), 2)
            term = random.randint(30, 720)
            
            liab_data.append({
                'CODIGO SOCIO/CLIENTE': customer_id,
                'APELLIDOS NOMBRES': name,
                'NRO OPERACION': op_code,
                'FECHA DE APERTURA': opening_date,
                'FECHA DE VENCIMIENTO': due_date,
                'PRODUCTO': random.choice(products),
                'MONEDA': random.choice(currencies),
                'MONTO': amount,
                'SALDO': balance,
                'TASA': tasa,
                'PLAZO': term,
                'AGENCIA': random.choice(agencies),
                'FECHA DE CORTE': dt
            })
            
    df_liab = pd.DataFrame(liab_data)
    
    # 2. ACTIVOS LIQUIDOS
    asset_data = []
    asset_types = ['CAJA', 'BANCOS', 'BCRP', 'INVERSIONES']
    for month_str in months:
        dt = datetime.strptime(month_str, '%Y-%m-%d').date()
        for a_type in asset_types:
            asset_data.append({
                'NOMBRE DEL ACTIVO': f'{a_type} PRINCIPAL',
                'TIPO (CAJA/BANCOS/BCRP/INVERSIONES)': a_type,
                'MONEDA': 'S/',
                'MONTO': round(random.uniform(500000, 2000000), 2),
                'HAIRCUT %': 0 if a_type != 'INVERSIONES' else 5,
                'FECHA DE CORTE': dt
            })
            
    df_assets = pd.DataFrame(asset_data)
    
    # 3. SALDOS HISTORICOS (Last 30 days for each month)
    hist_data = []
    base_balance = 50000000
    for month_str in months:
        dt = datetime.strptime(month_str, '%Y-%m-%d').date()
        for i in range(30):
            h_date = dt - timedelta(days=i)
            variation = random.uniform(-0.02, 0.02)
            balance = base_balance * (1 + variation)
            hist_data.append({
                'FECHA': h_date,
                'MONEDA': 'S/',
                'TIPO PRODUCTO': 'TOTAL DEPOSITOS',
                'SALDO TOTAL': round(balance, 2)
            })
            
    df_hist = pd.DataFrame(hist_data)
    
    # Save to Excel
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df_liab.to_excel(writer, index=False, sheet_name='PASIVOS')
        df_assets.to_excel(writer, index=False, sheet_name='ACTIVOS_LIQUIDOS')
        df_hist.to_excel(writer, index=False, sheet_name='SALDOS_HISTORICOS')
        
    print(f"Archivo '{filename}' generado exitosamente con {len(df_liab)} registros de pasivos.")

if __name__ == '__main__':
    generate_liquidity_test_data()
