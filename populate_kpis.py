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
    'FINANCIERA': [
        {'nombre': 'Crecimiento de Cartera de Crédito', 'formula': '((Cartera N - Cartera N-1)/Cartera N-1)*100', 'peso': 50, 'unidad': 'Porcentaje', 'freq': 'MENSUAL', 'medio': 'Reporte de Cartera'},
        {'nombre': 'Índice de Morosidad', 'formula': '(Cartera Atrasada / Cartera Total)*100', 'peso': 50, 'unidad': 'Porcentaje', 'freq': 'MENSUAL', 'medio': 'EEFF'}
    ],
    'SOCIO/CLIENTE': [
        {'nombre': 'Crecimiento de Base Social', 'formula': '((Socios N - Socios N-1)/Socios N-1)*100', 'peso': 50, 'unidad': 'Porcentaje', 'freq': 'TRIMESTRAL', 'medio': 'Reporte de Socios'},
        {'nombre': 'Índice de Satisfacción del Socio (CSAT)', 'formula': '(Socios Satisfechos / Total Encuestados)*100', 'peso': 50, 'unidad': 'Porcentaje', 'freq': 'SEMESTRAL', 'medio': 'Encuestas'}
    ],
    'PROCESOS INTERNOS': [
        {'nombre': 'Tiempo de Otorgamiento de Crédito', 'formula': 'Tiempo Total / Créditos Desembolsados', 'peso': 50, 'unidad': 'Días', 'freq': 'MENSUAL', 'medio': 'Sistema Core'},
        {'nombre': 'Digitalización de Transacciones', 'formula': '(Tx Digitales / Tx Totales)*100', 'peso': 50, 'unidad': 'Porcentaje', 'freq': 'MENSUAL', 'medio': 'Reporte Canales'}
    ],
    'APRENDIZAJE Y CRECIMIENTO': [
        {'nombre': 'Cumplimiento Plan de Capacitación', 'formula': '(Horas Ejecutadas / Horas Programadas)*100', 'peso': 50, 'unidad': 'Porcentaje', 'freq': 'SEMESTRAL', 'medio': 'RRHH'},
        {'nombre': 'Retención de Talento Clave', 'formula': '((Total Claves - Bajas Claves) / Total Claves)*100', 'peso': 50, 'unidad': 'Porcentaje', 'freq': 'ANUAL', 'medio': 'RRHH'}
    ]
}

# Delete existing to prevent duplicates and clean up
Indicador.objects.filter(organization=org).delete()

created_count = 0
for obj in objetivos:
    perspectiva = obj.perspectiva.nombre.upper()
    templates = kpi_templates.get(perspectiva, kpi_templates['FINANCIERA'])
    
    # Try to set a logical tipo_objetivo
    tipo = obj.tipo_objetivo if obj.tipo_objetivo else 'Estratégico'
    
    for i, t in enumerate(templates):
        # Create a specific name based on the template and the objective
        unique_name = f"Ind {i+1}: {t['nombre']} - {obj.nombre[:30]}"
        Indicador.objects.create(
            organization=org,
            objetivo=obj,
            nombre=unique_name,
            formula=t['formula'],
            peso=t['peso'],
            unidad_medida=t['unidad'],
            frecuencia_medicion=t['freq'],
            responsable='Gerencia de ' + perspectiva.capitalize(),
            medio_verificacion=t['medio'],
            tipo_objetivo=tipo
        )
        created_count += 1

print(f"Successfully created {created_count} unique indicators (2 per objective).")
