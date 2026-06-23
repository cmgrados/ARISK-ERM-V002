import os
import sys
import django
from datetime import date, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.strategic_risk.models import PortafolioPOA, ActividadPOA

def seed_activities():
    proyectos = PortafolioPOA.objects.all()
    print(f"Encontrados {proyectos.count()} proyectos.")

    actividades_sugeridas = [
        ("Definir alcance de la campaña", "Establecer objetivo, público meta, mensaje central, canales y entregables."),
        ("Elaborar cronograma operativo", "Distribuir las actividades por fechas, responsables y hitos de control."),
        ("Diseñar piezas de comunicación", "Crear banners, posts, videos, correos y otros materiales publicitarios."),
        ("Configurar campañas digitales", "Programar publicaciones, anuncios pagados, segmentación y parámetros de medición."),
        ("Ejecutar la fase 1 del proyecto", "Lanzar la primera etapa según el cronograma aprobado."),
        ("Realizar seguimiento y monitoreo", "Revisar avances, métricas, cumplimiento de plazos y alertas de desviación."),
        ("Hacer diagnóstico inicial", "Evaluar resultados preliminares, alcance, interacción y percepción de la campaña."),
        ("Preparar reportes de avance", "Emitir informes periódicos con indicadores, incidencias y decisiones tomadas."),
        ("Ajustar acciones correctivas", "Modificar mensajes, canales o segmentación según los resultados obtenidos.")
    ]

    for proyecto in proyectos:
        # Check if project already has activities
        if proyecto.actividades.exists():
            print(f"El proyecto '{proyecto.nombre_proyecto}' ya tiene actividades. Saltando.")
            continue
            
        print(f"Generando actividades para '{proyecto.nombre_proyecto}'...")
        
        # Calculate dates. Start at Jan 1st of project's year
        anio = proyecto.anio
        fecha_inicio_base = date(anio, 1, 1)
        duracion_por_actividad = 15 # 15 days each
        
        for i, (nombre, descripcion) in enumerate(actividades_sugeridas):
            fecha_inicio = fecha_inicio_base + timedelta(days=i * duracion_por_actividad)
            fecha_fin = fecha_inicio + timedelta(days=duracion_por_actividad - 1)
            
            # The activity name combining both? Or just "nombre: descripcion"?
            act_desc = f"{nombre}. {descripcion}"
            if len(act_desc) > 500:
                act_desc = act_desc[:497] + "..."
                
            predecesora = str(i) if i > 0 else ""
            
            ActividadPOA.objects.create(
                organization=proyecto.organization,
                proyecto=proyecto,
                numero=i + 1,
                descripcion=act_desc,
                fecha_inicio=fecha_inicio,
                fecha_final=fecha_fin,
                duracion=duracion_por_actividad,
                predecesora=predecesora,
                responsable=proyecto.lider_proyecto or "No asignado",
                medio_verificacion="Documento/Reporte",
                costo=proyecto.presupuesto / len(actividades_sugeridas) if proyecto.presupuesto else 1000
            )

    print("Proceso completado.")

if __name__ == '__main__':
    seed_activities()
