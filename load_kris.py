import os
import django
from datetime import date, timedelta
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.op_risk.models import Risk, Process, KeyRiskIndicator, KRIReading

kris_data = [
    {
        "name": "% de Mora de Cartera",
        "description": "Porcentaje de la cartera total que se encuentra con atraso mayor a 30 días.",
        "risk_keyword": "Deterioro acelerado de cartera",
        "green": 4.0,
        "yellow": 6.0,
        "red": 8.0,
        "readings": [3.8, 4.5, 6.2]  # from oldest to newest
    },
    {
        "name": "N° de Créditos Aprobados por Excepción",
        "description": "Cantidad mensual de créditos que se aprueban fuera de los parámetros del manual de crédito.",
        "risk_keyword": "Aprobación de créditos",
        "green": 5,
        "yellow": 10,
        "red": 15,
        "readings": [3, 8, 12]
    },
    {
        "name": "Horas de Caída del Sistema Core",
        "description": "Número de horas acumuladas en el mes que el sistema principal no estuvo disponible.",
        "risk_keyword": "Caída del core",
        "green": 1.0,
        "yellow": 3.0,
        "red": 5.0,
        "readings": [0, 0.5, 2.5]
    },
    {
        "name": "Ratio de Cobertura de Liquidez (RCL)",
        "description": "Nivel de activos líquidos disponibles frente a los pasivos de corto plazo.",
        "risk_keyword": "Incumplimiento de pagos",
        "green": 120, # Higher is better, so the logic might be inverted, but standard thresholds in this model usually check green_threshold <= ... wait. 
                      # The model says Green (<=), Yellow(<=), Red(>). For ratios, we'll treat it as % de brecha de liquidez.
                      # Let's rename to "% Brecha de Liquidez (Negativa)"
    },
    {
        "name": "% Brecha de Liquidez",
        "description": "Porcentaje de la brecha de liquidez negativa frente al patrimonio.",
        "risk_keyword": "Incumplimiento de pagos",
        "green": 5.0,
        "yellow": 10.0,
        "red": 15.0,
        "readings": [3.2, 5.5, 11.0]
    },
    {
        "name": "Diferencias de Caja Mensual (Soles)",
        "description": "Suma total de faltantes de caja reportados en el mes en toda la red de agencias.",
        "risk_keyword": "Diferencias de caja",
        "green": 500,
        "yellow": 1500,
        "red": 3000,
        "readings": [300, 800, 450]
    },
    {
        "name": "N° de Reclamos de Socios No Atendidos",
        "description": "Cantidad de reclamos que superaron el plazo legal (30 días) sin respuesta al cierre de mes.",
        "risk_keyword": "Reclamos reiterados",
        "green": 0,
        "yellow": 5,
        "red": 10,
        "readings": [0, 2, 7]
    },
    {
        "name": "Multas Pagadas a Reguladores",
        "description": "Monto acumulado en miles de soles por multas pagadas a la SBS u otros reguladores en el año.",
        "risk_keyword": "Sanción por reportes",
        "green": 0,
        "yellow": 5,
        "red": 10,
        "readings": [0, 0, 4.6]
    },
    {
        "name": "Rotación de Personal Clave (%)",
        "description": "Porcentaje de personal crítico o estratégico que renunció en el último trimestre.",
        "risk_keyword": "Rotación de personal",
        "green": 5.0,
        "yellow": 10.0,
        "red": 15.0,
        "readings": [3.0, 6.5, 9.0]
    },
    {
        "name": "Operaciones Inusuales Pendientes de Análisis",
        "description": "Número de alertas PLAFT que tienen más de 15 días sin haber sido analizadas o descartadas.",
        "risk_keyword": "No detección de operaciones inusuales",
        "green": 10,
        "yellow": 30,
        "red": 50,
        "readings": [5, 12, 35]
    },
    {
        "name": "Porcentaje de Concentración en Top 20 Depositantes",
        "description": "Porcentaje que representan los 20 mayores depositantes sobre el total de captaciones.",
        "risk_keyword": "Concentración excesiva",
        "green": 15.0,
        "yellow": 25.0,
        "red": 35.0,
        "readings": [14.5, 18.2, 26.0]
    }
]

created_count = 0

for kdata in kris_data:
    if "readings" not in kdata:
        continue
        
    risk = Risk.objects.filter(name__icontains=kdata["risk_keyword"]).first()
    process = risk.process if risk else None
    
    kri, created = KeyRiskIndicator.objects.get_or_create(
        name=kdata["name"],
        defaults={
            "description": kdata["description"],
            "green_threshold": kdata["green"],
            "yellow_threshold": kdata["yellow"],
            "red_threshold": kdata["red"],
            "risk": risk,
            "process": process,
        }
    )
    if created:
        created_count += 1
        
        # Add historical readings
        today = date.today()
        for i, val in enumerate(kdata["readings"]):
            reading_date = today - timedelta(days=(len(kdata["readings"]) - i) * 30) # approx 1 month apart
            KRIReading.objects.create(
                kri=kri,
                date=reading_date,
                value=val,
                notes=f"Lectura automática del periodo {reading_date.strftime('%Y-%m')}"
            )

print(f"KRIs generated successfully: {created_count} KRIs created.")
