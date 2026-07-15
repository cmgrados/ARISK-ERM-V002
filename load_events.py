import os
import django
import sys
from datetime import date, timedelta
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.op_risk.models import Risk, Process, RiskEvent, Control

events_data = [
    {
        "title": "Faltante en Caja de Agencia Principal",
        "root_cause": "Durante el arqueo de cierre de la cajera 3, se identificó un faltante en efectivo que no pudo ser sustentado.",
        "immediate_action": "Se descontó de la planilla de la cajera y se emitió amonestación.",
        "event_type": "LOSS",
        "amount": 500.00,
        "risk_keyword": "Diferencias de caja",
        "days_ago": 5
    },
    {
        "title": "Intento de Fraude con Documentos Falsos",
        "root_cause": "Se detectó que un socio intentó solicitar un crédito de 20,000 con boletas de pago adulteradas.",
        "immediate_action": "El fraude fue detenido por el analista antes del desembolso.",
        "event_type": "NEAR_MISS",
        "amount": 0.00,
        "risk_keyword": "Aprobación de créditos con documentación falsa",
        "days_ago": 12
    },
    {
        "title": "Caída del Servidor Principal por 2 Horas",
        "root_cause": "Falla eléctrica en el CPD causó que el core financiero estuviera inaccesible entre las 10:00 y las 12:00.",
        "immediate_action": "Activación del Plan de Continuidad y UPS secundario.",
        "event_type": "SYSTEM_FAILURE",
        "amount": 0.00,
        "risk_keyword": "Caída del core",
        "days_ago": 20
    },
    {
        "title": "Ataque de Phishing a Correos Corporativos",
        "root_cause": "Varios colaboradores recibieron correos suplantando a Soporte TI solicitando contraseñas.",
        "immediate_action": "El sistema bloqueó el acceso por geolocalización inusual y se forzó cambio de clave.",
        "event_type": "NEAR_MISS",
        "amount": 0.00,
        "risk_keyword": "Seguridad de la información",
        "days_ago": 8
    },
    {
        "title": "Desembolso a Cuenta Errónea",
        "root_cause": "Error de digitación por parte del área de operaciones ocasionó que un desembolso se abonara a otra cuenta.",
        "immediate_action": "Se extornó la operación tras 3 días de gestiones.",
        "event_type": "NEAR_MISS",
        "amount": 0.00,
        "risk_keyword": "Desembolso erróneo",
        "days_ago": 2
    },
    {
        "title": "Sanción SBS por Retraso en Reporte",
        "root_cause": "Retraso de dos días en el anexo regulatorio de provisiones del mes pasado.",
        "immediate_action": "Pago de multa y automatización del reporte.",
        "event_type": "LOSS",
        "amount": 4600.00,
        "risk_keyword": "Sanción por reportes",
        "days_ago": 45
    },
    {
        "title": "Fraude Interno Detectado - Analista de Crédito",
        "root_cause": "Una auditoría inopinada descubrió que un analista creaba créditos ficticios.",
        "immediate_action": "Despido y denuncia penal al ex-colaborador.",
        "event_type": "FRAUD",
        "amount": 18000.00,
        "risk_keyword": "Fraude interno",
        "days_ago": 120
    },
    {
        "title": "Diferencia Bancaria No Justificada",
        "root_cause": "Cargo de mantenimiento no contemplado en el tarifario que no se detectó por 2 meses.",
        "immediate_action": "Reclamo al banco y ajuste contable.",
        "event_type": "LOSS",
        "amount": 350.00,
        "risk_keyword": "Diferencias bancarias",
        "days_ago": 14
    }
]

created_count = 0
today = date.today()

for ev_data in events_data:
    occurrence = today - timedelta(days=ev_data["days_ago"])
    discovery = occurrence + timedelta(days=random.randint(0, 2))
    if discovery > today:
        discovery = today
        
    risk = Risk.objects.filter(name__icontains=ev_data["risk_keyword"]).first()
    process = risk.process if risk else None
    
    # Intenta buscar un control preventivo que falló (solo por rellenar datos realistas)
    failed_control = None
    if risk:
        failed_control = risk.controls.first()
    
    event, created = RiskEvent.objects.get_or_create(
        title=ev_data["title"],
        defaults={
            "root_cause": ev_data["root_cause"],
            "immediate_action": ev_data["immediate_action"],
            "date_occurred": occurrence,
            "date_discovered": discovery,
            "event_type": ev_data["event_type"],
            "amount": ev_data["amount"],
            "process": process,
            "failed_control": failed_control,
        }
    )
    if created:
        created_count += 1

print(f"RiskEvents generated successfully: {created_count} events created.")
