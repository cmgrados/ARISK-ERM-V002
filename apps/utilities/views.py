import pandas as pd
import math
import io
import re
from calendar import monthrange
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from credit_risk.models import Customer, CreditOperation, CarteraCreditoCarga
# Commented out due to refactor
# from liquidity_risk.models import LiabilityOperation, LiquidAsset, HistoricalDepositBalance
# from liquidity_risk.engine import process_monthly_liquidity
from credit_risk.utils import generate_missing_metrics

from catalogs.models import Product
from django.db import transaction
from django.db.models import Sum, Max, Q, Count
from django.core.cache import cache
from django.utils.timezone import now
from datetime import datetime, date
from django.contrib.auth.decorators import login_required

from liquidity_risk.models import LiqBalanceUpload, LiqLoadStatus
from django.http import HttpResponse
import io
from .models import BulkLoadLog, Socio, LiqAccountPlanModel, LiqAccountMapping
import unicodedata
import re

def normalize_text(text):
    if text is None or pd.isna(text): return ""
    # Standardize to uppercase, remove accents, and strip special chars for mapping
    text = str(text).upper().strip()
    text = "".join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
    # For values like "C.P.P." or "1.0", we remove dots/commas
    return text.replace('.', '').replace(',', '').replace('-', '_').replace(' ', '_')

def get_col_robust(keywords, df_cols):
    # Normalize keywords
    normalized_kw = [normalize_text(k) for k in keywords]
    # Normalize columns
    col_map = {normalize_text(c): c for c in df_cols}
    
    # 1. Exact Match (Highest Priority)
    for nk in normalized_kw:
        if nk in col_map: return col_map[nk]
    
    # 2. Prefix/Partial Match (for long keywords)
    for nk in normalized_kw:
        if len(nk) < 3: continue
        for norm_name, original_name in col_map.items():
            if nk in norm_name: return original_name
            
    return None

def map_sbs_exhaustive(val):
    raw = normalize_text(val)
    if not raw: return 'NORMAL'
    # Direct mappings
    if raw in ['0', 'A', 'NORMAL', 'VIGENTE', 'NORMAL_VIGENTE']: return 'NORMAL'
    if raw in ['1', 'B', 'CPP', 'PROBLEMA', 'POTENCIAL', 'POTENCIALMENTE', 'CON_PROBLEMAS', 'CON_DIFICULTADES']: return 'CPP'
    if raw in ['2', 'C', 'DEFICIENTE']: return 'DEFICIENTE'
    if raw in ['3', 'D', 'DUDOSO']: return 'DUDOSO'
    if raw in ['4', 'E', 'PERDIDA']: return 'PERDIDA'
    # Partial keywords
    if 'PERDIDA' in raw: return 'PERDIDA'
    if 'DUDOSO' in raw: return 'DUDOSO'
    if 'DEFICIENTE' in raw: return 'DEFICIENTE'
    if 'CPP' in raw or 'PROB' in raw or 'POT' in raw: return 'CPP'
    return 'NORMAL'

def map_credit_type(val):
    raw = normalize_text(val)
    if not raw: return 'CONSUMO'
    if 'CONS' in raw: return 'CONSUMO'
    if 'HIPO' in raw or 'VIV' in raw: return 'HIPOTECARIO'
    if 'MICRO' in raw or 'PEQUE' in raw or 'MES' in raw or 'PYME' in raw: return 'PYME'
    if 'MED' in raw or 'CORP' in raw or 'NO_MIN' in raw or 'COMERC' in raw: return 'NO_MINORISTA'
    return 'CONSUMO' # Default to CONSUMO as requested

def clean_decimal_latam(val):
    if pd.isna(val) or val is None: return Decimal('0.00')
    if isinstance(val, (int, float, Decimal)): return Decimal(str(val))
    s = str(val).replace('S/', '').replace('$', '').strip()
    if not s or s.lower() == 'nan': return Decimal('0.00')
    dot_count = s.count('.')
    comma_count = s.count(',')
    try:
        if dot_count > 0 and comma_count > 0:
            dot_idx = s.rfind('.')
            comma_idx = s.rfind(',')
            if comma_idx > dot_idx:
                s = s.replace('.', '').replace(',', '.')
            else:
                s = s.replace(',', '')
        elif dot_count > 1: s = s.replace('.', '')
        elif comma_count > 1: s = s.replace(',', '')
        elif comma_count == 1:
            parts = s.split(',')
            if len(parts[-1]) <= 2: s = s.replace(',', '.')
            else: s = s.replace(',', '')
        return Decimal(s)
    except: return Decimal('0.00')

def parse_date(val):
    if pd.isna(val) or val is None or str(val).strip().lower() in ('', 'nan', 'none', 'nat'): return None
    if isinstance(val, (datetime, date)): return val if isinstance(val, date) else val.date()
    try:
        if isinstance(val, (int, float)) and 30000 < val < 60000:
            return pd.to_datetime(val, unit='D', origin='1899-12-30').date()
        if str(val).isdigit() and 30000 < int(val) < 60000:
            return pd.to_datetime(int(val), unit='D', origin='1899-12-30').date()
        return pd.to_datetime(val, dayfirst=True).date()
    except: return None

def dashboard(request):
    context = {'page_title': 'Utilitarios y Herramientas del Sistema'}
    return render(request, 'utilities/dashboard.html', context)

def download_credit_template(request):
    cols = ['N', 'NCL', 'FNAC', 'GEN', 'EC', 'EMP', 'CSOC', 'PR', 'TID', 'NID', 'TPER', 'DOM', 'RCO', 'CAL', 'CALINT', 'CAGE', 'MON', 'CCR', 'TCR', 'STCR', 'FOT', 'MORG', 'TEA', 'SKCR', 'CC', 'KVI', 'KRE', 'KRF', 'KVE', 'KJU', 'KCO', 'CCO', 'DAK', 'SGP', 'SGA', 'PVR', 'PCI', 'SCC', 'CCC', 'SIN', 'SIS', 'SID', 'TPR', 'NCPR', 'NCPA', 'PCUO', 'DGR', 'FVGO', 'FVGA', 'SSC', 'SSG', 'SCR', 'SKCO', 'SCOR', 'SINC', 'SCS', 'CORTE']
    import pandas as pd
    import io
    from django.http import FileResponse
    
    df = pd.DataFrame(columns=cols)
    example = {c: '' for c in cols}
    example['N'] = '1'
    example['NCL'] = 'PEREZ SOSA JUAN'
    example['CSOC'] = '12345'
    example['CCR'] = 'CRED-001'
    example['MORG'] = 10000.00
    df = pd.concat([df, pd.DataFrame([example])], ignore_index=True)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Plantilla_Creditos')
    
    output.seek(0)
    return FileResponse(output, as_attachment=True, filename='plantilla_carga_creditos_v4.xlsx')

