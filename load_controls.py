import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.op_risk.models import Risk, Control

controls_data = [
    {
        "risk_keywords": ["Plan institucional"],
        "name": "Comité de Planeamiento Trimestral",
        "description": "Revisión trimestral del cumplimiento de metas estratégicas con la Alta Dirección.",
        "type": "DETECTIVE",
        "periodicity": "Trimestral",
        "design_efficacy": 85,
        "operational_effectiveness": 80
    },
    {
        "risk_keywords": ["Decisiones sin sustento"],
        "name": "Manual y Reglamento de Comités",
        "description": "Exigencia de actas formales y validación de quórum mínimo antes de cada sesión.",
        "type": "PREVENTIVE",
        "periodicity": "Por evento",
        "design_efficacy": 90,
        "operational_effectiveness": 95
    },
    {
        "risk_keywords": ["Incumplimiento regulatorio"],
        "name": "Matriz de Seguimiento Normativo",
        "description": "Matriz actualizada por Cumplimiento para asegurar la implementación de normativas SBS.",
        "type": "DETECTIVE",
        "periodicity": "Mensual",
        "design_efficacy": 95,
        "operational_effectiveness": 85
    },
    {
        "risk_keywords": ["Fraude interno en el otorgamiento", "Aprobación de créditos con documentación falsa", "Sobreendeudamiento"],
        "name": "Comité de Créditos Colegiado y Validación en Buró",
        "description": "Ningún crédito es aprobado por una sola persona. Validación obligatoria en centrales de riesgo.",
        "type": "PREVENTIVE",
        "periodicity": "Diario",
        "design_efficacy": 95,
        "operational_effectiveness": 90
    },
    {
        "risk_keywords": ["Robo de información", "ciberataque", "Seguridad de la información"],
        "name": "Firewall de Nueva Generación e IDS",
        "description": "Sistema de prevención de intrusiones y segmentación de red para proteger los datos de los socios.",
        "type": "PREVENTIVE",
        "periodicity": "Continuo",
        "design_efficacy": 90,
        "operational_effectiveness": 85
    },
    {
        "risk_keywords": ["Diferencias de caja"],
        "name": "Arqueos Inopinados de Caja",
        "description": "Auditoría Interna o el Jefe de Agencia realiza arqueos sorpresivos sin previo aviso.",
        "type": "DETECTIVE",
        "periodicity": "Semanal",
        "design_efficacy": 90,
        "operational_effectiveness": 85
    },
    {
        "risk_keywords": ["Desembolso erróneo"],
        "name": "Control Dual en Desembolsos",
        "description": "Todo desembolso requiere el ingreso por el asesor y la autorización en sistema por el Jefe de Agencia.",
        "type": "PREVENTIVE",
        "periodicity": "Diario",
        "design_efficacy": 100,
        "operational_effectiveness": 95
    },
    {
        "risk_keywords": ["Pérdida por gestión tardía de morosidad", "Deterioro acelerado de cartera", "Refinanciaciones improductivas"],
        "name": "Alertas Tempranas y Comité de Morosidad",
        "description": "Reporte diario de morosidad y reunión semanal para revisar las carteras en riesgo.",
        "type": "DETECTIVE",
        "periodicity": "Semanal",
        "design_efficacy": 85,
        "operational_effectiveness": 80
    },
    {
        "risk_keywords": ["Incumplimiento de pagos por insuficiente caja"],
        "name": "Comité ALCO y Flujo de Caja Proyectado",
        "description": "Seguimiento diario de la posición de liquidez y reuniones mensuales del Comité de Activos y Pasivos.",
        "type": "PREVENTIVE",
        "periodicity": "Diario/Mensual",
        "design_efficacy": 95,
        "operational_effectiveness": 90
    },
    {
        "risk_keywords": ["Retiro masivo de ahorros", "Concentración excesiva de depósitos"],
        "name": "Plan de Contingencia de Liquidez y Diversificación",
        "description": "Límites máximos de captación por socio y líneas de crédito de contingencia con bancos de segundo piso.",
        "type": "PREVENTIVE",
        "periodicity": "Mensual",
        "design_efficacy": 85,
        "operational_effectiveness": 85
    },
    {
        "risk_keywords": ["Errores en asientos", "Información financiera errónea"],
        "name": "Conciliación Contable-Operativa Automática",
        "description": "El sistema concilia diariamente los saldos de cartera/captaciones contra el balance contable.",
        "type": "DETECTIVE",
        "periodicity": "Diario",
        "design_efficacy": 90,
        "operational_effectiveness": 90
    },
    {
        "risk_keywords": ["Diferencias bancarias"],
        "name": "Conciliación Bancaria Diaria",
        "description": "Revisión diaria de los extractos bancarios frente a los movimientos de tesorería.",
        "type": "DETECTIVE",
        "periodicity": "Diario",
        "design_efficacy": 95,
        "operational_effectiveness": 90
    },
    {
        "risk_keywords": ["Caída del core", "Pérdida de información"],
        "name": "Plan de Continuidad de Negocio (BCP) y Backups Externos",
        "description": "Copias de seguridad diarias cifradas en sitio alterno y pruebas semestrales de restauración.",
        "type": "CORRECTIVE",
        "periodicity": "Diario/Semestral",
        "design_efficacy": 95,
        "operational_effectiveness": 85
    },
    {
        "risk_keywords": ["No detección de operaciones inusuales", "Sanción por reportes"],
        "name": "Sistema de Monitoreo Transaccional PLAFT",
        "description": "Alertas automáticas en el core bancario que detienen transacciones que superan el perfil del socio.",
        "type": "DETECTIVE",
        "periodicity": "Diario",
        "design_efficacy": 90,
        "operational_effectiveness": 80
    },
    {
        "risk_keywords": ["Toma de decisiones sin información"],
        "name": "Tablero de Control de Gerencia (BI)",
        "description": "Dashboards automatizados y conectados directamente a la base de datos para evitar manipulación.",
        "type": "PREVENTIVE",
        "periodicity": "Diario",
        "design_efficacy": 95,
        "operational_effectiveness": 90
    },
    {
        "risk_keywords": ["Rotación de personal", "Errores por personal no capacitado"],
        "name": "Plan de Sucesión y Capacitación Continua",
        "description": "Programa de retención de talentos clave y plataforma virtual de capacitación obligatoria anual.",
        "type": "PREVENTIVE",
        "periodicity": "Anual",
        "design_efficacy": 80,
        "operational_effectiveness": 75
    },
    {
        "risk_keywords": ["Falla de proveedor"],
        "name": "Evaluación Anual de Proveedores (SLA)",
        "description": "Revisión anual del cumplimiento de los Acuerdos de Nivel de Servicio (SLA) con proveedores críticos.",
        "type": "DETECTIVE",
        "periodicity": "Anual",
        "design_efficacy": 85,
        "operational_effectiveness": 80
    },
    {
        "risk_keywords": ["Prescripción o pérdida de garantías", "Contratos mal redactados"],
        "name": "Plantillas Legales Estandarizadas y Alertas Judiciales",
        "description": "Uso de proformas aprobadas por asesoría externa y sistema de alertas para fechas de prescripción.",
        "type": "PREVENTIVE",
        "periodicity": "Mensual",
        "design_efficacy": 90,
        "operational_effectiveness": 85
    },
    {
        "risk_keywords": ["Hallazgos no cerrados"],
        "name": "Comité de Auditoría",
        "description": "Reunión del Comité de Auditoría con el Consejo de Vigilancia para exigir planes de acción.",
        "type": "CORRECTIVE",
        "periodicity": "Mensual",
        "design_efficacy": 90,
        "operational_effectiveness": 80
    },
    {
        "risk_keywords": ["Reclamos reiterados"],
        "name": "Libro de Reclamaciones Virtual y Seguimiento de Tiempos",
        "description": "Plataforma que alerta cuando un reclamo está cerca del plazo normativo de atención.",
        "type": "DETECTIVE",
        "periodicity": "Diario",
        "design_efficacy": 95,
        "operational_effectiveness": 90
    },
    {
        "risk_keywords": ["Pérdida de expedientes físicos"],
        "name": "Digitalización Inmediata y Custodia Segura",
        "description": "Escaneo de legajos de crédito el mismo día del desembolso y custodia en bóveda ignífuga.",
        "type": "PREVENTIVE",
        "periodicity": "Diario",
        "design_efficacy": 95,
        "operational_effectiveness": 85
    }
]

created_count = 0
for cdata in controls_data:
    control, created = Control.objects.get_or_create(
        name=cdata["name"],
        defaults={
            "description": cdata["description"],
            "type": cdata["type"],
            "periodicity": cdata["periodicity"],
            "design_efficacy": cdata["design_efficacy"],
            "operational_effectiveness": cdata["operational_effectiveness"],
        }
    )
    if created:
        created_count += 1
    
    # Associate risks
    for keyword in cdata["risk_keywords"]:
        matched_risks = Risk.objects.filter(name__icontains=keyword)
        for risk in matched_risks:
            control.risks.add(risk)

print(f"Controls generated successfully: {created_count} controls created.")
