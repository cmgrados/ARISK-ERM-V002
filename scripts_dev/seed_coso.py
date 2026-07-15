import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from operational_risk.models import COSOComponent, COSOPrinciple

def seed_coso():
    coso_structure = {
        'Ambiente de Control': {
            'order': 1,
            'principles': [
                ('P1', 'Compromiso con la integridad y los valores éticos.'),
                ('P2', 'Independencia de la supervisión de la junta directiva.'),
                ('P3', 'Estructuras, líneas de reporte y autoridades/responsabilidades.'),
                ('P4', 'Compromiso con la competencia profesional.'),
                ('P5', 'Responsabilidad en la rendición de cuentas.'),
            ]
        },
        'Evaluación de Riesgos': {
            'order': 2,
            'principles': [
                ('P6', 'Especificación de objetivos relevantes.'),
                ('P7', 'Identificación y análisis de riesgos.'),
                ('P8', 'Evaluación del riesgo de fraude.'),
                ('P9', 'Identificación y análisis de cambios significativos.'),
            ]
        },
        'Actividades de Control': {
            'order': 3,
            'principles': [
                ('P10', 'Selección y desarrollo de actividades de control.'),
                ('P11', 'Selección y desarrollo de controles generales sobre TI.'),
                ('P12', 'Despliegue a través de políticas y procedimientos.'),
            ]
        },
        'Información y Comunicación': {
            'order': 4,
            'principles': [
                ('P13', 'Uso de información relevante.'),
                ('P14', 'Comunicación interna.'),
                ('P15', 'Comunicación externa.'),
            ]
        },
        'Actividades de Monitoreo': {
            'order': 5,
            'principles': [
                ('P16', 'Evaluaciones continuas y/o separadas.'),
                ('P17', 'Evaluación y comunicación de deficiencias.'),
            ]
        }
    }

    for comp_name, data in coso_structure.items():
        comp, created = COSOComponent.objects.get_or_create(
            name=comp_name,
            defaults={'order': data['order']}
        )
        if created:
            print(f"Componente '{comp_name}' creado.")
        
        for code, p_name in data['principles']:
            principle, p_created = COSOPrinciple.objects.get_or_create(
                component=comp,
                code=code,
                defaults={'name': p_name}
            )
            if p_created:
                print(f"  Principio '{code}' creado.")

if __name__ == "__main__":
    seed_coso()
