import pandas as pd
import math
import io
import re
from calendar import monthrange
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from credit_risk.models import Customer, CreditOperation
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

from liquidity_risk.models import (
    LiqBalanceUpload, LiqSavingsUpload, LiqTermDepositUpload,
    LiqBalanceDetail, LiqSavingsAccount, LiqTermDeposit,
    LiqAccountMapping, LiqAccountPlanModel, LiqLoadStatus,
    LiqLiabilityUpload, LiqLiabilityDetail
)
from liquidity_risk.loaders import (
    process_balance_load, process_savings_load, process_account_mapping_load
)

from django.http import HttpResponse
import io
from .models import BulkLoadLog
from .models import BulkLoadLog
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
    if pd.isna(val) or val is None: return None
    if isinstance(val, (datetime, timezone.datetime)): return val.date()
    if isinstance(val, (datetime, timezone.datetime, timezone.datetime)): return val.date()
    try: return pd.to_datetime(val).date()
    except: return None

def dashboard(request):
    context = {'page_title': 'Utilitarios y Herramientas del Sistema'}
    return render(request, 'utilities/dashboard.html', context)

def download_credit_template(request):
    cols = [
        'CODIGO SOCIO/CLIENTE', 'APELLIDOS NOMBRES', 'EDAD', 'SEXO', 
        'FECHA DE NACIMIENTO', 'FECHA DESEMBOLSO', 'FECHA VENCIMIENTO', 'PERIODICIDAD PAGO', 'NRO PAGARÉ', 
        'MONTO PRESTAMO', 'TEA', 'PLAZO', 'ULTIMA FECHA MOV', 'SALDO', 
        'DIAS ATRASO', 'CLASIFICACIÓN', 'TIPO DE CRÉDITO', 
        'PROVISIÓN GENERICA', 'PROVISIÓN ESPECIFICA', 'PROV REQUERIDA', 
        'PROV CONSTITUIDA', 'INTERES POR COBRAR', 'INTERES SUSPENSO', 
        'CARTERA VIGENTE', 'CARTERA VENCIDA', 'CARTERA JUDICIAL', 'REFINANCIADO VIGENTE', 
        'REFINANCIADO VENCIDA', 'REPROGRAMACION VIGENTE', 'REPROGRAMACION VENCIDA', 
        'PRODUCTO', 'CONVENIO', 'ANALISTA SOLICITUD CRED.', 'NOMBRE ANALISTA SOLICITUD CRED.', 
        'AGENCIA', 'FECHA DE CORTE'
    ]
    df = pd.DataFrame(columns=cols)
    example = {'CODIGO SOCIO/CLIENTE': '12345678', 'APELLIDOS NOMBRES': 'ABAD APESTEGUIA CARLOS ALBERTO', 'EDAD': 71, 'SEXO': 'M', 'FECHA DE NACIMIENTO': '1954-01-01', 'FECHA DESEMBOLSO': '2025-01-15', 'NRO PAGARÉ': 'CRED-001', 'MONTO PRESTAMO': 10000.00, 'TEA': 18.5, 'PLAZO': 24, 'ULTIMA FECHA MOV': '2025-04-10', 'SALDO': 8500.00, 'DIAS ATRASO': 0, 'CLASIFICACIÓN': 'Normal', 'TIPO DE CRÉDITO': 'MYPE', 'PROVISIÓN GENERICA': 100.00, 'PROVISIÓN ESPECIFICA': 0.00, 'PROV REQUERIDA': 100.00, 'PROV CONSTITUIDA': 100.00, 'INTERES POR COBRAR': 45.00, 'INTERES SUSPENSO': 0.00, 'CARTERA VIGENTE': 8500.00, 'CARTERA VENCIDA': 0.00, 'REFINANCIADO VIGENTE': 0.00, 'REFINANCIADO VENCIDA': 0.00, 'REPROGRAMACION VIGENTE': 0.00, 'REPROGRAMACION VENCIDA': 0.00, 'PRODUCTO': 'CRÉDITO CAPITAL DE TRABAJO', 'CONVENIO': 'NINGUNO', 'ANALISTA SOLICITUD CRED.': 'A01', 'NOMBRE ANALISTA SOLICITUD CRED.': 'ASESOR_X', 'AGENCIA': 'AGENCIA_01', 'FECHA DE CORTE': '2026-04-30'}
    df = pd.concat([df, pd.DataFrame([example])], ignore_index=True)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Plantilla_Creditos')
    response = HttpResponse(output.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=plantilla_carga_creditos_v3.xlsx'
    return response

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

import csv
from django.http import StreamingHttpResponse
from django.utils.timezone import now
from credit_risk.models import CreditOperation

class Echo:
    """An object that implements just the write method of the file-like interface."""
    def write(self, value):
        return value

def export_credit_data(request):
    """
    Exports all CreditOperations as a Streaming CSV so it can handle 300k+ rows 
    without consuming all memory or timing out.
    """
    def generate_csv():
        pseudo_buffer = Echo()
        writer = csv.writer(pseudo_buffer)
        
        # UTF-8 BOM for Excel to open it automatically with correct encoding
        yield '\ufeff'
        
        # Header
        yield writer.writerow([
            'FECHA_CORTE', 'AGENCIA', 'DNI_RUC', 'SOCIO', 'NOMBRE', 'EDAD', 'GENERO',
            'SEGMENTO', 'OP_REF', 'PRODUCTO', 'SALDO', 'TASA_PORCENTAJE', 
            'FECHA_DESEMBOLSO', 'FECHA_VENCIMIENTO', 'TIPO_CREDITO', 'PROVISION_REQUERIDA'
        ])
        
        # Querying data in chunks using iterator to save memory
        qs = CreditOperation.objects.select_related('customer').all().order_by('-load_date').iterator(chunk_size=5000)
        
        for obj in qs:
            yield writer.writerow([
                obj.load_date,
                obj.agency,
                obj.customer.document_id if obj.customer else '',
                obj.customer.external_id if obj.customer else '',
                obj.customer.name if obj.customer else '',
                obj.customer.age if obj.customer else '',
                obj.customer.gender if obj.customer else '',
                obj.customer.segment if obj.customer else '',
                obj.operation_code,
                obj.product_name,
                obj.balance,
                obj.rate,
                obj.disbursement_date,
                obj.maturity_date,
                obj.credit_type,
                obj.required_provision
            ])
            
    response = StreamingHttpResponse(generate_csv(), content_type='text/csv; charset=utf-8')
    filename = f'export_cartera_{now().strftime("%Y%m%d_%H%M")}.csv'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

def export_liability_data(request):
    from liquidity_risk.models import LiqLiabilityDetail
    
    def generate_csv():
        pseudo_buffer = Echo()
        writer = csv.writer(pseudo_buffer)
        
        # UTF-8 BOM for Excel
        yield '\ufeff'
        
        # Header
        yield writer.writerow([
            'PERIODO', 'AGENCIA', 'AG_APERTURA', 'SOCIO', 'NOMBRES', 'EDAD', 'SEXO',
            'FECHA_NACIMIENTO', 'FECHA_APERTURA', 'FECHA_VENCIMIENTO', 'NRO_CUENTA',
            'PRODUCTO', 'MONEDA', 'MONTO', 'SALDO', 'TEA', 'TEM'
        ])
        
        qs = LiqLiabilityDetail.objects.all().order_by('-period').iterator(chunk_size=5000)
        for obj in qs:
            yield writer.writerow([
                obj.period,
                obj.agency,
                obj.opening_agency,
                obj.customer_id,
                obj.customer_name,
                obj.customer_age,
                obj.customer_gender,
                obj.customer_birth_date,
                obj.opening_date,
                obj.due_date,
                obj.account_number,
                obj.product,
                obj.currency,
                obj.amount,
                obj.balance,
                obj.rate,
                obj.tem
            ])
            
    response = StreamingHttpResponse(generate_csv(), content_type='text/csv; charset=utf-8')
    filename = f'export_pasivos_{now().strftime("%Y%m%d_%H%M")}.csv'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

def parse_date(date_val):
    if pd.isna(date_val) or date_val == '': return None
    try: return pd.to_datetime(date_val).date()
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
            
            # Normalize column names
            df.columns = [str(c).strip().upper().replace(' ', '_') for c in df.columns]
            
            # 1. Identify Cut-off Dates
            # Try to find a date column in the file first
            cut_off_col = next((c for c in df.columns if 'FECHA' in c and 'CORTE' in c), None)
            if not cut_off_col:
                cut_off_col = next((c for c in df.columns if 'PERIODO' in c or 'CUT_OFF' in c), None)
            
            if cut_off_col:
                dates = df[cut_off_col].unique()
                dates = [pd.to_datetime(d).date() for d in dates if not pd.isna(d)]
            elif manual_date_str:
                dates = [datetime.strptime(manual_date_str, '%Y-%m-%d').date()]
            else:
                messages.error(request, "Debe especificar una fecha de corte.")
                return redirect('utilities:bulk_load_credit')

            if not dates:
                messages.error(request, "No se identificaron fechas de corte válidas en el archivo.")
                return redirect('utilities:bulk_load_credit')

            # --- Detección de Columnas Robusta ---
            col_sbs = get_col_robust(['CLASIFICACION', 'CATEGORIA', 'CALIFICACION', 'SBS', 'SITUACION'], df.columns)
            col_agency = get_col_robust(['AGENCIA', 'OFICINA', 'SUCURSAL', 'LOCALIDAD', 'CENTRO'], df.columns)
            col_balance = get_col_robust(['SALDO', 'MONTO_PENDIENTE', 'DEUDA', 'CAPITAL'], df.columns)
            col_id = get_col_robust(['DOCUMENTO', 'DNI', 'RUC', 'CODIGO_SOCIO', 'COD_USUARIO', 'CLIENTE'], df.columns)
            
            col_op_ref = get_col_robust(['OP_REF', 'PAGARE', 'OPERACION', 'CREDITO', 'CONTRATO', 'NUM_OPER', 'NRO_OP'], df.columns)
            if not col_op_ref: col_op_ref = get_col_robust(['NRO', 'NUMERO', 'COD_OP'], df.columns)
            
            col_tea = get_col_robust(['TASA', 'TEA', 'TREA', 'INT'], df.columns)
            col_term = get_col_robust(['PLAZO', 'MESES', 'DIAS', 'TERM'], df.columns)
            col_past_due = get_col_robust(['ATRASO', 'DIAS_ATRASO', 'MORA', 'MOROSIDAD', 'DIAS_MORA'], df.columns)
            col_maturity = get_col_robust(['VENCIMIENTO', 'FECHA_VENC', 'MATURITY', 'VENCE'], df.columns)
            col_type = get_col_robust(['TIPO_DE_CREDITO', 'TIPO_CREDITO', 'MODALIDAD', 'SEGMENTO'], df.columns)
            col_advisor = get_col_robust(['ASESOR', 'ANALISTA', 'EJECUTIVO', 'FUNCIONARIO'], df.columns)
            col_product = get_col_robust(['PRODUCTO', 'LINEA', 'DESC_PRODUCTO', 'PRODUCT'], df.columns)
            col_orig_monto = get_col_robust(['MONTO_PRESTAMO', 'PRESTAMO', 'MONTO_DESEMBOLSADO', 'ORIGINAL', 'DESEMBOLSO', 'MONTO_APR'], df.columns)
            
            # Additional financial fields
            col_prov_req = get_col_robust(['PROV_REQUERIDA', 'PROVISION_REQUERIDA', 'REQUERIDA'], df.columns)
            col_prov_const = get_col_robust(['PROV_CONSTITUIDA', 'PROVISION_CONSTITUIDA', 'CONSTITUIDA'], df.columns)
            col_int_cobrar = get_col_robust(['INTERES_POR_COBRAR', 'INT_COBRAR', 'DEVENGADO'], df.columns)
            col_int_susp = get_col_robust(['INTERES_SUSPENSO', 'INT_SUSPENSO'], df.columns)
            col_cart_vig = get_col_robust(['CARTERA_VIGENTE', 'VIGENTE'], df.columns)
            col_cart_venc = get_col_robust(['CARTERA_VENCIDA', 'VENCIDA'], df.columns)
            col_cart_jud = get_col_robust(['CARTERA_JUDICIAL', 'JUDICIAL'], df.columns)
            col_ref_vig = get_col_robust(['REFINANCIADO_VIGENTE', 'REF_VIGENTE'], df.columns)
            col_ref_venc = get_col_robust(['REFINANCIADO_VENCIDA', 'REF_VENCIDA'], df.columns)

            with open('debug_load.log', 'a', encoding='utf-8') as f:
                f.write(f"--- NUEVA CARGA: {file.name} ---\n")
                f.write(f"Columnas detectadas: SBS={col_sbs}, ID={col_id}, OP={col_op_ref}, Bal={col_balance}, Type={col_type}, Prod={col_product}\n")
                f.write("Muestra de primeras 5 filas:\n")
                f.write(df.head(5).to_string() + "\n")
                f.write("-----------------------------\n")

            # --- OPTIMIZACIÓN: Caché de Clientes ---
            all_doc_ids = [str(x) for x in df[col_id].dropna().unique() if str(x).strip() != ''] if col_id else []
            customers_cache = {c.document_id: c for c in Customer.objects.filter(document_id__in=all_doc_ids)}
            
            if cut_off_col:
                df['_temp_date'] = pd.to_datetime(df[cut_off_col], errors='coerce').dt.date
            
            total_records = 0
            # Process each date in its own transaction to prevent long SQLite locks
            for d in dates:
                with transaction.atomic():
                    # Filter for period or use whole DF
                    period_df = df[df['_temp_date'] == d] if cut_off_col else df
                    
                    with open('debug_load.log', 'a', encoding='utf-8') as f:
                        f.write(f"Procesando fecha {d}: {len(period_df)} filas encontradas.\n")
                    
                    # Idempotency: remove previous loads for this date
                    CreditOperation.objects.filter(load_date=d).delete()
                    
                    ops_to_create = []
                    # Convertir a lista de diccionarios (mucho más rápido que iterrows)
                    rows = period_df.to_dict('records')
                    
                    # 1. Asegurar Clientes
                    new_customers = []
                    for row in rows:
                        doc_id = str(row.get(col_id, '')).strip()
                        if doc_id and doc_id.upper() not in ['NAN', 'NONE', '', '<NA>'] and doc_id not in customers_cache:
                            c = Customer(
                                document_id=doc_id, 
                                name=str(row.get('NOMBRE', row.get('CLIENTE', row.get('SOCIO', 'DESCONOCIDO')))).strip().upper()[:255]
                            )
                            new_customers.append(c)
                            customers_cache[doc_id] = c # Placeholder
                    
                    if new_customers:
                        Customer.objects.bulk_create(new_customers, ignore_conflicts=True)
                        for c in Customer.objects.filter(document_id__in=[nc.document_id for nc in new_customers]):
                            customers_cache[c.document_id] = c
                    
                    # --- AGGREGATION LOGIC ---
                    ops_accumulator = {} # (customer_id, op_code) -> CreditOperation object
                    cust_op_counter = {}
                    
                    for row in rows:
                        try:
                            doc_id = str(row.get(col_id, '')).strip()
                            if '.' in doc_id: doc_id = doc_id.split('.')[0]
                            if doc_id.upper() in ['NAN', 'NONE', '', '<NA>']: continue
                            
                            customer = customers_cache.get(doc_id)
                            if not customer: continue
                            
                            op_code = str(row.get(col_op_ref, "")).strip()
                            if op_code.upper() in ['NAN', 'NONE', '', '0', '<NA>']:
                                cust_op_counter[customer.id] = cust_op_counter.get(customer.id, 0) + 1
                                op_code = f"OP-{doc_id}-{cust_op_counter[customer.id]}"
                            
                            # Normalize Classification (Exhaustive)
                            sbs_cat = map_sbs_exhaustive(row.get(col_sbs, 'NORMAL'))

                            # Values
                            balance_val = clean_decimal_latam(row.get(col_balance, 0))
                            orig_val = clean_decimal_latam(row.get(col_orig_monto, balance_val))
                            past_due_val = int(clean_decimal_latam(row.get(col_past_due, 0)))
                            
                            # Financial Metrics
                            prov_req = clean_decimal_latam(row.get(col_prov_req, 0))
                            prov_const = clean_decimal_latam(row.get(col_prov_const, 0))
                            int_cob = clean_decimal_latam(row.get(col_int_cobrar, 0))
                            int_susp = clean_decimal_latam(row.get(col_int_susp, 0))
                            c_vig = clean_decimal_latam(row.get(col_cart_vig, 0))
                            c_venc = clean_decimal_latam(row.get(col_cart_venc, 0))
                            c_jud = clean_decimal_latam(row.get(col_cart_jud, 0))
                            r_vig = clean_decimal_latam(row.get(col_ref_vig, 0))
                            r_venc = clean_decimal_latam(row.get(col_ref_venc, 0))

                            key = (customer.id, op_code)
                            if key in ops_accumulator:
                                op = ops_accumulator[key]
                                op.balance += balance_val
                                op.original_amount += orig_val
                                op.days_past_due = max(op.days_past_due, past_due_val)
                                op.required_provision += prov_req
                                op.established_provision += prov_const
                                op.interest_receivable += int_cob
                                op.interest_suspended += int_susp
                                op.current_portfolio += c_vig
                                op.past_due_portfolio += c_venc
                                op.judicial_portfolio += c_jud
                                op.refinanced_current += r_vig
                                op.refinanced_past_due += r_venc
                                
                                cat_order = {'NORMAL': 0, 'CPP': 1, 'DEFICIENTE': 2, 'DUDOSO': 3, 'PERDIDA': 4}
                                if cat_order.get(sbs_cat, 0) > cat_order.get(op.sbs_classification, 0):
                                    op.sbs_classification = sbs_cat
                            else:
                                disb_date = parse_date(row.get('FECHA_DESEMBOLSO', row.get('DESEMBOLSO', d)))
                                term_val = int(clean_decimal_latam(row.get(col_term, 0)))
                                mat_date = parse_date(row.get(col_maturity))
                                if not mat_date and disb_date and term_val > 0:
                                    from dateutil.relativedelta import relativedelta
                                    mat_date = disb_date + relativedelta(months=term_val)

                                ops_accumulator[key] = CreditOperation(
                                    customer=customer, operation_code=op_code,
                                    disbursement_date=disb_date, maturity_date=mat_date,
                                    original_amount=orig_val, balance=balance_val,
                                    rate=clean_decimal_latam(row.get(col_tea, 0)), term=term_val,
                                    load_date=d, days_past_due=past_due_val, sbs_classification=sbs_cat,
                                    agency=str(row.get(col_agency, 'SIN AGENCIA')).strip().upper(),
                                    product_name=str(row.get(col_product, 'SIN PRODUCTO')).strip().upper(),
                                    credit_type=map_credit_type(row.get(col_type, row.get(col_product, 'CONSUMO'))),
                                    advisor=str(row.get(col_advisor, 'SIN ASESOR')).strip().upper(),
                                    required_provision=prov_req, established_provision=prov_const,
                                    interest_receivable=int_cob, interest_suspended=int_susp,
                                    current_portfolio=c_vig, past_due_portfolio=c_venc, judicial_portfolio=c_jud,
                                    refinanced_current=r_vig, refinanced_past_due=r_venc,
                                    is_refinanced=(r_vig > 0 or r_venc > 0)
                                )
                        except: continue
                    
                    to_create = list(ops_accumulator.values())
                    if to_create:
                        CreditOperation.objects.bulk_create(to_create, batch_size=2000, ignore_conflicts=True)
                        total_records += len(to_create)
                        
                        # Ingestion Summary for Audit
                        class_counts = {}
                        total_bal = Decimal('0')
                        for op in to_create:
                            class_counts[op.sbs_classification] = class_counts.get(op.sbs_classification, 0) + 1
                            total_bal += op.balance
                        
                        with open('debug_load.log', 'a', encoding='utf-8') as f:
                            f.write(f"--- RESUMEN AUDITORÍA {d} ---\n")
                            f.write(f"Operaciones Únicas: {len(to_create)}\n")
                            f.write(f"Saldos por Clasificación: {class_counts}\n")
                            f.write(f"Balance Total Sumado: {total_bal}\n")
                            f.write(f"-----------------------------\n")

                        try:
                            generate_missing_metrics(load_date=d, force_recalculate=True)
                        except Exception as e:
                            with open('debug_load.log', 'a', encoding='utf-8') as f:
                                f.write(f"Error en métricas: {str(e)}\n")

            if total_records == 0:
                msg = f"No se procesaron registros. Verifique que las columnas coincidan. ID detectado: {col_id}, OP detectado: {col_op_ref}"
                messages.warning(request, msg)
            else:
                messages.success(request, f"Carga de cartera completada. {total_records} registros procesados.")

            BulkLoadLog.objects.create(
                file_name=file.name, load_type='CREDIT',
                cut_off_dates=",".join([d.strftime('%Y-%m-%d') for d in dates]),
                records_processed=total_records, status='Success' if total_records > 0 else 'Warning'
            )
            cache.clear()
            return redirect('utilities:bulk_load_credit')
            
        except Exception as e:
            import traceback
            with open('debug_load.log', 'a', encoding='utf-8') as f:
                f.write(f"ERROR FATAL EN CARGA: {str(e)}\n")
                f.write(traceback.format_exc() + "\n")
            try:
                date_str = ",".join([d.strftime('%Y-%m-%d') for d in dates])
            except:
                date_str = ""
            BulkLoadLog.objects.create(
                file_name=file.name,
                load_type='CREDIT',
                cut_off_dates=date_str,
                records_processed=0,
                status='Error',
                error_message=str(e) or "Error desconocido"
            )
            messages.error(request, f"Error en la carga: {str(e) or 'Error desconocido'}")
            return redirect('utilities:bulk_load_credit')

    history = BulkLoadLog.objects.filter(load_type='CREDIT').order_by('-load_date')
    return render(request, 'utilities/credit_bulk_load.html', {
        'page_title': 'Carga Masiva - Cartera de Créditos',
        'history': history,
        'today': timezone.now().date()
    })

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

def bulk_load_liability(request):
    from liquidity_risk.models import LiqLiabilityUpload, LiqLiabilityDetail, LiqLoadStatus
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
                all_dfs.append(pd.read_csv(file))

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
                            LiqLiabilityDetail.objects.filter(period=d).delete()
                            cleared_periods.add(d)

                        period_df = df[df['_temp_date'] == d]
                        rows = period_df.to_dict('records')
                        
                        upload_obj, _ = LiqLiabilityUpload.objects.update_or_create(
                            period=d, defaults={'status': LiqLoadStatus.SUCCESS, 'user': request.user}
                        )
                        
                        to_create = []
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
                            
                            # Regla Crítica de Clasificación (basado en PRODUCTO)
                            prod_name = str(row.get(col_prod, '')).strip().upper()
                            if 'PLAZO' in prod_name:
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
                                upload=upload_obj,
                                period=d,
                                agency=str(row.get(col_agency, 'SIN AGENCIA')).strip().upper(),
                                opening_agency=str(row.get(col_agency_open, '')).strip().upper(),
                                customer_id=str(row.get(col_id, '')).strip(),
                                customer_name=str(row.get(col_name, 'CLIENTE DESCONOCIDO')).strip().upper(),
                                customer_age=int(clean_decimal_latam(row.get(col_age, 0))) or None,
                                customer_gender=str(row.get(col_gender, '')).strip().upper()[:1],
                                customer_birth_date=f_birth,
                                opening_date=f_open,
                                due_date=f_venc,
                                account_number=acc_num,
                                product=str(row.get(col_prod, 'SIN PRODUCTO')).strip().upper(),
                                currency='ME' if any(k in str(row.get(col_moneda, '')).upper() for k in ['ME', '$', 'DOLAR', 'USD']) else 'MN',
                                amount=monto,
                                balance=saldo,
                                rate=clean_decimal_latam(row.get(col_tea, 0)),
                                tem=clean_decimal_latam(row.get(col_tem, 0)),
                                term_days=int(clean_decimal_latam(row.get(col_term, 0))),
                                created_by_user_code=str(row.get(col_user_crea, '')).strip().upper(),
                                captador=str(row.get(col_captador, '')).strip().upper(),
                                segment=str(row.get(col_segment, 'PERSONA NATURAL')).strip().upper(),
                                cancellation_date=f_canc,
                                # Derived
                                liquidity_item=rubro,
                                funding_type=tipo,
                                cut_off_status=estado,
                                days_to_due=dias_venc,
                                liquidity_band=banda,
                                is_observed=is_obs,
                                observation_detail=obs_det
                            ))
                        
                        if to_create:
                            LiqLiabilityDetail.objects.bulk_create(to_create, batch_size=2000)
                            records_count += len(to_create)

            messages.success(request, f"Carga masiva completada. {records_count} registros procesados.")
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
                from liquidity_risk.models import LiqSavingsAccount, LiqTermDeposit, LiqLiabilityDetail, LiqLiabilityUpload
                # Also delete associated Upload tracking objects if they are empty or per period
                count1, _ = LiqSavingsAccount.objects.filter(period__in=dates).delete()
                count2, _ = LiqTermDeposit.objects.filter(period__in=dates).delete()
                count3, _ = LiqLiabilityDetail.objects.filter(period__in=dates).delete()
                LiqLiabilityUpload.objects.filter(period__in=dates).delete()
                deleted_count = count1 + count2 + count3
                
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
                    from liquidity_risk.models import LiqSavingsAccount, LiqTermDeposit, LiqLiabilityDetail, LiqLiabilityUpload
                    count1, _ = LiqSavingsAccount.objects.filter(period__in=dates).delete()
                    count2, _ = LiqTermDeposit.objects.filter(period__in=dates).delete()
                    count3, _ = LiqLiabilityDetail.objects.filter(period__in=dates).delete()
                    LiqLiabilityUpload.objects.filter(period__in=dates).delete()
                    deleted_count = count1 + count2 + count3
                    
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
                    'plan_model': plan_model,
                    'currency': request.POST.get('currency', 'MN'),
                    'file_source': file,
                    'user': request.user,
                    'status': LiqLoadStatus.PENDING
                }
            )
            if process_balance_load(upload.id):
                messages.success(request, "Proceso de carga iniciado correctamente.")
            else:
                messages.error(request, "Error al procesar el balance.")
        return redirect('utilities:load_balance')
        
    history = LiqBalanceUpload.objects.all().order_by('-period')
    all_models = LiqAccountPlanModel.objects.filter(is_active=True)
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
def view_balance(request, upload_id):
    upload = get_object_or_404(LiqBalanceUpload, id=upload_id)
    details = upload.details.all().order_by('account_code')
    return render(request, 'liquidity_risk/loaders/view_balance_detail.html', {
        'page_title': f'Detalle de Balance - {upload.period.strftime("%m/%Y")}',
        'upload': upload,
        'details': details
    })

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
def export_account_mapping(request):
    selected_model_name = request.GET.get('model', '').strip()
    
    if not selected_model_name:
        first_model = LiqAccountPlanModel.objects.first()
        selected_model_name = first_model.name if first_model else 'ESTANDAR'
        
    mappings = LiqAccountMapping.objects.filter(plan_model__name=selected_model_name).order_by('account_code')
    
    data = []
    for m in mappings:
        data.append({
            'CÓDIGO': m.account_code,
            'DENOMINACIÓN': m.account_name,
            'RUBRO LIQUIDEZ': m.liquidity_item,
            'TIPO': m.get_account_type_display(),
            'MONEDA': m.get_currency_display(),
            'DISTRIBUCIÓN': m.get_distribution_rule_display(),
            'ORIGEN': m.get_data_source_display(),
        })
        
    df = pd.DataFrame(data)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Maestro de Cuentas')
        
        # Ajustar ancho de columnas
        worksheet = writer.sheets['Maestro de Cuentas']
        for idx, col in enumerate(df.columns):
            max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
            worksheet.column_dimensions[chr(65 + idx)].width = max_len
    
    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    filename = f'maestro_cuentas_{selected_model_name}.xlsx'
    response['Content-Disposition'] = f'attachment; filename={filename}'
    return response

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

