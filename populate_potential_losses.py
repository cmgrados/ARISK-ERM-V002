import os
import django
import random
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from operational_risk.models import PotentialLoss
from catalogs.models import Process, Subprocess, OrganizationalUnit
from users.models import User

users = list(User.objects.all())
if not users:
    print("No users found. Creating a default user.")
    user = User.objects.create(username="admin", is_superuser=True, is_staff=True)
    users.append(user)

processes = list(Process.objects.all())
subprocesses = list(Subprocess.objects.all())
areas = list(OrganizationalUnit.objects.all())

loss_types = [
    "Fraude Interno",
    "Fraude Externo",
    "Fallas en Sistemas",
    "Errores de Procesamiento",
    "Daños a Activos Físicos",
    "Incumplimiento Regulatorio",
    "Ciberataque / Ransomware"
]

descriptions = [
    "Se detectó una inconsistencia en el cuadre diario de caja debido a un error del cajero.",
    "El sistema de banca por internet sufrió una caída de 45 minutos impidiendo transacciones.",
    "Un proveedor externo facturó por duplicado y el sistema aprobó ambos pagos.",
    "Se identificó un intento de acceso no autorizado a los servidores de base de datos.",
    "Pérdida de documentación física original de expedientes de crédito por inundación en archivo.",
    "Multa impuesta por el regulador debido al envío tardío de reportes normativos.",
    "Error de configuración en el firewall permitió tráfico anómalo durante la madrugada."
]

observations_list = [
    "Se requiere mayor control dual en este proceso.",
    "Auditoría interna ya ha sido notificada para revisar el caso en profundidad.",
    "Se procedió a aislar el equipo afectado y se levantó un ticket con soporte.",
    "El proveedor se ha comprometido a realizar la nota de crédito correspondiente.",
    "Se está evaluando actualizar las políticas de seguridad de la información.",
    "Pendiente validación final por la gerencia de riesgos.",
    "El impacto final podría ser menor si se activa la póliza de seguros."
]

potential_losses = PotentialLoss.objects.all()
print(f"Actualizando {potential_losses.count()} posibles pérdidas...")

for pl in potential_losses:
    pl.detection_date = datetime.now().date() - timedelta(days=random.randint(1, 100))
    
    if processes:
        pl.process = random.choice(processes)
    if subprocesses:
        pl.subprocess = random.choice(subprocesses)
    if areas:
        pl.area = random.choice(areas)
        
    pl.responsible = random.choice(users)
    pl.loss_type = random.choice(loss_types)
    pl.description = random.choice(descriptions)
    pl.currency = random.choice(['PEN', 'USD'])
    pl.priority = random.choice(['low', 'medium', 'high', 'critical'])
    pl.status = random.choice(['linked', 'adjusted', 'closed'])
    pl.observations = random.choice(observations_list)
    
    # ensure estimated amount makes sense with gross_loss
    if pl.gross_loss > 0:
        pl.estimated_amount = pl.gross_loss
    else:
        pl.estimated_amount = round(random.uniform(500, 15000), 2)
        
    pl.save()

print("¡Todas las posibles pérdidas han sido completadas con información realista!")
