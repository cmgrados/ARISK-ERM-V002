import os
import sys
import django
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from strategic_risk.models import ObjetivoEstrategico, Indicador
from users.models import Organization

org = Organization.objects.first()
objetivos = ObjetivoEstrategico.objects.filter(organization=org)

kpi_templates = {
    'Financiera': [
        {'nombre': 'Ind. 1: Crecimiento', 'formula': '((Ing. N - Ing. N-1)/Ing. N-1)*100', 'peso': 25, 'unidad': 'Porcentaje', 'freq': 'ANUAL', 'medio': 'EEFF'},
        {'nombre': 'Ind. 2: Margen', 'formula': '(Utilidad / Ingresos)*100', 'peso': 25, 'unidad': 'Porcentaje', 'freq': 'MENSUAL', 'medio': 'EEFF'},
        {'nombre': 'Ind. 3: Reducción Costos', 'formula': '((Costos N-1 - Costos N)/Costos N-1)*100', 'peso': 25, 'unidad': 'Porcentaje', 'freq': 'TRIMESTRAL', 'medio': 'Reportes'},
        {'nombre': 'Ind. 4: ROI', 'formula': '((Beneficio-Inv)/Inv)*100', 'peso': 25, 'unidad': 'Porcentaje', 'freq': 'ANUAL', 'medio': 'Reportes'}
    ],
    'Clientes': [
        {'nombre': 'Ind. 1: CSAT', 'formula': '(Satisfechos / Total)*100', 'peso': 25, 'unidad': 'Porcentaje', 'freq': 'TRIMESTRAL', 'medio': 'Encuestas'},
        {'nombre': 'Ind. 2: Retención', 'formula': '((Final - Nuevos)/Inicio)*100', 'peso': 25, 'unidad': 'Porcentaje', 'freq': 'MENSUAL', 'medio': 'CRM'},
        {'nombre': 'Ind. 3: NPS', 'formula': '% Prom. - % Detract.', 'peso': 25, 'unidad': 'Puntos', 'freq': 'SEMESTRAL', 'medio': 'NPS'},
        {'nombre': 'Ind. 4: SLA Quejas', 'formula': '(SLA / Total)*100', 'peso': 25, 'unidad': 'Porcentaje', 'freq': 'MENSUAL', 'medio': 'Tickets'}
    ],
    'Procesos Internos': [
        {'nombre': 'Ind. 1: T. Ciclo', 'formula': 'T. total / Procesos', 'peso': 25, 'unidad': 'Días', 'freq': 'MENSUAL', 'medio': 'Ops'},
        {'nombre': 'Ind. 2: Defectos', 'formula': '(Defectos / Total)*100', 'peso': 25, 'unidad': 'Porcentaje', 'freq': 'SEMESTRAL', 'medio': 'Calidad'},
        {'nombre': 'Ind. 3: Auditoría', 'formula': '(Hallazgos / Total)*100', 'peso': 25, 'unidad': 'Porcentaje', 'freq': 'ANUAL', 'medio': 'Auditoría'},
        {'nombre': 'Ind. 4: Eficiencia', 'formula': '(Real / Esperado)*100', 'peso': 25, 'unidad': 'Porcentaje', 'freq': 'MENSUAL', 'medio': 'Dashboard'}
    ],
    'Aprendizaje y Crecimiento': [
        {'nombre': 'Ind. 1: Capacitación', 'formula': 'Horas / Emp', 'peso': 25, 'unidad': 'Horas', 'freq': 'ANUAL', 'medio': 'RRHH'},
        {'nombre': 'Ind. 2: Retención Talento', 'formula': '(Retenidos / Total)*100', 'peso': 25, 'unidad': 'Porcentaje', 'freq': 'TRIMESTRAL', 'medio': 'RRHH'},
        {'nombre': 'Ind. 3: Clima', 'formula': 'Puntuación', 'peso': 25, 'unidad': 'Puntos', 'freq': 'ANUAL', 'medio': 'Encuestas'},
        {'nombre': 'Ind. 4: Tecnología', 'formula': '(Completados / Planeados)*100', 'peso': 25, 'unidad': 'Porcentaje', 'freq': 'SEMESTRAL', 'medio': 'IT'}
    ]
}

# Delete existing to prevent duplicates and clean up
Indicador.objects.filter(organization=org).delete()

created_count = 0
for obj in objetivos:
    perspectiva = obj.perspectiva.nombre
    templates = kpi_templates.get(perspectiva, kpi_templates['Financiera'])
    
    for t in templates:
        # Create a unique name to verify filtering works!
        unique_name = f"{t['nombre']} - {obj.nombre[:20]}..."
        Indicador.objects.create(
            organization=org,
            objetivo=obj,
            nombre=unique_name,
            formula=t['formula'],
            peso=t['peso'],
            unidad_medida=t['unidad'],
            frecuencia_medicion=t['freq'],
            responsable='Gerente de ' + perspectiva,
            medio_verificacion=t['medio']
        )
        created_count += 1

print(f"Successfully created {created_count} unique indicators.")
