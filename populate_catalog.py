# -*- coding: utf-8 -*-
from apps.op_risk.models import Macroprocess, Process, Subprocess, Activity
from apps.catalogs.models import Position

data = [
    # Dirección estratégica
    ("Dirección estratégica", "Planeamiento institucional", "Formulación estratégica", "Diagnóstico, objetivos, metas, plan anual", "Gerente General", "ALTA", "Información financiera, riesgo, mercado"),
    ("Dirección estratégica", "Planeamiento institucional", "Seguimiento de plan", "KPI, avance de metas, reuniones", "Gerente General", "ALTA", "Reportes de gestión"),
    
    # Gobierno corporativo
    ("Gobierno corporativo", "Gestión del consejo", "Sesiones y acuerdos", "Convocatoria, agenda, actas, acuerdos", "Miembro del Consejo de Administración", "ALTA", "Secretaría, cumplimiento"),
    ("Gobierno corporativo", "Comités", "Comité de riesgos", "Revisión de mapas, eventos, acciones", "Jefe de Riesgos", "ALTA", "Riesgo operacional, crédito, liquidez"),
    ("Gobierno corporativo", "Comités", "Comité de auditoría", "Seguimiento hallazgos, planes, controles", "Auditor Interno", "ALTA", "Auditoría, controles"),
    
    # Cumplimiento
    ("Cumplimiento", "Normativa y supervisión", "Seguimiento regulatorio", "Identificación, implementación, evidencias", "Oficial de Cumplimiento", "ALTA", "SBS, PLAFT, auditoría"),
    ("Cumplimiento", "PLAFT", "Debida diligencia", "Perfilado, monitoreo, alertas", "Oficial de Cumplimiento", "ALTA", "Captación, créditos"),
    ("Cumplimiento", "PLAFT", "Monitoreo transaccional", "Reglas, alertas, análisis", "Oficial de Cumplimiento", "ALTA", "Sistema transaccional"),
    ("Cumplimiento", "PLAFT", "Reportes regulatorios", "ROS, inusuales, umbrales", "Oficial de Cumplimiento", "ALTA", "Información consolidada"),
    
    # Gestión integral de riesgos
    ("Gestión integral de riesgos", "GIR", "Política y apetito de riesgo", "Definir límites, tolerancias, métricas", "Jefe de Riesgos", "ALTA", "Consejo, gerencia"),
    ("Gestión integral de riesgos", "GIR", "Monitoreo integral", "Informes, alertas, escalamiento", "Jefe de Riesgos", "ALTA", "Todas las áreas"),
    
    # Riesgo operacional
    ("Riesgo operacional", "Identificación", "Levantamiento de eventos", "Registro, causa, pérdida", "Jefe de Riesgos", "ALTA", "Todas las áreas"),
    ("Riesgo operacional", "Evaluación", "Matriz y KRIs", "Priorización, semáforos", "Jefe de Riesgos", "ALTA", "Procesos, controles"),
    ("Riesgo operacional", "Mitigación", "Planes de acción", "Seguimiento, cierre", "Jefe de Riesgos", "ALTA", "Gerencia, auditoría"),
    
    # Control interno
    ("Control interno", "SCI", "Autoevaluación", "Levantamiento, pruebas, seguimiento", "Auditor Interno", "ALTA", "Procesos, hallazgos"),
    
    # Ética y conducta
    ("Ética y conducta", "Integridad institucional", "Canal de denuncias", "Recepción, análisis, investigación", "Oficial de Cumplimiento", "MEDIA", "RRHH, legal"),
    
    # Captación
    ("Captación", "Ahorros y depósitos", "Apertura de cuentas", "KYC, contrato, parametrización", "Jefe de Operaciones", "ALTA", "Cumplimiento, sistemas"),
    ("Captación", "Ahorros y depósitos", "Administración de cuentas", "Movimientos, intereses, estados", "Jefe de Operaciones", "ALTA", "Core, contabilidad"),
    ("Captación", "Ahorros y depósitos", "Cierre de cuentas", "Validación saldos, bloqueo, pago", "Jefe de Operaciones", "MEDIA", "Caja, contabilidad"),
    ("Captación", "Fondos de asociados", "Aportes sociales", "Registro, actualización, devolución", "Jefe de Operaciones", "ALTA", "Socios, contabilidad"),
    
    # Colocaciones
    ("Colocaciones", "Originación de crédito", "Prospección y preevaluación", "Recepción solicitud, filtros", "Analista de Créditos", "ALTA", "Comercial, información socio"),
    ("Colocaciones", "Originación de crédito", "Evaluación crediticia", "Capacidad pago, score, visita", "Analista de Créditos", "ALTA", "Cartera, buró, ingresos"),
    ("Colocaciones", "Originación de crédito", "Aprobación", "Comité, niveles, condiciones", "Jefe de Créditos", "ALTA", "Política, riesgo"),
    ("Colocaciones", "Desembolso", "Formalización", "Contrato, pagaré, garantías", "Jefe de Operaciones", "ALTA", "Legal, tesorería"),
    ("Colocaciones", "Administración de cartera", "Seguimiento", "Mora, reprogramación, refinanciación", "Jefe de Cobranzas", "ALTA", "Cobranza, riesgo"),
    ("Colocaciones", "Administración de cartera", "Clasificación y provisiones", "Deterioro, castigos, provisión", "Jefe de Riesgos", "ALTA", "Anexo 6, balance"),
    
    # Recuperación
    ("Recuperación", "Cobranza", "Gestión preventiva", "Recordatorios, promesas de pago", "Jefe de Cobranzas", "ALTA", "Sistemas, cartera"),
    ("Recuperación", "Cobranza", "Cobranza administrativa", "Llamadas, visitas, acuerdos", "Jefe de Cobranzas", "ALTA", "Información de mora"),
    ("Recuperación", "Cobranza", "Cobranza judicial", "Patrocinios, demandas, garantías", "Asesor Legal", "ALTA", "Legal, cartera"),
    
    # Servicios al socio
    ("Servicios al socio", "Atención y servicios", "Atención de consultas", "PQR, reclamos, orientación", "Jefe de Agencia", "MEDIA", "Operaciones, cumplimiento"),
    ("Servicios al socio", "Atención y servicios", "Actualización de datos", "DNI, domicilio, actividad", "Jefe de Agencia", "MEDIA", "KYC, cumplimiento"),
    
    # Tesorería
    ("Tesorería", "Liquidez", "Programación de caja", "Flujo diario, posición, brechas", "Gerente de Finanzas", "ALTA", "Ahorros, créditos, pagos"),
    ("Tesorería", "Liquidez", "Gestión de excedentes", "Inversiones, depósitos, rentabilidad", "Gerente de Finanzas", "ALTA", "Consejo, límites"),
    ("Tesorería", "Pagos", "Pagos a proveedores", "Validación, autorización, ejecución", "Gerente de Finanzas", "ALTA", "Compras, autorizaciones"),
    ("Tesorería", "Pagos", "Pagos a socios", "Ahorros, retiros, retiros de aportes", "Recibidor Pagador (Cajero)", "ALTA", "Sistema, liquidez"),
    ("Tesorería", "Conciliaciones", "Bancarias", "Comparación, ajustes, diferencias", "Contador General", "ALTA", "Bancos, contabilidad"),
    ("Tesorería", "Conciliaciones", "Cajas", "Arqueos, faltantes, sobrantes", "Contador General", "ALTA", "Operaciones"),
    
    # Finanzas
    ("Finanzas", "Presupuesto", "Formulación presupuestal", "Ingresos, gastos, metas", "Gerente de Finanzas", "MEDIA", "Planeamiento"),
    ("Finanzas", "Presupuesto", "Control presupuestal", "Desviaciones, análisis", "Gerente de Finanzas", "MEDIA", "Contabilidad"),
    
    # Contabilidad
    ("Contabilidad", "Registro contable", "Registro diario", "Asientos, validación, cierres", "Contador General", "ALTA", "Operaciones, tesorería"),
    ("Contabilidad", "Reportes", "Estados financieros", "Balance, resultados, anexos", "Contador General", "ALTA", "Sistemas, tesorería"),
    ("Contabilidad", "Cierres", "Cierre mensual", "Ajustes, provisiones, conciliación", "Contador General", "ALTA", "Todas las áreas"),
    
    # RRHH
    ("RRHH", "Selección", "Reclutamiento", "Convocatoria, filtro, contratación", "Jefe de Recursos Humanos", "MEDIA", "Jefaturas"),
    ("RRHH", "Administración", "Legajos y nómina", "Contratos, asistencia, planillas", "Jefe de Recursos Humanos", "ALTA", "Legal, gerencia"),
    ("RRHH", "Capacitación", "Formación", "Inducción, riesgo, ética, PLAFT", "Jefe de Recursos Humanos", "MEDIA", "Cumplimiento"),
    
    # TI
    ("TI", "Soporte", "Mesa de ayuda", "Tickets, incidentes, escalamiento", "Jefe de Sistemas y TI", "ALTA", "Usuarios, core"),
    ("TI", "Seguridad", "Accesos y perfiles", "Altas, cambios, bajas, monitoreo", "Jefe de Sistemas y TI", "ALTA", "RRHH, usuarios"),
    ("TI", "Continuidad", "Backups y DRP", "Copias, pruebas, recuperación", "Jefe de Sistemas y TI", "ALTA", "Infraestructura"),
    
    # Compras
    ("Compras", "Abastecimiento", "Requerimientos", "Solicitud, evaluación, orden compra", "Jefe de Administración", "MEDIA", "Presupuesto"),
    ("Compras", "Contratación", "Contratos proveedores", "Evaluación, firma, control", "Jefe de Administración", "MEDIA", "Jurídica, gerencia"),
    
    # Legal
    ("Legal", "Gestión legal", "Contratos y garantías", "Revisión, redacción, custodia", "Asesor Legal", "ALTA", "Créditos, compras"),
    ("Legal", "Recuperación legal", "Procesos judiciales", "Demandas, medidas, seguimiento", "Asesor Legal", "ALTA", "Cobranza, cartera"),
    
    # Archivo
    ("Archivo", "Gestión documental", "Custodia", "Clasificación, archivo, retención", "Jefe de Administración", "MEDIA", "Todas las áreas"),
    
    # Auditoría interna
    ("Auditoría interna", "Evaluación independiente", "Plan anual", "Programación, ejecución", "Auditor Interno", "ALTA", "Riesgos, procesos"),
    ("Auditoría interna", "Seguimiento", "Observaciones", "Validación de cierres", "Auditor Interno", "ALTA", "Todas las áreas"),
]

