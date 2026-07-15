import re
import os

filepath = r"c:\Users\USER\Desktop\ARISK V002\apps\utilities\views.py"

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Define the new bulk_load_credit
new_bulk = """def bulk_load_credit(request):
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
            
            # Normalize column names (keep them exactly as the new template if possible)
            df.columns = [str(c).strip().upper() for c in df.columns]
            
            dates = []
            if manual_date_str:
                dates = [datetime.strptime(manual_date_str, '%Y-%m-%d').date()]
            else:
                # Si no hay fecha manual, usar hoy
                dates = [timezone.now().date()]

            if not dates:
                return redirect('utilities:bulk_load_credit')

            total_records = 0
            # Process each date in its own transaction to prevent long SQLite locks
            for d in dates:
                with transaction.atomic():
                    period_df = df
                    
                    # Idempotency: remove previous loads for this date
                    CreditOperation.objects.filter(load_date=d).delete()
                    CarteraCreditoCarga.objects.filter(fecha_corte=d).delete()
                    carga_accumulator = []
                    
                    ops_to_create = []
                    rows = period_df.to_dict('records')
                    
                    # 1. Asegurar Clientes
                    new_customers = []
                    all_doc_ids = [str(x) for x in df.get('NID', []) if pd.notna(x) and str(x).strip() != '']
                    customers_cache = {c.document_id: c for c in Customer.objects.filter(document_id__in=all_doc_ids)}
                    
                    for row in rows:
                        doc_id = str(row.get('NID', '')).strip()
                        if '.' in doc_id: doc_id = doc_id.split('.')[0]
                        if doc_id and doc_id.upper() not in ['NAN', 'NONE', '', '<NA>'] and doc_id not in customers_cache:
                            c = Customer(
                                document_id=doc_id, 
                                name=str(row.get('NCL', 'DESCONOCIDO')).strip().upper()[:255]
                            )
                            new_customers.append(c)
                            customers_cache[doc_id] = c
                    
                    if new_customers:
                        Customer.objects.bulk_create(new_customers, ignore_conflicts=True)
                        for c in Customer.objects.filter(document_id__in=[nc.document_id for nc in new_customers]):
                            customers_cache[c.document_id] = c
                    
                    # --- AGGREGATION LOGIC ---
                    ops_accumulator = {}
                    cust_op_counter = {}
                    
                    for row in rows:
                        try:
                            doc_id = str(row.get('NID', '')).strip()
                            if '.' in doc_id: doc_id = doc_id.split('.')[0]
                            if doc_id.upper() in ['NAN', 'NONE', '', '<NA>']: continue
                            
                            customer = customers_cache.get(doc_id)
                            if not customer: continue
                            
                            op_code = str(row.get('CCR', "")).strip()
                            if op_code.upper() in ['NAN', 'NONE', '', '0', '<NA>']:
                                cust_op_counter[customer.id] = cust_op_counter.get(customer.id, 0) + 1
                                op_code = f"OP-{doc_id}-{cust_op_counter[customer.id]}"
                            
                            # --- CARTERA CREDITO CARGA ---
                            carga = CarteraCreditoCarga(
                                fecha_corte=d,
                                n=str(row.get('N', '')).strip()[:50],
                                ncl=str(row.get('NCL', '')).strip()[:255],
                                fnac=parse_date(row.get('FNAC')),
                                gen=str(row.get('GEN', '')).strip()[:50],
                                ec=str(row.get('EC', '')).strip()[:50],
                                emp=str(row.get('EMP', '')).strip()[:255],
                                csoc=str(row.get('CSOC', '')).strip()[:50],
                                pr=str(row.get('PR', '')).strip()[:100],
                                tid=str(row.get('TID', '')).strip()[:50],
                                nid=doc_id,
                                tper=str(row.get('TPER', '')).strip()[:50],
                                dom=str(row.get('DOM', '')).strip()[:500],
                                rco=str(row.get('RCO', '')).strip()[:100],
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
                                cc=str(row.get('CC', '')).strip()[:100],
                                kvi=clean_decimal_latam(row.get('KVI', 0)),
                                kre=clean_decimal_latam(row.get('KRE', 0)),
                                krf=clean_decimal_latam(row.get('KRF', 0)),
                                kve=clean_decimal_latam(row.get('KVE', 0)),
                                kju=clean_decimal_latam(row.get('KJU', 0)),
                                kco=clean_decimal_latam(row.get('KCO', 0)),
                                cco=str(row.get('CCO', '')).strip()[:100],
                                dak=int(clean_decimal_latam(row.get('DAK', 0))),
                                sgp=clean_decimal_latam(row.get('SGP', 0)),
                                sga=clean_decimal_latam(row.get('SGA', 0)),
                                pvr=clean_decimal_latam(row.get('PVR', 0)),
                                pci=clean_decimal_latam(row.get('PCI', 0)),
                                scc=clean_decimal_latam(row.get('SCC', 0)),
                                ccc=str(row.get('CCC', '')).strip()[:100],
                                sin=clean_decimal_latam(row.get('SIN', 0)),
                                sis=clean_decimal_latam(row.get('SIS', 0)),
                                sid=clean_decimal_latam(row.get('SID', 0)),
                                tpr=str(row.get('TPR', '')).strip()[:100],
                                ncpr=int(clean_decimal_latam(row.get('NCPR', 0))),
                                ncpa=int(clean_decimal_latam(row.get('NCPA', 0))),
                                pcuo=str(row.get('PCUO', '')).strip()[:50],
                                dgr=int(clean_decimal_latam(row.get('DGR', 0))),
                                fvgo=parse_date(row.get('FVGO')),
                                fvga=parse_date(row.get('FVGA')),
                                ssc=clean_decimal_latam(row.get('SSC', 0)),
                                ssg=clean_decimal_latam(row.get('SSG', 0)),
                                scr=clean_decimal_latam(row.get('SCR', 0)),
                                skco=clean_decimal_latam(row.get('SKCO', 0)),
                                scor=str(row.get('SCOR', '')).strip()[:100],
                                sinc=clean_decimal_latam(row.get('SINC', 0)),
                                scs=clean_decimal_latam(row.get('SCS', 0))
                            )
                            carga_accumulator.append(carga)
                            
                            # --- CREDIT OPERATION ---
                            k = (customer.id, op_code)
                            if k not in ops_accumulator:
                                op = CreditOperation(
                                    operation_code=op_code,
                                    customer=customer,
                                    product=None,
                                    load_date=d,
                                    original_amount=carga.morg,
                                    balance=carga.skcr,
                                    rate=carga.tea,
                                    days_past_due=carga.dak,
                                    sbs_classification=map_sbs_exhaustive(carga.cal),
                                    credit_type=map_credit_type(carga.tcr),
                                    disbursement_date=carga.fot,
                                    maturity_date=carga.fvga,
                                    is_refinanced=(carga.krf > 0)
                                )
                                ops_accumulator[k] = op
                            else:
                                ops_accumulator[k].balance += carga.skcr
                                ops_accumulator[k].original_amount += carga.morg
                                
                        except Exception as e:
                            pass
                            
                    if carga_accumulator:
                        # Chunked inserts for speed
                        batch_size = 5000
                        for i in range(0, len(carga_accumulator), batch_size):
                            CarteraCreditoCarga.objects.bulk_create(carga_accumulator[i:i+batch_size])
                            
                    if ops_accumulator:
                        ops_list = list(ops_accumulator.values())
                        for i in range(0, len(ops_list), batch_size):
                            CreditOperation.objects.bulk_create(ops_list[i:i+batch_size])
                            
                    total_records += len(carga_accumulator)
                    
                    # Log
                    try:
                        BulkLoadLog.objects.create(
                            module='CarteraCredito',
                            file_name=file.name,
                            records_processed=len(carga_accumulator),
                            status='Exito',
                            cut_off_dates=str(d)
                        )
                    except: pass
                    
            messages.success(request, f"Se cargaron y procesaron {total_records} registros de cartera de créditos correctamente.")
            return redirect('utilities:bulk_load_credit')
            
        except Exception as e:
            messages.error(request, f"Error al procesar el archivo: {str(e)}")
            return redirect('utilities:bulk_load_credit')
            
    # GET request
    context = {'page_title': 'Carga Masiva - Cartera de Créditos'}
    return render(request, 'utilities/bulk_load_credit.html', context)
"""

# Now we need to replace the def bulk_load_credit(request): entirely.
# The original function goes from def bulk_load_credit to def download_liability_template.

content = re.sub(r"def bulk_load_credit\(request\):.*?def download_liability_template", new_bulk + "\n\ndef download_liability_template", content, flags=re.DOTALL)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print("bulk_load_credit updated.")
