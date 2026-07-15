import os
import django
from datetime import date, timedelta
from django.core.files.base import ContentFile

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.contenttypes.models import ContentType

from apps.op_risk.models import Risk, RiskEvent, ActionPlan, OpRiskDocument

# --- Planes de Acción ---
action_plans_data = [
    {
        "title": "Implementar Firewall de Nueva Generación",
        "description": "Adquirir y configurar firewall perimetral para mitigar intentos de phishing y ataques al servidor.",
        "risk_keyword": "Seguridad de la información",
        "status": "IN_PROGRESS",
        "days_to_commit": 30
    },
    {
        "title": "Actualizar Manual de Prevención LA/FT",
        "description": "Incluir nuevos tipologías de fraude y automatizar el reporte de alertas de operaciones inusuales.",
        "risk_keyword": "No detección de operaciones inusuales",
        "status": "COMPLETED",
        "days_to_commit": -15
    },
    {
        "title": "Capacitación a Cajeros en Detección de Billetes Falsos",
        "description": "Taller práctico presencial para todo el personal de ventanilla a nivel nacional.",
        "event_keyword": "Faltante en Caja", # Link to Event
        "status": "OPEN",
        "days_to_commit": 45
    },
    {
        "title": "Migración a Servidores en la Nube (AWS/Azure)",
        "description": "Para garantizar la disponibilidad del core financiero ante cortes de luz o desastres locales.",
        "event_keyword": "Caída del Servidor Principal",
        "status": "OVERDUE",
        "days_to_commit": -5
    },
    {
        "title": "Validación Biométrica en Desembolsos",
        "description": "Implementar huella digital obligatoria conectada a RENIEC para frenar suplantaciones.",
        "risk_keyword": "Aprobación de créditos con documentación falsa",
        "status": "IN_PROGRESS",
        "days_to_commit": 60
    }
]

created_plans = 0
today = date.today()

for plan_data in action_plans_data:
    commitment_date = today + timedelta(days=plan_data["days_to_commit"])
    
    risk = None
    event = None
    
    if "risk_keyword" in plan_data:
        risk = Risk.objects.filter(name__icontains=plan_data["risk_keyword"]).first()
    elif "event_keyword" in plan_data:
        event = RiskEvent.objects.filter(title__icontains=plan_data["event_keyword"]).first()
        
    plan, created = ActionPlan.objects.get_or_create(
        title=plan_data["title"],
        defaults={
            "description": plan_data["description"],
            "commitment_date": commitment_date,
            "status": plan_data["status"],
            "risk": risk,
            "event": event,
        }
    )
    if created:
        created_plans += 1

# --- Documentos ---
# Create some fake txt files in memory and save them to the model
docs_data = [
    {
        "title": "Manual de Políticas de Crédito V2.0",
        "content": "Este es el manual de políticas de crédito aprobado por el consejo.",
        "target_model": Risk,
        "target_keyword": "Aprobación de créditos",
        "version": "2.0"
    },
    {
        "title": "Acta de Comité de Auditoría - Q3",
        "content": "Acta de la reunión del comité de auditoría del tercer trimestre.",
        "target_model": ActionPlan,
        "target_keyword": "Implementar Firewall",
        "version": "1.0"
    },
    {
        "title": "Evidencia de Arqueo Sorpresivo - Agencia Centro",
        "content": "Acta firmada de que se realizó el arqueo sorpresivo con resultado conforme.",
        "target_model": RiskEvent,
        "target_keyword": "Faltante en Caja",
        "version": "1.0"
    }
]

created_docs = 0

for doc_data in docs_data:
    target_obj = None
    TargetModel = doc_data["target_model"]
    
    if TargetModel == Risk:
        target_obj = Risk.objects.filter(name__icontains=doc_data["target_keyword"]).first()
    elif TargetModel == ActionPlan:
        target_obj = ActionPlan.objects.filter(title__icontains=doc_data["target_keyword"]).first()
    elif TargetModel == RiskEvent:
        target_obj = RiskEvent.objects.filter(title__icontains=doc_data["target_keyword"]).first()
        
    if target_obj:
        ctype = ContentType.objects.get_for_model(target_obj)
        
        # Check if exists
        exists = OpRiskDocument.objects.filter(title=doc_data["title"], content_type=ctype, object_id=target_obj.id).exists()
        if not exists:
            new_doc = OpRiskDocument(
                title=doc_data["title"],
                version=doc_data["version"],
                content_type=ctype,
                object_id=target_obj.id
            )
            # Create a fake file
            file_name = f"{doc_data['title'].replace(' ', '_')}.txt"
            new_doc.file.save(file_name, ContentFile(doc_data["content"]))
            new_doc.save()
            created_docs += 1

print(f"Action Plans created: {created_plans}")
print(f"Documents created: {created_docs}")
