import os
import django
import random
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from operational_risk.models import OpRiskIncident, OpRiskEventCategory, PotentialLoss
from catalogs.models import OrganizationalUnit, Process, Subprocess, RiskType
from risks.models import Risk
from action_plans.models import ActionPlan
from users.models import User

print("Iniciando generación de datos de prueba para Riesgo Operacional...")

# 1. Crear Categorías Basilea (si no existen)
categorias_basilea = [
    "Fraude Interno",
    "Fraude Externo",
    "Prácticas de empleo y seguridad en el lugar de trabajo",
    "Clientes, productos y prácticas empresariales",
    "Daños a activos físicos",
    "Fallas del negocio y de los sistemas",
    "Ejecución, entrega y gestión de procesos"
]

cat_objects = []
for cat_name in categorias_basilea:
    cat, _ = OpRiskEventCategory.objects.get_or_create(name=cat_name)
    cat_objects.append(cat)

# 2. Get dependencies
processes = list(Process.objects.all())
subprocesses = list(Subprocess.objects.all())
areas = list(OrganizationalUnit.objects.all())
users = list(User.objects.all())
if not users:
    print("AVISO: No hay usuarios, creando un usuario de sistema...")
    user = User.objects.create(username="sysadmin", is_staff=True, is_superuser=True)
    users.append(user)

user = users[0]

risk_type, _ = RiskType.objects.get_or_create(code="OP", defaults={"name": "Riesgo Operacional"})

# 3. Create Risks
risks_list = []
for i in range(10):
    r, _ = Risk.objects.get_or_create(
        name=f"Riesgo Operacional General {i+1}",
        risk_type=risk_type,
        defaults={
            "description": "Riesgo de prueba generado automáticamente.",
            "owner": user,
            "process": random.choice(processes) if processes else None
        }
    )
    risks_list.append(r)

# 4. Create 50 OpRiskIncidents and Potential Losses
print("Generando 50 Incidentes de Riesgo Operacional...")
severities = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
statuses = ['open', 'mitigated', 'closed']
loss_types = ['Pérdida en efectivo', 'Robo de activos', 'Pérdida por demanda', 'Multa regulatoria', 'Falla tecnológica']

incidents_created = 0
for i in range(50):
    # Random dates in the last 2 years
    days_ago = random.randint(1, 700)
    incident_date = datetime.now().date() - timedelta(days=days_ago)
    discovery_date = incident_date + timedelta(days=random.randint(0, 5))
    
    cat = random.choice(cat_objects)
    sev = random.choice(severities)
    stat = random.choice(statuses)
    proc = random.choice(processes) if processes else None
    
    incident = OpRiskIncident.objects.create(
        title=f"Evento Operacional: {cat.name} - {i+1:03d}",
        description=f"Se detectó un evento relacionado con {cat.name} durante las operaciones normales.",
        incident_date=incident_date,
        discovery_date=discovery_date,
        category=cat,
        process=proc,
        severity=sev,
        status=stat,
        reported_by=random.choice(users),
        root_cause_analysis="Falta de controles adecuados" if stat == 'closed' else ""
    )
    incidents_created += 1

    # Generate 1 or 2 Potential Losses for this incident
    num_losses = random.randint(1, 2)
    for j in range(num_losses):
        gross = random.uniform(100.0, 50000.0)
        recovery = random.uniform(0.0, gross * 0.8) # Recover up to 80%
        
        pl = PotentialLoss.objects.create(
            detection_date=discovery_date,
            process=proc,
            subprocess=random.choice(subprocesses) if subprocesses else None,
            area=random.choice(areas) if areas else None,
            loss_type=random.choice(loss_types),
            description=f"Pérdida preliminar vinculada a incidente {incident.id}",
            estimated_amount=gross,
            currency='PEN',
            status='linked',
            priority=sev.lower(),
            responsible=random.choice(users),
            incident=incident,
            gross_loss=gross,
            recovery_amount=recovery,
            created_by=user
        )
    
    # Let the incident recalculate its totals
    incident.update_totals()

# 5. Create Action Plans linked to the Risks
print("Generando Planes de Acción...")
ap_statuses = ['pending', 'in_progress', 'completed', 'overdue']

for i in range(25):
    days_ago = random.randint(1, 100)
    start_date = datetime.now().date() - timedelta(days=days_ago)
    due_date = start_date + timedelta(days=random.randint(10, 60))
    stat = random.choice(ap_statuses)
    
    progress = 100 if stat == 'completed' else (random.randint(10, 90) if stat == 'in_progress' else 0)
    comp_date = start_date + timedelta(days=random.randint(5, 50)) if stat == 'completed' else None
    
    ap = ActionPlan.objects.create(
        title=f"Plan de Acción Mitigatorio {i+1:03d}",
        description="Implementar nuevos controles para reducir la probabilidad del riesgo asociado.",
        risk=random.choice(risks_list),
        responsible=random.choice(users),
        start_date=start_date,
        due_date=due_date,
        completion_date=comp_date,
        status=stat,
        progress=progress
    )

print(f"Completado: Se generaron {incidents_created} eventos, sus posibles pérdidas, y 25 planes de acción.")
