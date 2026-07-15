import re

filepath = r"c:\Users\USER\Desktop\ARISK V002\apps\utilities\views.py"

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Replace download_credit_template
new_download = """def download_credit_template(request):
    cols = ['N', 'NCL', 'FNAC', 'GEN', 'EC', 'EMP', 'CSOC', 'PR', 'TID', 'NID', 'TPER', 'DOM', 'RCO', 'CAL', 'CALINT', 'CAGE', 'MON', 'CCR', 'TCR', 'STCR', 'FOT', 'MORG', 'TEA', 'SKCR', 'CC', 'KVI', 'KRE', 'KRF', 'KVE', 'KJU', 'KCO', 'CCO', 'DAK', 'SGP', 'SGA', 'PVR', 'PCI', 'SCC', 'CCC', 'SIN', 'SIS', 'SID', 'TPR', 'NCPR', 'NCPA', 'PCUO', 'DGR', 'FVGO', 'FVGA', 'SSC', 'SSG', 'SCR', 'SKCO', 'SCOR', 'SINC', 'SCS']
    import pandas as pd
    import io
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
    response = HttpResponse(output.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=plantilla_carga_creditos_v4.xlsx'
    return response"""

content = re.sub(r"def download_credit_template\(request\):.*?return response", new_download, content, flags=re.DOTALL)

# Replace export_credit_data
new_export = """def export_credit_data(request):
    from credit_risk.models import CreditOperation
    import pandas as pd
    import io
    
    load_date = request.GET.get('load_date')
    qs = CreditOperation.objects.select_related('customer').all()
    if load_date:
        qs = qs.filter(load_date=load_date)
        
    cols = ['N', 'NCL', 'FNAC', 'GEN', 'EC', 'EMP', 'CSOC', 'PR', 'TID', 'NID', 'TPER', 'DOM', 'RCO', 'CAL', 'CALINT', 'CAGE', 'MON', 'CCR', 'TCR', 'STCR', 'FOT', 'MORG', 'TEA', 'SKCR', 'CC', 'KVI', 'KRE', 'KRF', 'KVE', 'KJU', 'KCO', 'CCO', 'DAK', 'SGP', 'SGA', 'PVR', 'PCI', 'SCC', 'CCC', 'SIN', 'SIS', 'SID', 'TPR', 'NCPR', 'NCPA', 'PCUO', 'DGR', 'FVGO', 'FVGA', 'SSC', 'SSG', 'SCR', 'SKCO', 'SCOR', 'SINC', 'SCS']
    
    data = []
    for i, op in enumerate(qs):
        row = {c: '' for c in cols}
        row['N'] = i + 1
        row['NCL'] = op.customer.name if op.customer else ''
        row['CSOC'] = op.customer.external_id if op.customer else ''
        row['NID'] = op.customer.document_id if op.customer else ''
        row['CCR'] = op.operation_code
        row['FOT'] = op.disbursement_date.strftime('%Y%m%d') if op.disbursement_date else ''
        row['MORG'] = float(op.original_amount)
        row['TEA'] = float(op.rate)
        row['SKCR'] = float(op.balance)
        row['DAK'] = op.days_past_due
        row['CAL'] = op.sbs_classification
        data.append(row)
        
    df = pd.DataFrame(data, columns=cols)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Cartera_Creditos')
        
    response = HttpResponse(output.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=exportacion_cartera_creditos.xlsx'
    return response"""

content = re.sub(r"def export_credit_data\(request\):.*?return response", new_export, content, flags=re.DOTALL)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print("Views updated.")
