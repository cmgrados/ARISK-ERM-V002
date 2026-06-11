import pandas as pd
import numpy as np
import traceback
from datetime import datetime, date
import unicodedata
import re
from decimal import Decimal
from .models import (
    LiqLoadStatus, LiqBalanceUpload, LiqBalanceDetail,
    LiqSavingsUpload, LiqSavingsAccount,
    LiqAccountMapping, LiqAccountPlanModel
)

def normalize_text(text):
    if text is None or pd.isna(text): return ""
    text = str(text).upper()
    return "".join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn').strip()

def clean_decimal(val):
    if pd.isna(val) or val is None: return Decimal('0.00')
    try:
        s = str(val).replace('S/', '').replace('$', '').replace(',', '').strip()
        if s == '' or s.lower() == 'nan': return Decimal('0.00')
        return Decimal(s)
    except:
        return Decimal('0.00')

def parse_date(val):
    if pd.isna(val) or val is None: return None
    if isinstance(val, (date, datetime)): return val
    try:
        return pd.to_datetime(val).date()
    except:
        return None

def to_date(val):
    if val is None or pd.isna(val) or val == "": return None
    if isinstance(val, (date, datetime)): return val
    try:
        # Intentar convertir directamente si es un objeto datetime o string ISO
        return pd.to_datetime(val).date()
    except:
        if isinstance(val, str):
            # Intentar con formatos comunes si falla el automático
            for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d', '%d-%m-%Y']:
                try:
                    return datetime.strptime(val, fmt).date()
                except:
                    continue
    return None

