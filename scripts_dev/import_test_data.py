import os
import django
import pandas as pd
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from credit_risk.models import Customer
from liquidity_risk.models import LiabilityOperation, LiquidAsset, HistoricalDepositBalance
from liquidity_risk.engine import process_monthly_liquidity
from utilities.models import BulkLoadLog

def clean_decimal(val):
    if pd.isna(val) or val == '': return 0
    try: return float(val)
    except: return 0

def parse_date(date_val):
    if pd.isna(date_val) or date_val == '': return None
    try: return pd.to_datetime(date_val).date()
    except: return None

def run_import(filename='data_prueba_liquidez_2026.xlsx'):
    print(f"Iniciando importación de {filename}...")
    
    if not os.path.exists(filename):
        print(f"Error: El archivo {filename} no existe.")
        return

    sheets = pd.read_excel(filename, sheet_name=None)
    
    # 1. PASIVOS
    df_liab = sheets.get('PASIVOS')
    count_liab = 0
    cutoff_dates = set()
    
    if df_liab is not None:
        print("Procesando Pasivos...")
        for _, row in df_liab.iterrows():
            try:
                dt = parse_date(row.get('FECHA DE CORTE'))
                if not dt: continue
                cutoff_dates.add(dt.strftime('%Y-%m-%d'))
                
                obj, created = LiabilityOperation.objects.update_or_create(
                    operation_code=str(row.get('NRO OPERACION')),
                    load_date=dt,
                    defaults={
                        'customer_code': str(row.get('CODIGO SOCIO/CLIENTE', '')),
                        'customer_name': str(row.get('APELLIDOS NOMBRES', 'N/A')),
                        'opening_date': parse_date(row.get('FECHA DE APERTURA')),
                        'due_date': parse_date(row.get('FECHA DE VENCIMIENTO')),
                        'product': str(row.get('PRODUCTO', 'N/A')),
                        'currency': str(row.get('MONEDA', 'S/')),
                        'amount': clean_decimal(row.get('MONTO')),
                        'balance': clean_decimal(row.get('SALDO')),
                        'rate': clean_decimal(row.get('TASA')),
                        'term': int(clean_decimal(row.get('PLAZO'))),
                        'agency': str(row.get('AGENCIA', 'CENTRAL'))
                    }
                )
                count_liab += 1
            except Exception as e:
                print(f"Error en fila pasivos: {e}")
                
    # 2. ACTIVOS
    df_assets = sheets.get('ACTIVOS_LIQUIDOS')
    count_assets = 0
    if df_assets is not None:
        print("Procesando Activos Líquidos...")
        for _, row in df_assets.iterrows():
            try:
                dt = parse_date(row.get('FECHA DE CORTE'))
                if not dt: continue
                LiquidAsset.objects.update_or_create(
                    name=str(row.get('NOMBRE DEL ACTIVO')),
                    load_date=dt,
                    defaults={
                        'asset_type': str(row.get('TIPO (CAJA/BANCOS/BCRP/INVERSIONES)')),
                        'currency': str(row.get('MONEDA', 'S/')),
                        'amount': clean_decimal(row.get('MONTO')),
                        'haircut': clean_decimal(row.get('HAIRCUT %'))
                    }
                )
                count_assets += 1
            except Exception as e:
                print(f"Error en fila activos: {e}")

    # 3. HISTORICOS
    df_hist = sheets.get('SALDOS_HISTORICOS')
    count_hist = 0
    if df_hist is not None:
        print("Procesando Saldos Históricos...")
        for _, row in df_hist.iterrows():
            try:
                dt = parse_date(row.get('FECHA'))
                if not dt: continue
                HistoricalDepositBalance.objects.update_or_create(
                    date=dt,
                    currency=str(row.get('MONEDA', 'S/')),
                    product_type=str(row.get('TIPO PRODUCTO', 'TOTAL')),
                    defaults={'total_balance': clean_decimal(row.get('SALDO TOTAL'))}
                )
                count_hist += 1
            except: continue

    # Process metrics
    print("Recalculando motor de riesgo...")
    for dt_str in cutoff_dates:
        process_monthly_liquidity(datetime.strptime(dt_str, '%Y-%m-%d').date())

    # Log
    BulkLoadLog.objects.create(
        file_name=filename,
        load_type='LIABILITY',
        cut_off_dates=", ".join(sorted(list(cutoff_dates))),
        records_processed=count_liab,
        status='Success'
    )
    
    print(f"Importación completa. Registros: {count_liab}. Cortes: {len(cutoff_dates)}")

if __name__ == '__main__':
    run_import()
