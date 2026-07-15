import pandas as pd
from django.http import HttpResponse
from modulo_riesgo_credito.models import RiskClassification

def export_sbs_anexo_5(cut_off_date):
    """
    Generador del Anexo 5 de la SBS (Reporte de Deudores y Provisiones) usando Pandas.
    Genera un archivo Excel estructurado para la fecha de corte solicitada.
    """
    classifications = RiskClassification.objects.filter(cut_off_date=cut_off_date).select_related('operation')
    
    data = []
    for cl in classifications:
        op = cl.operation
        data.append({
            'COD_SOCIO': op.customer.document_id,
            'TIPO_CREDITO': op.credit_type,
            'SALDO_VIGENTE': float(cl.snapshot_data.get('balance', 0)),
            'DIAS_MORA': cl.days_past_due,
            'CLASIFICACION_SBS': cl.sbs_classification,
            'PROVISION_REQUERIDA': float(cl.required_provision)
        })
        
    df = pd.DataFrame(data)
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="Anexo5_SBS_{cut_off_date}.xlsx"'
    
    if not df.empty:
        # Usar openpyxl como engine para exportar
        with pd.ExcelWriter(response, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Anexo 5')
    else:
        # Enviar archivo en blanco si no hay data
        df = pd.DataFrame(columns=['COD_SOCIO', 'TIPO_CREDITO', 'SALDO_VIGENTE', 'DIAS_MORA', 'CLASIFICACION_SBS', 'PROVISION_REQUERIDA'])
        with pd.ExcelWriter(response, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Anexo 5')
            
    return response