def process_balance_load(upload_id):
    main_upload = LiqBalanceUpload.objects.get(id=upload_id)
    main_upload.status = LiqLoadStatus.VALIDATING
    main_upload.save()
    
    try:
        # Load the file
        sheets_to_try = [0]
        if main_upload.file_source.name.endswith('.xlsx'):
            try:
                xls = pd.ExcelFile(main_upload.file_source.path, engine='openpyxl')
                sheets_to_try = xls.sheet_names
            except:
                xls = pd.ExcelFile(main_upload.file_source.path)
                sheets_to_try = xls.sheet_names
        
        df_raw = None
        found_header_idx = -1
        found_sheet = None
        col_indices = {'code': -1, 'name': -1, 'saldo': -1, 'period': -1}

        for sheet in sheets_to_try:
            if main_upload.file_source.name.endswith('.xlsx'):
                df_temp = pd.read_excel(main_upload.file_source.path, header=None, sheet_name=sheet)
            else:
                df_temp = pd.read_csv(main_upload.file_source.path, header=None)
            
            if df_temp.empty: continue
            
            for i in range(min(150, len(df_temp))):
                row_raw = df_temp.iloc[i]
                row_values = [normalize_text(v) for v in row_raw]
                
                idx_code = next((j for j, v in enumerate(row_values) if 'CUENTA' in v or 'CODIGO' in v), None)
                idx_name = next((j for j, v in enumerate(row_values) if any(x in v for x in ['NOMBRE', 'DENOMINACION', 'DESCRIPCION'])), None)
                idx_period = next((j for j, v in enumerate(row_values) if 'PERIODO' in v or 'FECHA' in v), None)
                
                # Para el formato pivoteado (masivo), buscamos si alguna columna es una fecha
                has_date_cols = any(to_date(v) is not None for v in row_raw)
                idx_saldo = next((j for j, v in enumerate(row_values) if any(x in v for x in ['SALDO', 'TOTAL', 'DEBE', 'HABER', 'IMPORTE'])), None)

                if idx_code is not None and (idx_saldo is not None or has_date_cols):
                    found_header_idx = i
                    found_sheet = sheet
                    df_raw = df_temp
                    col_indices['code'] = idx_code
                    col_indices['saldo'] = idx_saldo if idx_saldo is not None else -1 # Usaremos date_columns si es -1
                    if idx_name is not None: col_indices['name'] = idx_name
                    if idx_period is not None: col_indices['period'] = idx_period
                    break
            if found_header_idx != -1: break

        if found_header_idx == -1:
            main_upload.status = LiqLoadStatus.ERROR
            main_upload.observations = "No se encontró cabecera con 'CUENTA' y 'SALDO'."
            main_upload.save()
            return False

        # Set headers and slice data
        headers = df_raw.iloc[found_header_idx]
        df = df_raw.iloc[found_header_idx+1:].copy()
        df.columns = [str(h) for h in headers]
        
        col_code_name = str(headers.iloc[col_indices['code']])
        col_name_name = str(headers.iloc[col_indices['name']]) if col_indices['name'] != -1 else None
        col_saldo_name = str(headers.iloc[col_indices['saldo']]) if col_indices['saldo'] != -1 else None
        col_period_name = str(headers.iloc[col_indices['period']]) if col_indices['period'] != -1 else None
        # Detect multiple periods
        periods_found = [main_upload.period]
        date_columns = {} # date -> column_name

        if col_period_name:
            df['temp_period'] = df[col_period_name].apply(to_date)
            unique_periods = df['temp_period'].dropna().unique()
            if len(unique_periods) > 0:
                periods_found = unique_periods
        else:
            # Check if headers contain multiple dates (Massive Pivot Format)
            for col in df.columns:
                d = to_date(col)
                if d:
                    date_columns[d] = col
            
            if date_columns:
                periods_found = sorted(date_columns.keys())

        total_processed = 0
        all_accounts = list(LiqAccountMapping.objects.filter(plan_model=main_upload.plan_model))
        
        for target_period in periods_found:
            # Create or get upload for this period
            if target_period == main_upload.period:
                current_upload = main_upload
            else:
                current_upload, created = LiqBalanceUpload.objects.get_or_create(
                    period=target_period,
                    defaults={
                        'plan_model': main_upload.plan_model,
                        'currency': main_upload.currency,
                        'user': main_upload.user,
                        'status': LiqLoadStatus.VALIDATING,
                        'file_source': main_upload.file_source
                    }
                )
                if not created and current_upload.status == LiqLoadStatus.SUCCESS:
                    # Si ya está cargado con éxito, lo saltamos o lo actualizamos (aquí elegimos limpiar y recargar)
                    current_upload.details.all().delete()
                    current_upload.status = LiqLoadStatus.VALIDATING
                    current_upload.save()

            # Filter data or use specific column
            if col_period_name:
                df_period = df[df['temp_period'] == target_period]
                current_col_saldo = col_saldo_name
            elif date_columns:
                df_period = df
                current_col_saldo = date_columns[target_period]
            else:
                df_period = df
                current_col_saldo = col_saldo_name
            
            # Build data dict
            rows = df_period.to_dict('records')
            for row in rows:
                code = str(row.get(col_code_name, '')).strip()
                if code and code != 'nan' and not code.startswith('TOTAL'):
                    excel_data[code] = {
                        'name': str(row.get(col_name_name, '')) if col_name_name else "",
                        'saldo': clean_decimal(row.get(current_col_saldo, 0))
                    }
            
            # Clear old details
            LiqBalanceDetail.objects.filter(upload=current_upload).delete()
            details = []
            
            # Process with plan mapping
            for acc in all_accounts:
                match = excel_data.pop(acc.account_code, None)
                saldo = match['saldo'] if match else Decimal('0.00')
                details.append(LiqBalanceDetail(
                    upload=current_upload, period=target_period,
                    currency=current_upload.currency if current_upload.currency != 'MX' else 'MN',
                    account_code=acc.account_code, account_name=acc.account_name,
                    balance=saldo, nature='D', liquidity_item=acc.liquidity_item
                ))
            
            # Remaining in excel
            for code, data in excel_data.items():
                details.append(LiqBalanceDetail(
                    upload=current_upload, period=target_period,
                    currency=current_upload.currency if current_upload.currency != 'MX' else 'MN',
                    account_code=code, account_name=data['name'],
                    balance=data['saldo'], nature='D', liquidity_item='OTROS'
                ))
            
            LiqBalanceDetail.objects.bulk_create(details)
            current_upload.status = LiqLoadStatus.SUCCESS
            current_upload.observations = f"Cargados {len(details)} registros."
            current_upload.save()
            total_processed += 1

        main_upload.observations = f"Se procesaron {total_processed} periodos correctamente."
        main_upload.save()
        return True
    except Exception as e:
        main_upload.status = LiqLoadStatus.ERROR
        main_upload.observations = f"Error: {str(e)}\n{traceback.format_exc()}"[:1000]
        main_upload.save()
        return False