def download_liability_template(request):
    cols = [
        'AGENCIA', 'A.G.APERTURA', 'COD.SOCIO', 'APELLIDOS Y NOMBRES', 'EDAD', 
        'SEXO', 'FECHA NACIMIENTO', 'FECHA APERTURA', 'FECHA VENCIMIENTO', 
        'NRO CUENTA', 'PRODUCTO', 'MONEDA', 'MONTO', 'SALDO', 'TEA', 'TEM', 
        'PLAZO', 'USUARIO CREA', 'CAPTADOR', 'FECHA CANCELACION', 'PERIODO'
    ]
    df = pd.DataFrame(columns=cols)
    example = {
        'AGENCIA': 'PRINCIPAL', 'A.G.APERTURA': 'PRINCIPAL', 'COD.SOCIO': '12345', 
        'APELLIDOS Y NOMBRES': 'PEREZ SOSA JUAN', 'EDAD': 35, 'SEXO': 'M', 
        'FECHA NACIMIENTO': '1989-05-15', 'FECHA APERTURA': '2024-01-10', 
        'FECHA VENCIMIENTO': '2025-01-10', 'NRO CUENTA': 'DPF-001234', 
        'PRODUCTO': 'PLAZO FIJO MN', 'MONEDA': 'MN', 'MONTO': 10000.00, 'SALDO': 10000.00, 
        'TEA': 7.5, 'TEM': 0.60, 'PLAZO': 360, 'USUARIO CREA': 'ADMIN', 
        'CAPTADOR': 'ASESOR 1', 'PERIODO': '2024-12'
    }
    df = pd.concat([df, pd.DataFrame([example])], ignore_index=True)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Plantilla_Pasivos')
    response = HttpResponse(output.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=plantilla_pasivos_arisk.xlsx'
    return response

def download_liability_csv(request):
    return download_liability_template(request)

def export_credit_data(request):
    from credit_risk.models import CarteraCreditoCarga
    import pandas as pd
    import io
    
    load_date = request.GET.get('load_date')
    qs = CarteraCreditoCarga.objects.all()
    if load_date:
        qs = qs.filter(fecha_corte=load_date)
        
    cols = ['N', 'NCL', 'FNAC', 'GEN', 'EC', 'EMP', 'CSOC', 'PR', 'TID', 'NID', 'TPER', 'DOM', 'RCO', 'CAL', 'CALINT', 'CAGE', 'MON', 'CCR', 'TCR', 'STCR', 'FOT', 'MORG', 'TEA', 'SKCR', 'CC', 'KVI', 'KRE', 'KRF', 'KVE', 'KJU', 'KCO', 'CCO', 'DAK', 'SGP', 'SGA', 'PVR', 'PCI', 'SCC', 'CCC', 'SIN', 'SIS', 'SID', 'TPR', 'NCPR', 'NCPA', 'PCUO', 'DGR', 'FVGO', 'FVGA', 'SSC', 'SSG', 'SCR', 'SKCO', 'SCOR', 'SINC', 'SCS', 'CORTE']
    
    # Obtenemos los datos directamente de la base de datos (Ultra rápido, sin instanciar objetos ORM)
    records = qs.values_list(
        'n', 'ncl', 'fnac', 'gen', 'ec', 'emp', 'csoc', 'pr', 'tid', 'nid', 'tper', 'dom', 'rco', 'cal', 'calint', 'cage', 'mon', 'ccr', 'tcr', 'stcr', 'fot', 'morg', 'tea', 'skcr', 'cc', 'kvi', 'kre', 'krf', 'kve', 'kju', 'kco', 'cco', 'dak', 'sgp', 'sga', 'pvr', 'pci', 'scc', 'ccc', 'sin', 'sis', 'sid', 'tpr', 'ncpr', 'ncpa', 'pcuo', 'dgr', 'fvgo', 'fvga', 'ssc', 'ssg', 'scr', 'skco', 'scor', 'sinc', 'scs', 'fecha_corte'
    )
    
    # Creamos el DataFrame directamente
    df = pd.DataFrame.from_records(records, columns=cols)
    
    # Convertimos los Decimal/Date a string o float si es necesario para Excel
    for c in ['MORG', 'TEA', 'SKCR', 'KVI', 'KRE', 'KRF', 'KVE', 'KJU', 'KCO', 'SGP', 'SGA', 'PVR', 'PCI', 'SCC', 'SIN', 'SIS', 'SID', 'SSC', 'SSG', 'SCR', 'SKCO', 'SINC', 'SCS']:
        df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
        
    for c in ['FNAC', 'FOT', 'FVGO', 'FVGA', 'CORTE']:
        df[c] = pd.to_datetime(df[c], errors='coerce').dt.strftime('%Y-%m-%d')
        
    # En lugar de Excel, usamos CSV que procesa 100,000 registros en < 1 segundo
    # y es 100% compatible con Excel sin causar colapsos de memoria.
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="exportacion_cartera_creditos.csv"'
    
    # Escribimos directo al response
    df.to_csv(response, index=False, sep=';', encoding='utf-8-sig')
    return response

def export_liability_data(request):
    return HttpResponse("Exportación no disponible temporalmente.")

def parse_date(date_val):
    if pd.isna(date_val) or date_val is None or str(date_val).strip().lower() in ('', 'nan', 'none', 'nat'): return None
    if isinstance(date_val, (datetime, date)): return date_val if isinstance(date_val, date) else date_val.date()
    try:
        if isinstance(date_val, (int, float)) and 30000 < date_val < 60000:
            return pd.to_datetime(date_val, unit='D', origin='1899-12-30').date()
        if str(date_val).isdigit() and 30000 < int(date_val) < 60000:
            return pd.to_datetime(int(date_val), unit='D', origin='1899-12-30').date()
        return pd.to_datetime(date_val, dayfirst=True).date()
    except: return None

def clean_decimal(val):
    if pd.isna(val) or val == '': return 0
    try:
        if isinstance(val, str):
            val = val.replace('S/', '').replace('$', '').replace(',', '').strip()
            if not val: return 0
        return float(val)
    except: return 0

def bulk_load_credit(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES.get('file')
        manual_date_str = request.POST.get('load_date')
        
        try:
            # Read file
            if file.name.endswith('.xlsx') or file.name.endswith('.xls'):
                xl = pd.ExcelFile(file)
                all_dfs = []
                for sheet_name in xl.sheet_names:
                    temp_df = xl.parse(sheet_name, dtype=str)
                    if not temp_df.empty:
                        temp_df['_sheet_name'] = sheet_name
                        all_dfs.append(temp_df)
                if all_dfs:
                    df = pd.concat(all_dfs, ignore_index=True)
                else:
                    df = pd.DataFrame()
            else:
                try:
                    df = pd.read_csv(file, dtype=str)
                except UnicodeDecodeError:
                    file.seek(0)
                    df = pd.read_csv(file, encoding='latin-1', dtype=str)
            
            # Normalize column names
            import unicodedata
            df.columns = [
                unicodedata.normalize('NFKD', str(c)).encode('ASCII', 'ignore').decode('utf-8').strip().upper().replace(' ', '_').replace('.', '_')
                for c in df.columns
            ]
            
            # 1. Identify Cut-off Dates
            cut_off_col = 'CORTE' if 'CORTE' in df.columns else None
            
            dates = []
            if cut_off_col:
                for d in df[cut_off_col].unique():
                    if pd.isna(d) or str(d).strip() in ('', '0', '0.0', 'NaN', 'NaT', 'None'): continue
                    try:
                        if isinstance(d, (int, float)) and 30000 < d < 60000:
                            dt = pd.to_datetime(d, unit='D', origin='1899-12-30')
                        elif str(d).isdigit() and 30000 < int(d) < 60000:
                            dt = pd.to_datetime(int(d), unit='D', origin='1899-12-30')
                        else:
                            dt = pd.to_datetime(d, dayfirst=True)
                        if dt.year > 1990:
                            dates.append(dt.date())
                    except: pass
                dates = list(set(dates))
            
            if not dates and manual_date_str:
                dates = [datetime.strptime(manual_date_str, '%Y-%m-%d').date()]

            if not dates:
                messages.error(request, "No se identificaron fechas de corte válidas en el archivo y no se especificó una manualmente.")
                return redirect('utilities:bulk_load_credit')

            with open('debug_load.log', 'a', encoding='utf-8') as f:
                f.write(f"--- NUEVA CARGA: {file.name} ---\n")

            # Cache
            all_doc_ids = [str(x) for x in df['NID'].dropna().unique() if str(x).strip() != ''] if 'NID' in df.columns else []
            customers_cache = {c.document_id: c for c in Customer.objects.filter(document_id__in=all_doc_ids)}
            
            if cut_off_col:
                df['_temp_date'] = pd.to_datetime(df[cut_off_col], dayfirst=True, errors='coerce').dt.date
            
            total_records = 0
            
            from credit_risk.models import CarteraCreditoCarga
            
            for d in dates:
                with transaction.atomic():
                    period_df = df[df['_temp_date'] == d] if cut_off_col else df
                    
                    CreditOperation.objects.filter(load_date=d).delete()
                    CarteraCreditoCarga.objects.filter(fecha_corte=d).delete()
                    
                    carga_accumulator = []
                    ops_to_create = []
                    rows = period_df.to_dict('records')
                    
                    new_customers = []
                    for row in rows:
                        doc_id = str(row.get('NID', '')).strip()
                        if '.' in doc_id: doc_id = doc_id.split('.')[0]
                        if doc_id and doc_id.upper() not in ['NAN', 'NONE', '', '<NA>'] and doc_id not in customers_cache:
                            c = Customer(
                                document_id=doc_id, 
                                name=str(row.get('NCL', '')).strip().upper()[:255],
                                external_id=str(row.get('CSOC', '')).strip()[:50]
                            )
                            new_customers.append(c)
                            customers_cache[doc_id] = c
                    
                    if new_customers:
                        Customer.objects.bulk_create(new_customers, ignore_conflicts=True)
                        for c in Customer.objects.filter(document_id__in=[nc.document_id for nc in new_customers]):
                            customers_cache[c.document_id] = c
                    
                    cust_op_counter = {}
                    
                    for row in rows:
                        doc_id = str(row.get('NID', '')).strip()
                        if '.' in doc_id: doc_id = doc_id.split('.')[0]
                        if doc_id.upper() in ['NAN', 'NONE', '', '<NA>']: continue
                        
                        customer = customers_cache.get(doc_id)
                        if not customer: continue
                        
                        op_code = str(row.get('CCR', "")).strip()
                        if op_code.upper() in ['NAN', 'NONE', '', '0', '<NA>']:
                            cust_op_counter[customer.id] = cust_op_counter.get(customer.id, 0) + 1
                            op_code = f"OP-{doc_id}-{cust_op_counter[customer.id]}"
                        
                        # Instanciar el Staging
                        carga = CarteraCreditoCarga(
                            fecha_corte=d,
                            n=str(row.get('N', '')).strip()[:50],
                            ncl=str(row.get('NCL', '')).strip()[:255],
                            fnac=parse_date(row.get('FNAC')),
                            gen=str(row.get('GEN', '')).strip()[:50],
                            ec=str(row.get('EC', '')).strip()[:50],
                            emp=str(row.get('EMP', '')).strip()[:255],
                            csoc=str(row.get('CSOC', '')).strip()[:50],
                            pr=str(row.get('PR', '')).strip()[:50],
                            tid=str(row.get('TID', '')).strip()[:50],
                            nid=doc_id,
                            tper=str(row.get('TPER', '')).strip()[:50],
                            dom=str(row.get('DOM', '')).strip()[:500],
                            rco=str(row.get('RCO', '')).strip()[:50],
                            cal=str(row.get('CAL', '')).strip()[:50],
                            calint=str(row.get('CALINT', '')).strip()[:50],
                            cage=str(row.get('CAGE', '')).strip()[:50],
                            mon=str(row.get('MON', '')).strip()[:50],
                            ccr=op_code,
                            tcr=str(row.get('TCR', '')).strip()[:100],
                            stcr=str(row.get('STCR', '')).strip()[:100],
                            fot=parse_date(row.get('FOT')),
                            morg=clean_decimal_latam(row.get('MORG', 0)),
                            tea=clean_decimal_latam(row.get('TEA', 0)),
                            skcr=clean_decimal_latam(row.get('SKCR', 0)),
                            cc=str(row.get('CC', '')).strip()[:50],
                            kvi=clean_decimal_latam(row.get('KVI', 0)),
                            kre=clean_decimal_latam(row.get('KRE', 0)),
                            krf=clean_decimal_latam(row.get('KRF', 0)),
                            kve=clean_decimal_latam(row.get('KVE', 0)),
                            kju=clean_decimal_latam(row.get('KJU', 0)),
                            kco=clean_decimal_latam(row.get('KCO', 0)),
                            cco=str(row.get('CCO', '')).strip()[:50],
                            dak=int(clean_decimal_latam(row.get('DAK', 0))),
                            sgp=clean_decimal_latam(row.get('SGP', 0)),
                            sga=clean_decimal_latam(row.get('SGA', 0)),
                            pvr=clean_decimal_latam(row.get('PVR', 0)),
                            pci=clean_decimal_latam(row.get('PCI', 0)),
                            scc=clean_decimal_latam(row.get('SCC', 0)),
                            ccc=str(row.get('CCC', '')).strip()[:50],
                            sin=clean_decimal_latam(row.get('SIN', 0)),
                            sis=clean_decimal_latam(row.get('SIS', 0)),
                            sid=clean_decimal_latam(row.get('SID', 0)),
                            tpr=str(row.get('TPR', '')).strip()[:50],
                            ncpr=int(clean_decimal_latam(row.get('NCPR', 0))),
                            ncpa=int(clean_decimal_latam(row.get('NCPA', 0))),
                            pcuo=str(row.get('PCUO', '')).strip()[:50],
                            dgr=str(row.get('DGR', '')).strip()[:50],
                            fvgo=parse_date(row.get('FVGO')),
                            fvga=parse_date(row.get('FVGA')),
                            ssc=clean_decimal_latam(row.get('SSC', 0)),
                            ssg=clean_decimal_latam(row.get('SSG', 0)),
                            scr=clean_decimal_latam(row.get('SCR', 0)),
                            skco=clean_decimal_latam(row.get('SKCO', 0)),
                            scor=str(row.get('SCOR', '')).strip()[:50],
                            sinc=clean_decimal_latam(row.get('SINC', 0)),
                            scs=clean_decimal_latam(row.get('SCS', 0)),
                            asesor=str(row.get('ASESOR', '')).strip()[:255]
                        )
                        carga_accumulator.append(carga)
                        
                        # Active Portfolio
                        op = CreditOperation(
                            operation_code=op_code,
                            customer=customer,
                            load_date=d,
                            disbursement_date=carga.fot,
                            original_amount=carga.morg,
                            rate=carga.tea,
                            balance=carga.skcr,
                            days_past_due=carga.dak,
                            sbs_classification=carga.calint,
                            agency=carga.cage,
                            advisor=carga.asesor,
                            product_name=carga.tpr,
                            credit_type=carga.tcr,
                            # Map additional fields from excel
                            required_provision=carga.pvr,
                            established_provision=carga.pci,
                            refinanced_current=carga.krf,
                            restructured_current=carga.kre,
                            current_portfolio=carga.kvi,
                            past_due_portfolio=carga.kve,
                            judicial_portfolio=carga.kju,
                            is_refinanced=(carga.krf > 0)
                        )
                        ops_to_create.append(op)
                        
                    if carga_accumulator:
                        CarteraCreditoCarga.objects.bulk_create(carga_accumulator, batch_size=2000)
                    if ops_to_create:
                        CreditOperation.objects.bulk_create(ops_to_create, batch_size=2000)
                        
                    total_records += len(ops_to_create)
            
            status = 'Success' if total_records > 0 else 'Warning'
            error_msg = ''
            
        except Exception as e:
            status = 'Error'
            error_msg = str(e)
            dates = []
            total_records = 0
            import traceback
            traceback.print_exc()
            
        # Log Result
        log = BulkLoadLog.objects.create(
            load_type='Credit',
            file_name=file.name,
            records_processed=total_records,
            status=status,
            error_message=error_msg,
            cut_off_dates=','.join(sorted([d.strftime('%Y-%m-%d') for d in dates])) if dates else ''
        )
        
        if status == 'Success':
            messages.success(request, f"Se procesaron {total_records} registros correctamente.")
        elif status == 'Warning':
            messages.warning(request, "El archivo se leyó pero 0 registros fueron guardados. Revise la estructura.")
        else:
            messages.error(request, f"Error procesando archivo: {error_msg}")
            
        return redirect('utilities:bulk_load_credit')
    
    # GET context
    history = BulkLoadLog.objects.filter(load_type='Credit').order_by('-load_date')[:50]
    return render(request, 'utilities/credit_bulk_load.html', {'history': history, 'page_title': 'Carga Masiva - Cartera de Créditos'})
from django.db import transaction
from calendar import monthrange
from datetime import datetime, date

def parse_period_to_date(val, base_date=None):
    if pd.isna(val) or val == '' or str(val).strip() == '-': return None
    if isinstance(val, (datetime, date)):
        d = val if isinstance(val, date) else val.date()
        return d
    
    s = str(val).strip().upper()
    try:
        # YYYY-MM or YYYY/MM -> Last day of month
        if re.match(r'^\d{4}[-/]\d{2}$', s):
            sep = '-' if '-' in s else '/'
            y, m = s.split(sep)
            last_day = monthrange(int(y), int(m))[1]
            return date(int(y), int(m), last_day)
        
        # YYYY-MM-DD
        if re.match(r'^\d{4}[-/]\d{2}[-/]\d{2}$', s):
            return pd.to_datetime(s).date()
        
        # DD/MM/YYYY
        if re.match(r'^\d{2}[-/]\d{2}[-/]\d{4}$', s):
            return pd.to_datetime(s, dayfirst=True).date()
    except: pass
    
    # Try generic pandas parse
    try:
        return pd.to_datetime(s).date()
    except:
        return None

def get_liquidity_band(days):
    if days is None: return "1M" # Default for savings or unknown
    if days <= 30: return "1M"
    if days <= 60: return "2M"
    if days <= 90: return "3M"
    if days <= 120: return "4M"
    if days <= 150: return "5M"
    if days <= 180: return "6M"
    if days <= 270: return "7-9 M"
    if days <= 360: return "10-12 M"
    if days <= 720: return "Más de 1A a 2A"
    return "Más de 2A a 5A"

def clean_decimal_latam(val):
    if pd.isna(val) or val == '' or val is None: return Decimal('0')
    if isinstance(val, (int, float, Decimal)): return Decimal(str(val))
    try:
        s = str(val).strip().replace(',', '')
        return Decimal(s)
    except:
        return Decimal('0')

def get_col_robust(options, existing_cols):
    for opt in options:
        if opt in existing_cols:
            return opt
    # Búsqueda robusta (case-insensitive y parcial)
    for opt in options:
        for col in existing_cols:
            if opt.upper() in str(col).upper():
                return col
    return None

def to_date_only(val):
    if val is None or pd.isna(val): return None
    if hasattr(val, 'date'): return val.date()
    if isinstance(val, (datetime, date)):
        return val if isinstance(val, date) else val.date()
    try:
        return pd.to_datetime(val).date()
    except:
        return None

def map_productos_pasivo(producto):
    if not producto: return "OTRO"
    p = str(producto).strip().upper()
    if p in ["AHORRO PROGRAMADO DIARIA", "KIDS", "DIARIA", "SEMANAL", "QUINCENAL", "MENSUAL", "AHORRO PROGRAMADO SEMANAL", "AHORRO PROGRAMADO QUINCENAL", "AHORRO PROGRAMADO MENSUAL", "AHORRO PROGRAMADO KIDS"]:
        return "PROGRAMADO"
    elif p in ["CUENTA LIBRE", "LIBRE", "AHORRO LIBRE", "CUENTA KIDS", "INTERES DPF", "INTERESES DEPOSITO A PLAZO"]:
        return "CTA LIBRE"
    elif p in ["PLAZO FIJO 90", "PLAZO FIJO 180", "PLAZO FIJO 270", "PLAZO FIJO 540", "PLAZO FIJO 720", "PLAZO FIJO 1080", "PLAZO FIJO 360"]:
        return "DEPOSITOS A PLAZO"
    return "OTRO"

def map_adm_agen_pasivo(ofic_apertura):
    if not ofic_apertura: return None
    o = str(ofic_apertura).strip().upper()
    if o == "AG. AGUAYTIA": return "ADM-WDAZA"
    elif o == "AG. ATALAYA": return "ADM-RDAVILA"
    elif o == "AG. AUCAYACU": return "ADM-SIN DEFINIR"
    elif o == "AG. HUÁNUCO": return "ADM-JCUADROS"
    elif o == "AG. LA MERCED": return "ADM-LCHUQUIYAURI"
    elif o == "AG. PANGOA": return "ADM-MALLCCA"
    elif o == "AG. PICHANAKI": return "ADM-GGAGO"
    elif o == "AG. SATIPO": return "ADM-MMARAVI"
    elif o == "AG. TINGO MARIA": return "ADM-PHERRERA"
    elif o == "AG. VILLA RICA": return "ADM-HHUAMANI"
    return None

def bulk_load_liability(request):
    from liquidity_risk.models import LiqLiabilityDetail, CarteraPasivoCarga
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES.get('file')
        import traceback
        try:
            # Debug logging disabled to avoid file I/O issues
# with open('debug_load.log', 'a', encoding='utf-8') as f:
#     f.write(f"\n--- INICIANDO CARGA PASIVOS: {file.name} ---\n")
            # 1. Leer archivo
            all_dfs = []
            if file.name.endswith('.xlsx') or file.name.endswith('.xls'):
                xl = pd.ExcelFile(file)
                for sheet_name in xl.sheet_names:
                    temp_df = xl.parse(sheet_name)
                    if not temp_df.empty:
                        temp_df['_sheet_name'] = sheet_name
                        all_dfs.append(temp_df)
            else:
                try:
                    all_dfs.append(pd.read_csv(file))
                except UnicodeDecodeError:
                    file.seek(0)
                    all_dfs.append(pd.read_csv(file, encoding='latin-1'))

            if not all_dfs:
                messages.error(request, "El archivo está vacío.")
                return redirect('utilities:bulk_load_liability')

            records_count = 0
            cleared_periods = set() 

            for df in all_dfs:
                df_cols = list(df.columns)
                
                # Detección de Columnas
                col_id = get_col_robust(['COD.SOCIO', 'SOCIO', 'ID', 'ID_SOCIO', 'CLIENTE', 'CODIGO'], df_cols)
                col_acc = get_col_robust(['NRO CUENTA', 'NRO_CUENTA', 'CUENTA', 'CERTIFICADO'], df_cols)
                col_name = get_col_robust(['APELLIDOS Y NOMBRES', 'APELLIDOS_Y_NOMBRES', 'NOMBRE', 'CLIENTE'], df_cols)
                col_prod = get_col_robust(['PRODUCTO', 'DESC_PRODUCTO', 'TIPO_PRODUCTO'], df_cols)
                col_moneda = get_col_robust(['MONEDA', 'DIVISA', 'MON'], df_cols)
                col_monto = get_col_robust(['MONTO', 'VALOR', 'IMPORTE'], df_cols)
                col_saldo = get_col_robust(['SALDO', 'BALANCE'], df_cols)
                col_tea = get_col_robust(['TEA', 'TASA'], df_cols)
                col_tem = get_col_robust(['TEM'], df_cols)
                col_term = get_col_robust(['PLAZO', 'DIAS', 'MESES'], df_cols)
                col_agency = get_col_robust(['AGENCIA', 'OFICINA', 'SUCURSAL'], df_cols)
                col_agency_open = get_col_robust(['A.G.APERTURA', 'AGENCIA_APERTURA'], df_cols)
                col_birth = get_col_robust(['FECHA NACIMIENTO', 'FECHA_NACIMIENTO', 'NACIMIENTO'], df_cols)
                col_open = get_col_robust(['FECHA APERTURA', 'FECHA_APERTURA', 'APERTURA'], df_cols)
                col_due = get_col_robust(['FECHA VENCIMIENTO', 'FECHA_VENCIMIENTO', 'VENCIMIENTO'], df_cols)
                col_age = get_col_robust(['EDAD', 'AGE'], df_cols)
                col_gender = get_col_robust(['SEXO', 'GENDER'], df_cols)
                col_user_crea = get_col_robust(['USUARIO CREA', 'USUARIO_CREA'], df_cols)
                col_captador = get_col_robust(['CAPTADOR'], df_cols)
                col_segment = get_col_robust(['SEGMENTO', 'TIPO SOCIO', 'PERSONA', 'TIPO_SOCIO'], df_cols)
                col_cancel = get_col_robust(['FECHA CANCELACION', 'FECHA_CANCELACION', 'CANCELACION'], df_cols)
                col_period = get_col_robust(['PERIODO', 'FECHA_CORTE', 'CORTE', 'FECHA CIERRE', 'FECHA_CIERRE'], df_cols)

                if not col_period:
                    # Debug logging disabled for missing period column
# with open('debug_load.log', 'a', encoding='utf-8') as f:
#     f.write(f"Hoja {df['_sheet_name'].iloc[0]}: No se detectó columna de PERIODO. Columnas: {df_cols}\n")
                    messages.warning(request, f"La hoja {df['_sheet_name'].iloc[0]} no tiene columna de PERIODO. Se ignoró.")
                    continue

                df['_temp_date'] = df[col_period].apply(lambda x: parse_period_to_date(x))
                
                # Convertir a lista de objetos date puros
                tab_dates = [to_date_only(x) for x in df['_temp_date'].dropna().unique()]

                # Debug logging disabled for column and date info
# with open('debug_load.log', 'a', encoding='utf-8') as f:
#     f.write(f"Columnas Detectadas: ID={col_id}, Acc={col_acc}, Period={col_period}, Due={col_due}\n")
#     f.write(f"Fechas detectadas en la columna {col_period}: {df[col_period].unique()[:5]}\n")
#     f.write(f"Fechas parseadas (unicas): {tab_dates}\n")
                
                for d in tab_dates:
                    with transaction.atomic():
                        if d not in cleared_periods:
                            cleared_periods.add(d)
                            LiqLiabilityDetail.objects.filter(period=d).delete()
                            CarteraPasivoCarga.objects.filter(fecha_corte=d).delete()

                        period_df = df[df['_temp_date'].apply(to_date_only) == d]
                        rows = period_df.to_dict('records')
                        
                        to_create = []
                        to_create_carga = []
                        for row in rows:
                            acc_num = str(row.get(col_acc, '')).strip()
                            if '.' in acc_num: acc_num = acc_num.split('.')[0]
                            if not acc_num or acc_num.upper() in ['0', 'NAN', 'N/A', 'NONE', '']: continue
                            
                            monto = clean_decimal_latam(row.get(col_monto, 0))
                            saldo = clean_decimal_latam(row.get(col_saldo, monto))
                            
                            f_venc = to_date_only(row.get(col_due))
                            f_canc = to_date_only(row.get(col_cancel))
                            f_open = to_date_only(row.get(col_open, d))
                            f_birth = to_date_only(row.get(col_birth))
                            
                            # Regla Crítica de Clasificación
                            if f_venc:
                                rubro = "Obligaciones por cuentas a plazo"
                                tipo = "PLAZO"
                            else:
                                rubro = "Obligaciones por cuentas de ahorro"
                                tipo = "AHORRO"
                            
                            # Estado
                            d_date = to_date_only(d)
                            f_canc_date = to_date_only(f_canc)

                            if not f_canc_date or f_canc_date > d_date:
                                estado = "VIGENTE"
                            else:
                                estado = "CANCELADO"
                                
                            # Días y Banda
                            dias_venc = None
                            if f_venc:
                                dias_venc = (f_venc - d).days
                            
                            banda = "1M"
                            if tipo == "PLAZO" and estado == "VIGENTE":
                                banda = get_liquidity_band(dias_venc)
                            
                            # Observaciones
                            is_obs = False
                            obs_det = ""
                            if f_venc and f_venc < d and estado == "VIGENTE":
                                is_obs = True
                                obs_det = "Vencimiento expirado no regularizado."

                            to_create.append(LiqLiabilityDetail(
                                period=d,
                                agency=str(row.get(col_agency, 'SIN AGENCIA')).strip().upper(),
                                customer_name=str(row.get(col_name, 'SIN NOMBRE')).strip().upper(),
                                funding_type=tipo,
                                liquidity_item=rubro,
                                currency=str(row.get(col_moneda, 'MN')).strip().upper(),
                                balance=saldo,
                                liquidity_band=banda
                            ))

                            # Cálculos para CarteraPasivoCarga
                            of_val = str(row.get(get_col_robust(['OF'], df_cols) or 'Of', '')).strip()
                            socio_val = str(row.get(col_name, '')).strip()
                            ofic_ap_val = str(row.get(col_agency_open, '')).strip()
                            usuario_val = str(row.get(col_user_crea, '')).strip()
                            captador_val = str(row.get(col_captador, '')).strip()
                            producto_val = str(row.get(col_prod, '')).strip()
                            id_socio_val = str(row.get(col_id, '')).strip()
                            id_ahorro_val = str(row.get(get_col_robust(['IDAHORRO', 'ID AHORRO', 'ID_AHORRO'], df_cols) or 'IdAhorro', '')).strip()
                            
                            tim_val = clean_decimal_latam(row.get(col_tim if 'col_tim' in locals() else get_col_robust(['TIM'], df_cols), 0))
                            tea_val = clean_decimal_latam(row.get(col_tea, 0))
                            ult_mov_val = to_date_only(row.get(get_col_robust(['ULT. MOV.', 'ULT.MOV', 'ULT_MOV'], df_cols)))
                            
                            plz_val = row.get(col_term, 0)
                            try: plz_val = int(plz_val)
                            except: plz_val = 0
                            
                            ah_vinc_val = row.get(get_col_robust(['AH VINC', 'AH_VINC', 'AH. VINC.'], df_cols), 0)
                            try: ah_vinc_val = int(ah_vinc_val)
                            except: ah_vinc_val = 0
                            
                            mon_val = str(row.get(col_moneda, '')).strip()
                            
                            agencia_calc = ofic_ap_val.replace("AG.", "AGENCIA").strip()
                            cod_asesor = "CD-" + "".join([c for c in captador_val.upper() if not c.isdigit()])
                            producto_agrupado = map_productos_pasivo(producto_val)
                            
                            saldo_dpf = saldo if producto_agrupado == "DEPOSITOS A PLAZO" else 0
                            saldo_prog = saldo if producto_agrupado == "PROGRAMADO" else 0
                            saldo_ctas_libre = saldo if producto_agrupado == "CTA LIBRE" else 0
                            
                            trea = tea_val / Decimal('100.0')
                            plazo_dpf = plz_val if producto_agrupado == "DEPOSITOS A PLAZO" else 0
                            
                            if f_venc:
                                dias_restantes = (f_venc - d).days
                                p_vence2 = f"{dias_restantes} días restantes" if dias_restantes >= 0 else "Vencido"
                            else:
                                p_vence2 = "Vencido"
                                
                            adm_agen = map_adm_agen_pasivo(ofic_ap_val)
                            id_compuesto = f"{adm_agen}-{agencia_calc}" if adm_agen else f"None-{agencia_calc}"
                            
                            to_create_carga.append(CarteraPasivoCarga(
                                fecha_corte=d,
                                of=of_val,
                                id_socio=id_socio_val,
                                id_ahorro=id_ahorro_val,
                                socio=socio_val,
                                apertura=f_open,
                                ofic_apertura=ofic_ap_val,
                                usuario=usuario_val,
                                captador=captador_val,
                                producto=producto_val,
                                tim=tim_val,
                                tea=tea_val,
                                ult_mov=ult_mov_val,
                                vence=f_venc,
                                plz=plz_val,
                                ah_vinc=ah_vinc_val,
                                mon=mon_val,
                                saldo=saldo,
                                agencia_calc=agencia_calc,
                                cod_asesor=cod_asesor,
                                producto_agrupado=producto_agrupado,
                                saldo_dpf=saldo_dpf,
                                saldo_prog=saldo_prog,
                                saldo_ctas_libre=saldo_ctas_libre,
                                trea=trea,
                                plazo_dpf=plazo_dpf,
                                p_vence2=p_vence2,
                                adm_agen=adm_agen,
                                id_compuesto=id_compuesto
                            ))

                        if to_create:
                            LiqLiabilityDetail.objects.bulk_create(to_create, batch_size=2000)
                            CarteraPasivoCarga.objects.bulk_create(to_create_carga, batch_size=2000)
                            records_count += len(to_create)

            messages.success(request, f"Carga masiva procesada con éxito. {records_count} registros.")
            BulkLoadLog.objects.create(
                file_name=file.name, load_type='LIABILITY',
                cut_off_dates=",".join([str(d) for d in sorted(list(cleared_periods))]),
                records_processed=records_count, status='Success'
            )
            return redirect('utilities:bulk_load_liability')

        except Exception as e:
            with open('debug_load.log', 'a', encoding='utf-8') as f:
                f.write(f"ERROR EN CARGA PASIVOS: {str(e)}\n")
                f.write(traceback.format_exc() + "\n")
            messages.error(request, f"Error en la carga: {str(e)}")
            return redirect('utilities:bulk_load_liability')

    history = BulkLoadLog.objects.filter(load_type='LIABILITY').order_by('-load_date')
    return render(request, 'utilities/liability_bulk_load.html', {'history': history})


def delete_bulk_load_log(request, log_id):
    log = get_object_or_404(BulkLoadLog, id=log_id)
    if request.method == 'POST':
        # Determine redirect URL based on load type
        if log.load_type == 'CREDIT':
            redirect_url = 'utilities:bulk_load_credit'
        elif log.load_type == 'SOCIO':
            redirect_url = 'utilities:bulk_load_socios'
        else:
            redirect_url = 'utilities:bulk_load_liability'

        # Eliminar las operaciones asociadas a los cortes de este log
        if log.cut_off_dates:
            # Parse dates robustly to avoid ValidationError with different formats
            raw_dates = [d.strip() for d in log.cut_off_dates.split(',') if d.strip() and d.strip().upper() != 'N/A']
            dates = []
            for rd in raw_dates:
                # Handle possible smart quotes in string if they exist
                clean_rd = rd.replace('“', '').replace('”', '').replace('"', '').strip()
                parsed = parse_date(clean_rd)
                if parsed:
                    dates.append(parsed)
            
            if log.load_type == 'CREDIT':
                deleted_count, _ = CreditOperation.objects.filter(load_date__in=dates).delete()
            elif log.load_type == 'SOCIO':
                from .models import Socio
                deleted_count, _ = Socio.objects.filter(corte__in=dates).delete()
            else:
                # Removed associated Liq models delete
                deleted_count = 0
                
            messages.success(request, f"Se eliminó el log y {deleted_count} registros asociados.")
        else:
            messages.warning(request, "El log no tenía fechas de corte asociadas, solo se eliminó el registro del log.")
        
        log.delete()
        return redirect(redirect_url)
    
    # Fallback redirect
    if log.load_type == 'CREDIT':
        return redirect('utilities:bulk_load_credit')
    elif log.load_type == 'SOCIO':
        return redirect('utilities:bulk_load_socios')
    return redirect('utilities:bulk_load_liability')

def bulk_delete_logs(request):
    if request.method == 'POST':
        log_ids = request.POST.getlist('log_ids')
        if not log_ids:
            messages.warning(request, "No se seleccionaron cargas para eliminar.")
            return redirect(request.META.get('HTTP_REFERER', 'utilities:dashboard'))
            
        logs = BulkLoadLog.objects.filter(id__in=log_ids)
        total_deleted = 0
        
        for log in logs:
            if log.cut_off_dates:
                raw_dates = [d.strip() for d in log.cut_off_dates.split(',') if d.strip() and d.strip().upper() != 'N/A']
                dates = []
                for rd in raw_dates:
                    clean_rd = rd.replace('“', '').replace('”', '').replace('"', '').strip()
                    parsed = parse_date(clean_rd)
                    if parsed:
                        dates.append(parsed)
                
                if log.load_type == 'CREDIT':
                    deleted_count, _ = CreditOperation.objects.filter(load_date__in=dates).delete()
                elif log.load_type == 'SOCIO':
                    from .models import Socio
                    deleted_count, _ = Socio.objects.filter(corte__in=dates).delete()
                else:
                    from liquidity_risk.models import LiqLiabilityDetail
                    count3, _ = LiqLiabilityDetail.objects.filter(period__in=dates).delete()
                    deleted_count = count3
                    
                total_deleted += deleted_count
            log.delete()
            
        messages.success(request, f"Se eliminaron {len(log_ids)} cargas y {total_deleted} registros asociados.")
        return redirect(request.META.get('HTTP_REFERER', 'utilities:dashboard'))
    return redirect('utilities:dashboard')


def bulk_load_liability_detail(request, log_id):
    from liquidity_risk.models import LiqSavingsAccount, LiqTermDeposit
    log = get_object_or_404(BulkLoadLog, id=log_id)
    
    # Parse dates
    raw_dates = [d.strip() for d in (log.cut_off_dates or "").split(',') if d.strip() and d.strip().upper() != 'N/A']
    dates = []
    for rd in raw_dates:
        clean_rd = rd.replace('“', '').replace('”', '').replace('"', '').strip()
        parsed = parse_date(clean_rd)
        if parsed:
            dates.append(parsed)
            
    # Fetch bands for labelling
    from liquidity_risk.models import LiqTimeBand
    bands = list(LiqTimeBand.objects.all().order_by('order'))
    
    def get_band_label(p, d_date):
        if not d_date or not p: return "1M"
        days = (d_date - p).days
        for b in bands:
            if b.start_days <= days <= b.end_days:
                return b.name
        return "+1A" if days > 0 else "1M"
@login_required
def bulk_load_liability_detail(request, log_id):
    from liquidity_risk.models import LiqLiabilityDetail
    log = get_object_or_404(BulkLoadLog, id=log_id)
    dates = [d.strip() for d in log.cut_off_dates.split(',')]
    
    details = LiqLiabilityDetail.objects.filter(period__in=dates).order_by('agency', 'customer_name')
    
    # Resúmenes por Rubro y Moneda
    summary_rubro = details.values('liquidity_item', 'currency').annotate(
        count=Count('id'),
        total_balance=Sum('balance')
    ).order_by('liquidity_item', 'currency')

    # Resúmenes por Banda y Moneda
    summary_banda = details.values('liquidity_band', 'currency').annotate(
        count=Count('id'),
        total_balance=Sum('balance')
    ).order_by('liquidity_band', 'currency')

    # Totales para cards
    totals = details.values('currency').annotate(
        total_balance=Sum('balance')
    )
    total_mn = sum(t['total_balance'] for t in totals if t['currency'] == 'MN')
    total_me = sum(t['total_balance'] for t in totals if t['currency'] == 'ME')

    context = {
        'log': log,
        'details': details,
        'summary_rubro': summary_rubro,
        'summary_banda': summary_banda,
        'total_mn': total_mn,
        'total_me': total_me,
        'dates': dates,
        'page_title': f"Detalle de Carga: {log.file_name}"
    }
    
    return render(request, 'utilities/liability_detail.html', context)

# -----------------------------------------------------------------------------
# MIGRATED FROM LIQUIDITY RISK: BALANCE & MAPPING
# -----------------------------------------------------------------------------

@login_required
def download_balance_template(request):
    mode = request.GET.get('mode', 'single')
    
    if mode == 'massive':
        columns = ['Cuenta', 'Denominación', '2023-01-31', '2023-02-28', '2023-03-31']
        df = pd.DataFrame(columns=columns)
        df.loc[0] = ['110101', 'Caja Principal', '1500.50', '1600.00', '1550.20']
        filename = 'Plantilla_Balance_MASIVO.xlsx'
    else:
        columns = ['PERIODO', 'MONEDA', 'CODIGO CONTABLE', 'NOMBRE CUENTA', 'SALDO', 'NATURALEZA']
        df = pd.DataFrame(columns=columns)
        df.loc[0] = ['2026-03-01', 'MN', '110101', 'Caja Principal', '1500.50', 'DEUDORA']
        filename = 'Plantilla_Balance_ARISK.xlsx'
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Balance')
    
    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename={filename}'
    return response

@login_required
def load_balance(request):
    if request.method == 'POST':
        period = request.POST.get('period')
        file = request.FILES.get('file')
        plan_model_id = request.POST.get('plan_model')
        if file:
            plan_model = get_object_or_404(LiqAccountPlanModel, id=plan_model_id) if plan_model_id else None
            # If period is missing, use today as default (the loader will look for dates inside)
            target_period = period if period else now().date()
            
            upload, _ = LiqBalanceUpload.objects.update_or_create(
                period=target_period,
                defaults={
                    'status': LiqLoadStatus.PENDING
                }
            )
            if process_balance_load(upload.id):
                messages.success(request, "Proceso de carga iniciado correctamente.")
            else:
                messages.error(request, "Error al procesar el balance.")
        return redirect('utilities:load_balance')
        
    history = LiqBalanceUpload.objects.all().order_by('-period')
    all_models = LiqAccountPlanModel.objects.all()
    return render(request, 'liquidity_risk/loaders/load_balance.html', {
        'page_title': 'Carga de Balance de Comprobación',
        'history': history,
        'all_models': all_models
    })

@login_required
def delete_balance(request, upload_id):
    upload = get_object_or_404(LiqBalanceUpload, id=upload_id)
    if request.method == 'POST' or request.GET.get('confirm') == 'true':
        upload.delete()
        messages.success(request, "Carga eliminada correctamente.")
    return redirect('utilities:load_balance')

@login_required
def bulk_delete_balance_logs(request):
    from liquidity_risk.models import LiqBalanceUpload
    if request.method == 'POST':
        log_ids = request.POST.getlist('log_ids')
        if not log_ids:
            messages.warning(request, "No se seleccionaron cargas para eliminar.")
            return redirect('utilities:load_balance')
            
        logs = LiqBalanceUpload.objects.filter(id__in=log_ids)
        count = logs.count()
        logs.delete()
        messages.success(request, f"Se eliminaron {count} cargas de balance exitosamente.")
        
    return redirect('utilities:load_balance')

@login_required
def view_balance(request, upload_id):
    upload = get_object_or_404(LiqBalanceUpload, id=upload_id)
    details = upload.details.all().order_by('account_code')
    return render(request, 'liquidity_risk/loaders/view_balance_detail.html', {
        'page_title': f'Detalle de Balance - {upload.period.strftime("%m/%Y")}',
        'upload': upload,
        'details': details
    })

@login_required
def download_balance_data(request, upload_id):
    import csv
    from django.http import HttpResponse
    from liquidity_risk.models import LiqBalanceUpload
    
    upload = get_object_or_404(LiqBalanceUpload, id=upload_id)
    details = upload.details.all().order_by('account_code')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="balance_comprobacion_{upload.period.strftime("%Y%m")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Periodo', 'Cuenta', 'Saldo'])
    
    for row in details:
        writer.writerow([row.period.strftime("%Y-%m-%d"), row.account_code, row.balance])
        
    return response

def process_account_mapping_load(filepath, plan_model="ESTANDAR"):
    import pandas as pd
    try:
        from .models import LiqAccountPlanModel, LiqAccountMapping
        
        # Determine engine
        engine = 'openpyxl' if str(filepath).endswith('.xlsx') else None
        if not engine:
            df = pd.read_excel(filepath)
        else:
            df = pd.read_excel(filepath, engine=engine)
            
        if df.empty:
            return False, "El archivo está vacío."
            
        # Try to identify columns
        cols = [str(c).lower().strip() for c in df.columns]
        
        code_col, name_col, cat_col = None, None, None
        
        for i, c in enumerate(cols):
            if any(x in c for x in ['cuenta', 'codigo', 'code', 'código']):
                if not code_col: code_col = df.columns[i]
            if any(x in c for x in ['nombre', 'descripcion', 'name', 'descripción', 'denominacion', 'denominación']):
                if not name_col: name_col = df.columns[i]
            if any(x in c for x in ['categoria', 'tipo', 'clasificacion', 'category', 'categoría', 'rubro']):
                if not cat_col: cat_col = df.columns[i]
                
        if not code_col or not name_col:
            # Fallback to first 2 columns if not explicitly found
            if len(df.columns) >= 2:
                code_col, name_col = df.columns[0], df.columns[1]
                if len(df.columns) >= 3 and not cat_col:
                    cat_col = df.columns[2]
            else:
                return False, "No se pudieron identificar las columnas requeridas (Cuenta, Denominación)."
                
        # Get or create plan
        plan, _ = LiqAccountPlanModel.objects.get_or_create(name=plan_model)
        
        # Clear existing mappings for this plan
        LiqAccountMapping.objects.filter(plan_model=plan).delete()
        
        mappings_to_create = []
        for idx, row in df.iterrows():
            code = str(row[code_col]).strip() if pd.notna(row[code_col]) else ''
            if not code or code == 'nan': continue
            
            name = str(row[name_col]).strip() if pd.notna(row[name_col]) else ''
            cat = str(row[cat_col]).strip() if cat_col and pd.notna(row[cat_col]) else 'No Asignado'
            
            if len(code) > 50: code = code[:50]
            if len(name) > 255: name = name[:255]
            if len(cat) > 100: cat = cat[:100]
            
            # Infer account type based on first digit of code
            acc_type = 'OTR'
            if code.startswith('1'): acc_type = 'ACT'
            elif code.startswith('2'): acc_type = 'PAS'
            elif code.startswith('3'): acc_type = 'PAT'
            elif code.startswith('4'): acc_type = 'ING'
            elif code.startswith('5'): acc_type = 'GAS'
            
            # Infer currency (ME vs MN or from name)
            currency = 'PEN'
            if 'ME' in name.upper() or 'DOLARES' in name.upper() or 'DÓLARES' in name.upper() or 'EXTRANJERA' in name.upper():
                currency = 'USD'
                
            mappings_to_create.append(LiqAccountMapping(
                plan_model=plan,
                account_code=code,
                account_name=name,
                liquidity_category=cat,
                liquidity_item=cat,
                account_type=acc_type,
                currency=currency,
                distribution_rule='OTHER',
                data_source='BALANCE'
            ))
            
        if mappings_to_create:
            LiqAccountMapping.objects.bulk_create(mappings_to_create, batch_size=5000)
            return True, f"Se cargaron exitosamente {len(mappings_to_create)} cuentas al plan '{plan_model}'."
        else:
            return False, "No se encontraron registros válidos para cargar."
            
    except Exception as e:
        return False, f"Error al procesar el archivo: {str(e)}"

@login_required
def account_mapping(request):
    selected_model_name = request.GET.get('model', '').strip()
    
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES.get('file')
        plan_model_name = request.POST.get('plan_model', 'ESTANDAR').strip()
        import os
        from django.core.files.storage import default_storage
        path = default_storage.save('tmp/' + file.name, file)
        full_path = os.path.join(default_storage.location, path)
        
        success, msg = process_account_mapping_load(full_path, plan_model=plan_model_name)
        if success:
            messages.success(request, msg)
        else:
            messages.error(request, msg)
        
        if os.path.exists(full_path):
            os.remove(full_path)
        return redirect(f"{request.path}?model={plan_model_name}")

    # Ensure at least one model exists
    if not LiqAccountPlanModel.objects.exists():
        LiqAccountPlanModel.objects.create(name='ESTANDAR', description='Modelo base predefinido')

    # Get available models for dropdown
    available_models = LiqAccountPlanModel.objects.all().order_by('-created_at')
    
    if not selected_model_name:
        selected_model_name = available_models.first().name if available_models.exists() else 'ESTANDAR'
    
    mappings = LiqAccountMapping.objects.filter(plan_model__name=selected_model_name).order_by('account_code')
    
    # Summary of accounts per model
    model_stats = {m.name: LiqAccountMapping.objects.filter(plan_model=m).count() for m in available_models}
    
    return render(request, 'liquidity_risk/methodologies/account_mapping.html', {
        'page_title': 'Maestro de Cuentas (Plan de Cuentas)',
        'mappings': mappings,
        'selected_model': selected_model_name,
        'available_models': available_models,
        'model_stats': model_stats
    })

@login_required
def bulk_load_socios(request):
    from .models import Socio
    from django.core.management import call_command
    try:
        call_command('makemigrations', 'utilities', interactive=False)
        call_command('migrate', interactive=False)
    except Exception as e:
        print(f"Auto-migration failed: {e}")
        
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES.get('file')
        manual_date_str = request.POST.get('load_date')
        
        try:
            if file.name.endswith('.xlsx') or file.name.endswith('.xls'):
                xl = pd.ExcelFile(file)
                all_dfs = []
                for sheet_name in xl.sheet_names:
                    temp_df = xl.parse(sheet_name)
                    if not temp_df.empty:
                        temp_df['_sheet_name'] = sheet_name
                        all_dfs.append(temp_df)
                if all_dfs:
                    df = pd.concat(all_dfs, ignore_index=True)
                else:
                    df = pd.DataFrame()
            else:
                df = pd.read_csv(file)

            # Normalize column names for robust matching
            df.columns = [str(c).strip().upper().replace(' ', '_') for c in df.columns]

            # Detect Date Column
            cut_off_col = get_col_robust(['CORTE', 'FECHA_CORTE', 'FECHA_DE_CORTE', 'PERIODO'], df.columns)
            
            if cut_off_col:
                raw_dates = df[cut_off_col].unique()
                dates = []
                for d in raw_dates:
                    if not pd.isna(d):
                        try:
                            dates.append(pd.to_datetime(d).date())
                        except Exception:
                            pass
            elif manual_date_str:
                dates = [datetime.strptime(manual_date_str, '%Y-%m-%d').date()]
            else:
                messages.error(request, "Debe especificar una fecha de corte o incluirla en el archivo.")
                return redirect('utilities:bulk_load_socios')

            if not dates:
                messages.error(request, "No se identificaron fechas de corte válidas en el archivo.")
                return render(request, 'utilities/bulk_load_socios.html', {
                    'page_title': 'Error: No se identificaron fechas de corte válidas.',
                    'history': BulkLoadLog.objects.filter(load_type='SOCIO').order_by('-load_date'),
                })

            # Column detection based on new fields
            col_csocio = get_col_robust(['CSOCIO', 'CODIGO_SOCIO', 'CODIGO', 'CODIGO_CLIENTE'], df.columns)
            col_tid = get_col_robust(['TID', 'TIPO_SOCIO'], df.columns)
            col_nid = get_col_robust(['NID', 'DOCUMENTO', 'IDENTIFICACION', 'DNI', 'RUC'], df.columns)
            col_ncl = get_col_robust(['NCL', 'NOMBRES', 'RAZON_SOCIAL', 'SOCIO', 'CLIENTE'], df.columns)
            col_cond = get_col_robust(['CONDSOCIO', 'CONDICION', 'ESTADO'], df.columns)
            col_codofic = get_col_robust(['CODOFICINA', 'COD_OFICINA'], df.columns)
            col_oficina = get_col_robust(['OFICINA', 'AGENCIA', 'SUCURSAL'], df.columns)
            col_fingreso = get_col_robust(['FINGRESO', 'FECHA_INGRESO', 'INGRESO'], df.columns)
            col_aportes = get_col_robust(['APORTES', 'SALDO_APORTES', 'APORTACION'], df.columns)
            col_dir = get_col_robust(['DIRECCIÓN', 'DIRECCION', 'DOMICILIO'], df.columns)
            col_tel = get_col_robust(['TELEFONO', 'CELULAR'], df.columns)
            col_correo = get_col_robust(['CORREO', 'EMAIL'], df.columns)

            if cut_off_col:
                df['_temp_date'] = pd.to_datetime(df[cut_off_col], errors='coerce').dt.date

            total_records = 0
            for d in dates:
                with transaction.atomic():
                    period_df = df[df['_temp_date'] == d] if cut_off_col else df
                    
                    # Log object creation
                    log = BulkLoadLog.objects.create(
                        file_name=file.name,
                        load_type='SOCIO',
                        cut_off_dates=d.strftime('%Y-%m-%d'),
                        records_processed=0,
                        status='Pending'
                    )

                    # Replace old socio loads for this date
                    BulkLoadLog.objects.filter(load_type='SOCIO', cut_off_dates=d.strftime('%Y-%m-%d')).exclude(id=log.id).delete()
                    Socio.objects.filter(corte=d).delete()
                    
                    rows = period_df.to_dict('records')
                    to_create = []

                    for row in rows:
                        nid = str(row.get(col_nid, '')).strip()
                        if not nid or nid.upper() in ['NAN', 'NONE', '']: continue

                        aportes_val = clean_decimal_latam(row.get(col_aportes, 0))
                        if aportes_val <= 0: continue

                        try:
                            tid = int(clean_decimal_latam(row.get(col_tid, 1)))
                        except:
                            tid = 1

                        to_create.append(Socio(
                            csocio=str(row.get(col_csocio, '')).strip().upper(),
                            tid=tid,
                            nid=nid,
                            ncl=str(row.get(col_ncl, '')).strip().upper(),
                            condsocio=str(row.get(col_cond, '')).strip().upper(),
                            codoficina=str(row.get(col_codofic, '')).strip().upper(),
                            oficina=str(row.get(col_oficina, '')).strip().upper(),
                            fingreso=parse_date(row.get(col_fingreso)),
                            aportes=aportes_val,
                            direccion=str(row.get(col_dir, '')).strip().upper(),
                            telefono=str(row.get(col_tel, '')).strip().upper(),
                            correo=str(row.get(col_correo, '')).strip().lower(),
                            corte=d,
                            load_log=log
                        ))

                    if to_create:
                        Socio.objects.bulk_create(to_create, batch_size=2000)
                        total_records += len(to_create)
                        log.records_processed = len(to_create)
                        log.status = 'Success'
                        log.save()
                    else:
                        log.delete()

            if total_records == 0:
                messages.warning(request, "No se procesaron registros válidos.")
                return render(request, 'utilities/bulk_load_socios.html', {
                    'page_title': "Error: No se procesaron registros válidos. Revisa columnas y datos.",
                    'history': BulkLoadLog.objects.filter(load_type='SOCIO').order_by('-load_date'),
                })
            else:
                messages.success(request, f"Carga de socios completada. {total_records} registros procesados.")

            return redirect('utilities:bulk_load_socios')

        except Exception as e:
            import traceback
            messages.error(request, f"Error en la carga: {str(e)}")
            print(f"ERROR CARGA SOCIOS: {str(e)}\n{traceback.format_exc()}")
            return render(request, 'utilities/bulk_load_socios.html', {
                'page_title': f"Error en la carga: {str(e)}",
                'history': BulkLoadLog.objects.filter(load_type='SOCIO').order_by('-load_date'),
            })

    history = BulkLoadLog.objects.filter(load_type='SOCIO').order_by('-load_date')
    return render(request, 'utilities/bulk_load_socios.html', {
        'page_title': 'Carga Masiva - Base de Socios',
        'history': history,
        'today': timezone.now().date()
    })

@login_required
def download_socios_template(request):
    columns = [
        'CSOCIO', 'TID', 'NID', 'NCL', 'CONDSOCIO', 'CODOFICINA', 'OFICINA', 
        'FINGRESO', 'APORTES', 'DIRECCIÓN', 'TELEFONO', 'CORREO', 'CORTE'
    ]
    df = pd.DataFrame(columns=columns)
    df.loc[0] = ['S00001', 1, '0123456789', 'JUAN PEREZ', 'HABIL', '001', 'MATRIZ', '2023-01-01', 1500.50, 'AV. AMAZONAS', '099999999', 'juan@example.com', '2024-05-31']
    
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Plantilla_Socios')
    
    response = HttpResponse(output.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=plantilla_socios_arisk.xlsx'
    return response

@login_required
def bulk_load_socios_detail(request, log_id):
    from .models import Socio, BulkLoadLog
    from django.http import Http404
    from django.shortcuts import get_object_or_404, redirect
    from django.contrib import messages
    
    try:
        log = get_object_or_404(BulkLoadLog, id=log_id)
    except Http404:
        messages.warning(request, "El registro de carga que intentas ver ya no existe o fue eliminado.")
        return redirect('utilities:bulk_load_socios')
        
    socios = Socio.objects.filter(load_log=log).order_by('ncl')
    
    context = {
        'log': log,
        'socios': socios,
        'page_title': f"Detalle de Carga de Socios: {log.file_name}"
    }
    return render(request, 'utilities/socios_detail.html', context)

from liquidity_risk.models import LiqBalanceDetail

# --- POWER BI HELPER FUNCTIONS ---
def map_agencia_pbi(ofd):
    try:
        ofd_int = int(float(ofd))
        mapping = {
            1: "AGENCIA VILLA RICA", 2: "AGENCIA LA MERCED", 3: "AGENCIA PICHANAKI",
            4: "AGENCIA SATIPO", 5: "AGENCIA PANGOA", 6: "AGENCIA ATALAYA",
            7: "AGENCIA HUÁNUCO", 8: "AGENCIA TINGO MARIA", 9: "AGENCIA AGUAYTIA",
            10: "AGENCIA TOCACHE", 11: "AGENCIA AUCAYACU"
        }
        return mapping.get(ofd_int, "SIN DEFINIR")
    except:
        return "SIN DEFINIR"

def map_clasif_pbi(calific):
    calific = calific.upper() if calific else ""
    if "NORMAL" in calific: return "1-NORMAL"
    if "POTENCIAL" in calific: return "2-CPP"
    if "DEFICIENTE" in calific: return "3-DEFICIENTE"
    if "DUDOSO" in calific: return "4-DUDOSO"
    if "PERDIDA" in calific: return "5-PERDIDA"
    return "SIN DEFINIR"

def map_adm_agen_pbi(agencia):
    mapping = {
        "AGENCIA AGUAYTIA": "WDAZA", "AGENCIA ATALAYA": "RDAVILA",
        "AGENCIA AUCAYACU": "SIN DEFINIR", "AGENCIA HUÁNUCO": "JCUADROS",
        "AGENCIA LA MERCED": "MSANDOVAL", "AGENCIA PANGOA": "GGAGO",
        "AGENCIA PICHANAKI": "NGUTIERREZ", "AGENCIA SATIPO": "MMARAVI",
        "AGENCIA TINGO MARIA": "PHERRERA", "AGENCIA VILLA RICA": "HHUAMANI"
    }
    return "ADM-" + mapping.get(agencia, "NOMBRE_ADMINISTRADOR_DEFAULT")

def map_rango_desemb_pbi(monto):
    if monto <= 500: return "1-DE 0 A 500"
    if monto <= 1000: return "2-DE 501 A 1,000"
    if monto <= 5000: return "3-DE 1,001 A 5,000"
    if monto <= 10000: return "4-DE 5,001 A 10,000"
    if monto <= 30000: return "5-DE 10,001 A 30,000"
    if monto <= 50000: return "6-DE 30,001 A 50,000"
    if monto <= 100000: return "7-DE 50,001 A 100,000"
    return "DE 100,001 A MAS"

def map_producto_pbi(prod):
    p = prod.upper()
    if "CONVENIO" in p: return "CONVENIO"
    if "CREDI-COMERCIO" in p or p.startswith("CREDI-COMPRAS"): return "CREDI-COMERCIO"
    if "CREDI-MENSUAL" in p or p.startswith("CREDIMENSUAL"): return "CREDI-MENSUAL"
    if "GARANTIA HIPOTECARIA" in p or "CREDITO CON GARANTIA HIPOTECARIA" in p: return "GARANTÍA HIPOTECARIA"
    if "CREDIYA" in p: return "CREDIYA"
    if "MI COSECHA" in p: return "MI COSECHA"
    if "PRENDA" in p: return "PRENDATODO"
    if p.startswith("CREDI-TRANSPORTE"): return "CREDI-TRANSPORTE"
    return p

def map_rango_mora_pbi(dias):
    if dias == 0: return "1-CERO DIAS DE ATRASO"
    if dias <= 8: return "2-HASTA 08 DIAS DE ATRASO"
    if dias <= 15: return "3-HASTA 15 DIAS DE ATRASO"
    if dias <= 30: return "4-HASTA 30 DIAS DE ATRASO"
    if dias <= 60: return "5-HASTA 60 DIAS DE ATRASO"
    if dias <= 90: return "6-HASTA 90 DIAS DE ATRASO"
    if dias <= 120: return "7-HASTA 120 DIAS DE ATRASO"
    return "8-MAS DE 120 DIAS DE ATRASO"
# -----------------------------------

def process_portfolio_load(upload_id):
    try:
        upload = LiqBalanceUpload.objects.get(id=upload_id)
        df = pd.read_excel(upload.file_source.path)
        
        col_acc = get_col_robust(['CODIGO CONTABLE', 'CUENTA', 'ACCOUNT'], df.columns)
        col_bal = get_col_robust(['SALDO', 'BALANCE'], df.columns)
        
        if not col_acc or not col_bal:
            upload.status = LiqLoadStatus.ERROR
            upload.save()
            return False
            
        details = []
        for _, row in df.iterrows():
            code = str(row[col_acc]).strip()
            if not code or code == 'nan': continue
            bal = clean_decimal_latam(row[col_bal])
            details.append(LiqBalanceDetail(
                upload=upload,
                period=upload.period,
                account_code=code,
                balance=bal
            ))
            
        with transaction.atomic():
            LiqBalanceDetail.objects.filter(upload=upload).delete()
            LiqBalanceDetail.objects.bulk_create(details, batch_size=2000)
            upload.status = LiqLoadStatus.SUCCESS
            upload.save()
            
        return True
    except Exception as e:
        import traceback
        with open('debug_load.log', 'a', encoding='utf-8') as f:
            f.write(f"Error procesando balance: {str(e)}\n")
            f.write(traceback.format_exc() + "\n")
        
        upload = LiqBalanceUpload.objects.get(id=upload_id)
        upload.status = LiqLoadStatus.ERROR
        upload.save()
        return False

@login_required
def delete_account_mapping(request, mapping_id):
    from django.shortcuts import get_object_or_404, redirect
    from django.contrib import messages
    from .models import LiqAccountMapping
    
    mapping = get_object_or_404(LiqAccountMapping, id=mapping_id)
    plan_name = mapping.plan_model.name
    
    if request.method == 'POST':
        mapping.delete()
        messages.success(request, f"Mapeo eliminado exitosamente.")
        
    return redirect(f"/utilitarios/maestro-cuentas/?model={plan_name}")

@login_required
def delete_account_plan_model(request):
    from django.contrib import messages
    from django.shortcuts import redirect
    from .models import LiqAccountPlanModel
    
    if request.method == 'POST':
        model_name = request.POST.get('model_name')
        if model_name:
            plan = LiqAccountPlanModel.objects.filter(name=model_name).first()
            if plan:
                plan.delete()
                messages.success(request, f"El modelo '{model_name}' y todas sus cuentas han sido eliminados exitosamente.")
            else:
                messages.error(request, f"No se encontró el modelo '{model_name}'.")
    return redirect('utilities:account_mapping')

from .models import DatabaseBackup
from .backup_utils import perform_sqlite_backup, restore_sqlite_backup
from django.core.paginator import Paginator
import os
from django.conf import settings
from django.http import FileResponse

@login_required
def backup_manager(request):
    backups = DatabaseBackup.objects.all().order_by('-created_at')
    
    jobs = []
    try:
        from django_apscheduler.models import DjangoJob
        jobs = DjangoJob.objects.all()
    except Exception:
        pass

    context = {
        'page_title': 'Gestión de Backups',
        'backups': backups,
        'jobs': jobs,
    }
    return render(request, 'utilities/backup_manager.html', context)

@login_required
def create_backup(request):
    if request.method == 'POST':
        backup = perform_sqlite_backup(is_scheduled=False)
        if backup:
            messages.success(request, f"Backup '{backup.file_name}' creado exitosamente.")
        else:
            messages.error(request, "Error al crear el backup. Revisa los logs del servidor.")
    return redirect('utilities:backup_manager')

@login_required
def download_backup(request, backup_id):
    from django.shortcuts import get_object_or_404
    backup = get_object_or_404(DatabaseBackup, id=backup_id)
    if os.path.exists(backup.file_path):
        response = FileResponse(open(backup.file_path, 'rb'), as_attachment=True, filename=backup.file_name)
        return response
    else:
        messages.error(request, "El archivo de backup no existe en el servidor.")
        return redirect('utilities:backup_manager')

@login_required
def delete_backup(request, backup_id):
    from django.shortcuts import get_object_or_404
    if request.method == 'POST':
        backup = get_object_or_404(DatabaseBackup, id=backup_id)
        if os.path.exists(backup.file_path):
            try:
                os.remove(backup.file_path)
            except:
                pass
        backup.delete()
        messages.success(request, "Backup eliminado correctamente.")
    return redirect('utilities:backup_manager')

@login_required
def restore_backup(request):
    if request.method == 'POST':
        if 'backup_file' in request.FILES:
            uploaded_file = request.FILES['backup_file']
            
            temp_path = os.path.join(settings.MEDIA_ROOT, 'temp_upload.sqlite3')
            with open(temp_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            
            success = restore_sqlite_backup(temp_path)
            if success:
                messages.success(request, "Sistema restaurado exitosamente a partir del archivo subido.")
            else:
                messages.error(request, "Hubo un error al intentar restaurar el backup.")
            
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    return redirect('utilities:backup_manager')

@login_required
def schedule_backup(request):
    if request.method == 'POST':
        time_str = request.POST.get('backup_time')
        if time_str:
            try:
                hour, minute = map(int, time_str.split(':'))
                from apscheduler.schedulers.background import BackgroundScheduler
                from django_apscheduler.jobstores import DjangoJobStore
                from apscheduler.triggers.cron import CronTrigger
                from django.conf import settings
                from apps.utilities.backup_utils import perform_sqlite_backup
                
                scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
                scheduler.add_jobstore(DjangoJobStore(), "default")
                
                scheduler.add_job(
                    perform_sqlite_backup,
                    trigger=CronTrigger(hour=hour, minute=minute),
                    id="daily_db_backup",
                    max_instances=1,
                    replace_existing=True,
                    kwargs={'is_scheduled': True}
                )
                
                from django.contrib import messages
                messages.success(request, f"Backup automático reprogramado exitosamente para las {time_str} todos los días.")
            except Exception as e:
                from django.contrib import messages
                messages.error(request, f"Error al programar el backup: {e}")
        else:
            from django.contrib import messages
            messages.error(request, "Por favor proporciona una hora válida.")
            
    return redirect('utilities:backup_manager')
