import os
import django
import sys

# Set up Django
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'apps'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from operational_risk.models import OpRiskEventCategory, OpRiskIncident
from django.utils import timezone
import random
from datetime import timedelta

def load_test_data():
    # 1. Categories
    categories_data = [
        "Fraude Interno",
        "Fraude Externo",
        "Relaciones Laborales y Seguridad en el Puesto de Trabajo",
        "Clientes, Productos y Prácticas Empresariales",
        "Daños a Activos Físicos",
        "Incidencias en el Negocio y Fallos en los Sistemas",
        "Ejecución, Entrega y Gestión de Procesos"
    ]
    
    cats = []
    for cat_name in categories_data:
        cat, created = OpRiskEventCategory.objects.get_or_create(name=cat_name)
        cats.append(cat)
        print(f"Categoría {'creada' if created else 'ya existe'}: {cat_name}")

    # 2. Events
    event_titles = [
        "Phishing masivo a clientes de banca móvil",
        "Retiro no autorizado en ventanilla Agencia 01",
        "Falla en el servidor de base de datos - Core Bancario",
        "Incendio parcial en archivo central",
        "Error en conciliación de transferencias interbancarias",
        "Multa por incumplimiento en reporte regulatorio",
        "Robo de equipos portátiles en sede administrativa",
        "Interrupción de servicio ATM por vandalismo",
        "Accidente laboral en remodelación de oficina",
        "Reclamo masivo por cobro indebido de comisiones"
    ]
    
    for i, title in enumerate(event_titles):
        # Random data
        discovery_date = timezone.now() - timedelta(days=random.randint(0, 30))
        incident_date = discovery_date - timedelta(days=random.randint(0, 5))
        loss = random.randint(500, 50000)
        
        incident = OpRiskIncident.objects.create(
            title=title,
            description=f"Descripción detallada del evento: {title}. Identificado durante el monitoreo rutinario.",
            incident_date=incident_date.date(),
            discovery_date=discovery_date,
            category=random.choice(cats),
            severity=random.choice(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']),
            status=random.choice(['open', 'mitigated', 'closed']),
            gross_loss=loss,
            recovery_amount=loss * random.random() * 0.5,
        )
        print(f"Evento creado: {incident.title} (S/ {incident.gross_loss})")

if __name__ == "__main__":
    load_test_data()