def process_savings_load(upload_id):
    upload = LiqSavingsUpload.objects.get(id=upload_id)
    upload.status = LiqLoadStatus.VALIDATING
    upload.save()
    
    try:
        df = pd.read_excel(upload.file_source.path) if upload.file_source.name.endswith('.xlsx') else pd.read_csv(upload.file_source.path)
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        count = 0
        LiqSavingsAccount.objects.filter(upload=upload).delete()
        
        accounts = []
        rows = df.to_dict('records')
        for row in rows:
            accounts.append(LiqSavingsAccount(
                upload=upload,
                period=upload.period,
                customer_id=str(row.get('SOCIO', '')),
                document=str(row.get('DOCUMENTO', '')),
                account_number=str(row.get('CUENTA', '')),
                product=str(row.get('PRODUCTO', '')),
                currency=str(row.get('MONEDA', '')),
                balance=clean_decimal(row.get('SALDO')),
                opening_date=parse_date(row.get('FECHA APERTURA')),
                last_movement_date=parse_date(row.get('FECHA ÚLTIMO MOVIMIENTO')),
                agency=str(row.get('AGENCIA', '')),
                segment=str(row.get('SEGMENTO', '')),
                is_major_depositor=bool(row.get('INDICADOR GRAN DEPOSITANTE', False))
            ))
            count += 1
            
        LiqSavingsAccount.objects.bulk_create(accounts)
        upload.status = LiqLoadStatus.SUCCESS
        upload.save()
        return True
    except Exception as e:
        upload.status = LiqLoadStatus.ERROR
        upload.save()
        return False

def process_account_mapping_load(file_path, plan_model="ESTANDAR"):
    try:
        df = pd.read_excel(file_path) if file_path.endswith('.xlsx') else pd.read_csv(file_path)
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        col_cuenta = next((c for c in df.columns if 'CUENTA' in c or 'CODIGO' in c), None)
        col_denom = next((c for c in df.columns if any(x in c for x in ['DENOMINACION', 'NOMBRE', 'DENOMINACIÓN'])), None)
        col_tipo = next((c for c in df.columns if 'TIPO' in c), None)
        col_moneda = next((c for c in df.columns if 'MONEDA' in c), None)
        col_banda = next((c for c in df.columns if 'BANDA' in c), None)
        col_regla = next((c for c in df.columns if 'REGLA' in c or 'DISTRIBUCION' in c), None)
        col_origen = next((c for c in df.columns if 'ORIGEN' in c or 'FUENTE' in c), None)
        
        if not col_cuenta or not col_denom:
            return False, f"Columnas no encontradas. Se requiere 'CUENTA' y 'DENOMINACIÓN'."

        from .models import LiqAccountMapping, LiqAccountPlanModel, LiqTimeBand
        plan_obj, _ = LiqAccountPlanModel.objects.get_or_create(name=plan_model)
        
        count = 0
        current_rubro = "OTROS"
        
        for _, row in df.iterrows():
            code = str(row.get(col_cuenta, '')).strip()
            if not code or code == 'nan': continue
            name = str(row.get(col_denom, '')).strip()
            
            if len(code) == 2:
                current_rubro = name
            
            # Inferred defaults
            acc_type = 'ACT' if code.startswith('1') else 'PAS' if code.startswith('2') else 'PAT'
            if col_tipo and not pd.isna(row.get(col_tipo)):
                val_tipo = str(row.get(col_tipo)).upper()
                if 'ACT' in val_tipo: acc_type = 'ACT'
                elif 'PAS' in val_tipo: acc_type = 'PAS'
            
            currency = 'MN'
            if col_moneda and not pd.isna(row.get(col_moneda)):
                val_mon = str(row.get(col_moneda)).upper()
                if 'ME' in val_mon or 'USD' in val_mon: currency = 'ME'
            
            LiqAccountMapping.objects.update_or_create(
                plan_model=plan_obj,
                account_code=code,
                defaults={
                    'account_name': name,
                    'liquidity_item': current_rubro,
                    'account_type': acc_type,
                    'currency': currency,
                    'distribution_rule': 'SCHEDULE' if acc_type == 'ACT' else 'VOLATILE',
                    'data_source': 'BALANCE'
                }
            )
            count += 1
        return True, f"Se actualizaron {count} cuentas en el modelo '{plan_model}'."
    except Exception as e:
        return False, f"Error: {str(e)}\n{traceback.format_exc()}"

