import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.op_risk.models import Macroprocess, Process, Risk, ProbabilityLevel, ImpactLevel, RiskCategory

data = """
| Gobierno | Planeamiento estratégico | Plan institucional mal formulado y sin seguimiento | Falta de información, metas irreales, baja supervisión | 4 | 3 | 12 | Alta |
| Gobierno | Gestión de comités | Decisiones sin sustento ni quórum adecuado | Debilidad de gobierno, actas incompletas | 4 | 3 | 12 | Alta |
| Cumplimiento | Normativa SBS / interna | Incumplimiento regulatorio por cambios no implementados | Falta de seguimiento normativo | 5 | 4 | 20 | Muy alta |
| Riesgo operacional | Gestión operativa | Fraude interno en el otorgamiento de créditos por colusión de asesores | Debilidad de segregación, incentivos indebidos | 5 | 4 | 20 | Muy alta |
| Riesgo operacional | Gestión operativa | Robo de información confidencial de socios por ciberataque al servidor | Controles TI débiles, accesos indebidos | 5 | 4 | 20 | Muy alta |
| Riesgo operacional | Caja / agencia | Diferencias de caja por errores o sustracción | Arqueos deficientes, presión operativa | 4 | 4 | 16 | Alta |
| Riesgo operacional | Procesos de crédito | Aprobación de créditos con documentación falsa | Validación insuficiente, simulación de ingresos | 5 | 4 | 20 | Muy alta |
| Riesgo operacional | Procesos de crédito | Desembolso erróneo o a cuenta incorrecta | Fallas de digitación y validación | 4 | 3 | 12 | Alta |
| Riesgo operacional | Créditos / cobranzas | Pérdida por gestión tardía de morosidad | Alertas débiles, seguimiento insuficiente | 4 | 4 | 16 | Alta |
| Riesgo crediticio | Evaluación y aprobación | Sobreendeudamiento del socio por análisis deficiente | Ingreso no verificado, múltiples deudas | 5 | 4 | 20 | Muy alta |
| Riesgo crediticio | Cartera | Deterioro acelerado de cartera por concentración sectorial | Concentración por actividad económica | 5 | 3 | 15 | Alta |
| Riesgo crediticio | Cartera | Refinanciaciones improductivas que ocultan mora real | Tolerancia excesiva, presión comercial | 4 | 4 | 16 | Alta |
| Liquidez | Tesorería | Incumplimiento de pagos por insuficiente caja | Brechas mal gestionadas, fondeo volátil | 5 | 4 | 20 | Muy alta |
| Liquidez | Depósitos / ahorros | Retiro masivo de ahorros por pérdida de confianza | Rumores, crisis reputacional, mala atención | 5 | 3 | 15 | Alta |
| Liquidez | Gestión de pasivos | Concentración excesiva de depósitos en pocos socios | Fondeo poco diversificado | 4 | 3 | 12 | Alta |
| Contabilidad | Registro contable | Errores en asientos, provisiones o cierre mensual | Falta de revisión, carga manual | 4 | 3 | 12 | Alta |
| Contabilidad | Estados financieros | Información financiera errónea o incompleta | Conciliaciones deficientes | 5 | 3 | 15 | Alta |
| Tesorería | Conciliaciones | Diferencias bancarias no detectadas a tiempo | Seguimiento débil, falta de automatización | 4 | 3 | 12 | Alta |
| TI | Soporte tecnológico | Caída del core o indisponibilidad del sistema | Infraestructura débil, fallas del proveedor | 5 | 4 | 20 | Muy alta |
| TI | Seguridad de la información | Acceso no autorizado por contraseñas débiles o perfiles mal definidos | Gestión deficiente de accesos | 5 | 4 | 20 | Muy alta |
| TI | Respaldo y continuidad | Pérdida de información por fallas de backup | Backups no verificados o incompletos | 5 | 3 | 15 | Alta |
| PLAFT | Cumplimiento LA/FT | No detección de operaciones inusuales | Reglas insuficientes, análisis tardío | 5 | 3 | 15 | Alta |
| PLAFT | Cumplimiento LA/FT | Sanción por reportes no enviados o tardíos | Incumplimiento de plazos y controles | 5 | 3 | 15 | Alta |
| Gobierno | Consejo / gerencia | Toma de decisiones sin información confiable | Reportes tardíos o manipulados | 4 | 3 | 12 | Alta |
| Recursos Humanos | Personal | Rotación de personal clave y pérdida de conocimiento | Clima laboral, baja retención | 4 | 3 | 12 | Alta |
| Recursos Humanos | Capacitación | Errores por personal no capacitado | Inducción insuficiente | 4 | 4 | 16 | Alta |
| Proveedores | Terceros críticos | Falla de proveedor de core, soporte o comunicaciones | Contratos débiles, SLA inexistente | 5 | 3 | 15 | Alta |
| Legal | Recuperación judicial | Prescripción o pérdida de garantías | Seguimiento legal tardío | 5 | 3 | 15 | Alta |
| Legal | Contratos | Contratos mal redactados o no exigibles | Debilidad jurídica | 4 | 3 | 12 | Alta |
| Auditoría interna | Supervisión | Hallazgos no cerrados oportunamente | Falta de seguimiento y presión operativa | 4 | 3 | 12 | Alta |
| Atención al socio | Servicio | Reclamos reiterados y deterioro reputacional | Mala atención, tiempos largos | 3 | 4 | 12 | Alta |
| Archivo / documentación | Custodia | Pérdida de expedientes físicos o digitales | Orden documental deficiente | 4 | 3 | 12 | Alta |
"""

lines = [line.strip() for line in data.strip().split('\n') if line.strip()]

category = RiskCategory.objects.first()

for line in lines:
    parts = [p.strip() for p in line.split('|')[1:-1]]
    if len(parts) < 8:
        continue
    
    macro_name = parts[0]
    proc_name = parts[1]
    risk_name = parts[2]
    cause = parts[3]
    impact_lvl = int(parts[4])
    prob_lvl = int(parts[5])
    
    macro, _ = Macroprocess.objects.get_or_create(name=macro_name)
    process, _ = Process.objects.get_or_create(name=proc_name, macroprocess=macro)
    
    impact = ImpactLevel.objects.get(level=impact_lvl)
    prob = ProbabilityLevel.objects.get(level=prob_lvl)
    
    Risk.objects.get_or_create(
        name=risk_name,
        process=process,
        defaults={
            'cause': cause,
            'category': category,
            'inherent_impact': impact,
            'inherent_probability': prob,
            'status': 'APPROVED'
        }
    )

print("Risks loaded successfully.")
