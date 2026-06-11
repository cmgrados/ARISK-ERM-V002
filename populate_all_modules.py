import os
import django
import random
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from operational_risk.models import COSOComponent, COSOPrinciple, COSOAssessment, OpRiskIncident
from risks.models import Risk, RiskAssessment, ProbabilityScale, ImpactScale
from action_plans.models import ActionPlan, ActionFollowUp
from users.models import User

print("Iniciando inyección de datos de simulación para todos los submódulos...")

user = User.objects.first()
if not user:
    user = User.objects.create(username="sysadmin", is_staff=True, is_superuser=True)

# 1. COSO III - Componentes y Principios
coso_structure = {
    "Entorno de Control": [
        ("P1", "Demuestra compromiso con la integridad y los valores éticos"),
        ("P2", "Ejerce responsabilidad de supervisión"),
        ("P3", "Establece estructura, autoridad y responsabilidad"),
        ("P4", "Demuestra compromiso para la competencia"),
        ("P5", "Hace cumplir la responsabilidad")
    ],
    "Evaluación de Riesgos": [
        ("P6", "Especifica objetivos adecuados"),
        ("P7", "Identifica y analiza los riesgos"),
        ("P8", "Evalúa el riesgo de fraude"),
        ("P9", "Identifica y analiza cambios importantes")
    ],
    "Actividades de Control": [
        ("P10", "Selecciona y desarrolla actividades de control"),
        ("P11", "Selecciona y desarrolla controles generales sobre tecnología"),
        ("P12", "Se implementa a través de políticas y procedimientos")
    ],
    "Información y Comunicación": [
        ("P13", "Usa información relevante"),
        ("P14", "Comunica internamente"),
        ("P15", "Comunica externamente")
    ],
    "Actividades de Supervisión": [
        ("P16", "Realiza evaluaciones continuas y/o independientes"),
        ("P17", "Evalúa y comunica deficiencias")
    ]
}

print("-> Generando Diagnóstico COSO III...")
order = 1
for comp_name, principles in coso_structure.items():
    comp, _ = COSOComponent.objects.get_or_create(name=comp_name, defaults={'order': order})
    order += 1
    for code, p_name in principles:
        prin, _ = COSOPrinciple.objects.get_or_create(component=comp, code=code, defaults={'name': p_name})
        
        # Add random assessment
        score = random.choice([2, 3, 3, 4]) # Favor favorable scores
        COSOAssessment.objects.update_or_create(
            principle=prin,
            evaluation_date=datetime.now().date(),
            defaults={
                'score': score,
                'evidence': "Sustento de prueba documentado en informe interno.",
                'gap_analysis': "Brecha menor identificada en documentación secundaria.",
                'assessed_by': user
            }
        )

# 2. Risk Matrix (RCSA) - Evaluaciones
print("-> Generando Evaluaciones de Riesgo (Matriz RCSA)...")
prob_scales = list(ProbabilityScale.objects.all())
impact_scales = list(ImpactScale.objects.all())
risks = Risk.objects.all()
for r in risks:
    if not r.assessments.exists():
        RiskAssessment.objects.create(
            risk=r,
            inherent_probability=random.choice(prob_scales),
            inherent_impact=random.choice(impact_scales),
            comments="Evaluación generada automáticamente para la matriz."
        )

# 3. Action Plans - Seguimiento (Follow Ups)
print("-> Generando Seguimiento a Planes de Acción...")
action_plans = ActionPlan.objects.all()
for ap in action_plans:
    if random.choice([True, False]) and not ap.follow_ups.exists():
        num_followups = random.randint(1, 3)
        for i in range(num_followups):
            ActionFollowUp.objects.create(
                action_plan=ap,
                comment=f"Actualización de progreso: Fase {i+1} completada. Pendiente validación final.",
                performed_by=user
            )

print("¡Listo! Datos de prueba generados para Matriz RCSA, Diagnóstico COSO, y Seguimiento de Planes.")