def process_dpf_load(upload_id):
    upload = LiqTermDepositUpload.objects.get(id=upload_id)
    upload.status = LiqLoadStatus.VALIDATING
    upload.save()
    try:
        df = pd.read_excel(upload.file_source.path) if upload.file_source.name.endswith('.xlsx') else pd.read_csv(upload.file_source.path)
        df.columns = [str(c).strip().upper() for c in df.columns]
        LiqTermDeposit.objects.filter(upload=upload).delete()
        deposits = []
        rows = df.to_dict('records')
        for row in rows:
            deposits.append(LiqTermDeposit(
                upload=upload, period=upload.period,
                customer_id=str(row.get('SOCIO', '')),
                document=str(row.get('DOCUMENTO', '')),
                certificate_number=str(row.get('CERTIFICADO', '')),
                product=str(row.get('PRODUCTO', '')),
                currency='MN' if 'MN' in str(row.get('MONEDA', '')) else 'ME',
                amount=clean_decimal(row.get('MONTO')),
                issue_date=parse_date(row.get('FECHA CONSTITUCION')),
                maturity_date=parse_date(row.get('FECHA VENCIMIENTO')),
                interest_rate=clean_decimal(row.get('TEA', 0))
            ))
        LiqTermDeposit.objects.bulk_create(deposits)
        upload.status = LiqLoadStatus.SUCCESS
        upload.save()
        return True
    except:
        upload.status = LiqLoadStatus.ERROR
        upload.save()
        return False

def process_funding_load(upload_id):
    upload = LiqFundingUpload.objects.get(id=upload_id)
    upload.status = LiqLoadStatus.VALIDATING
    upload.save()
    try:
        df = pd.read_excel(upload.file_source.path) if upload.file_source.name.endswith('.xlsx') else pd.read_csv(upload.file_source.path)
        df.columns = [str(c).strip().upper() for c in df.columns]
        LiqFundingLine.objects.filter(upload=upload).delete()
        lines = []
        for _, row in df.iterrows():
            lines.append(LiqFundingLine(
                upload=upload, period=upload.period,
                entity_name=str(row.get('ENTIDAD', '')),
                line_type=str(row.get('TIPO LINEA', '')),
                currency='MN' if 'MN' in str(row.get('MONEDA', '')) else 'ME',
                approved_amount=clean_decimal(row.get('MONTO APROBADO')),
                used_amount=clean_decimal(row.get('MONTO UTILIZADO')),
                available_amount=clean_decimal(row.get('MONTO DISPONIBLE')),
                maturity_date=parse_date(row.get('VENCIMIENTO'))
            ))
        LiqFundingLine.objects.bulk_create(lines)
        upload.status = LiqLoadStatus.SUCCESS
        upload.save()
        return True
    except:
        upload.status = LiqLoadStatus.ERROR
        upload.save()
        return False

def process_investment_load(upload_id):
    upload = LiqInvestmentUpload.objects.get(id=upload_id)
    upload.status = LiqLoadStatus.VALIDATING
    upload.save()
    try:
        df = pd.read_excel(upload.file_source.path) if upload.file_source.name.endswith('.xlsx') else pd.read_csv(upload.file_source.path)
        df.columns = [str(c).strip().upper() for c in df.columns]
        LiqInvestment.objects.filter(upload=upload).delete()
        invests = []
        for _, row in df.iterrows():
            invests.append(LiqInvestment(
                upload=upload, period=upload.period,
                entity=str(row.get('IFI', '')),
                investment_type=str(row.get('TIPO INVERSION', '')),
                currency='MN' if 'MN' in str(row.get('MONEDA', '')) else 'ME',
                amount=clean_decimal(row.get('MONTO')),
                maturity_date=parse_date(row.get('VENCIMIENTO')),
                risk_rating=str(row.get('CLASIFICACION RIESGO', ''))
            ))
        LiqInvestment.objects.bulk_create(invests)
        upload.status = LiqLoadStatus.SUCCESS
        upload.save()
        return True
    except:
        upload.status = LiqLoadStatus.ERROR
        upload.save()
        return False