# Fetch positions mapping
positions = {p.name.lower(): p for p in Position.objects.all()}

def find_position(name):
    # Some basic fuzzy matching
    nl = name.lower()
    if nl in positions:
        return positions[nl]
    # Fallbacks
    if "consejo" in nl:
        return positions.get("miembro del consejo de administración")
    if "caja" in nl and not "jefe" in nl:
        return positions.get("recibidor pagador (cajero)")
    if "legal" in nl:
        return positions.get("asesor legal")
    if "riesgo" in nl:
        return positions.get("jefe de riesgos")
    if "cumplimiento" in nl:
        return positions.get("oficial de cumplimiento")
    if "auditor" in nl:
        return positions.get("auditor interno")
    return None

created_stats = {'macro': 0, 'process': 0, 'subprocess': 0, 'activity': 0}

for m_name, p_name, s_name, act_name, resp_name, crit, dep in data:
    pos = find_position(resp_name)
    area = pos.department if pos else None
    
    macro, created = Macroprocess.objects.get_or_create(
        name=m_name,
        defaults={'owner_position': pos, 'owner_area': area}
    )
    if created: created_stats['macro'] += 1
    
    process, created = Process.objects.get_or_create(
        macroprocess=macro,
        name=p_name,
        defaults={
            'criticality': crit,
            'owner_position': pos,
            'owner_area': area
        }
    )
    if created: created_stats['process'] += 1
    
    subprocess, created = Subprocess.objects.get_or_create(
        process=process,
        name=s_name,
        defaults={
            'owner_position': pos,
            'owner_area': area
        }
    )
    if created: created_stats['subprocess'] += 1
    
    activity, created = Activity.objects.get_or_create(
        subprocess=subprocess,
        name=act_name,
        defaults={
            'owner_position': pos,
            'owner_area': area
        }
    )
    if created: created_stats['activity'] += 1

print(f"Catalog loaded successfully. Created: {created_stats}")
