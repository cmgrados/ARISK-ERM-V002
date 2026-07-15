import re

filepath = r"c:\Users\USER\Desktop\ARISK V002\apps\utilities\views.py"

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Buscamos la función bulk_load_credit entera
match = re.search(r'(def bulk_load_credit\(request\):.*?)(?=\n\S)', content, re.DOTALL)
if not match:
    print("No se encontró bulk_load_credit")
    exit(1)

old_func = match.group(1)

new_func = """def bulk_load_credit(request):
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
                f.write(f"--- NUEVA CARGA: {file.name} ---\\n")

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
                            scs=clean_decimal_latam(row.get('SCS', 0))
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
                            sbs_classification=carga.cal
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
    for h in history:
        h.dates_list = h.cut_off_dates.split(',') if h.cut_off_dates else []
    return render(request, 'utilities/credit_bulk_load.html', {'history': history, 'page_title': 'Carga Masiva - Cartera de Créditos'})"""

content = content.replace(old_func, new_func)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print("Patch applied")
