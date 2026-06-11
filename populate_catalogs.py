import os
import django

# Bootstrap Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from catalogs.models import OrganizationalUnit, Process, Subprocess

unidades = [
    ['CONSEJO DE ADMINISTRACION', '', 'NO', 'Nivel máximo directivo'],
    ['COMITE DE EDUCACION', 'CONSEJO DE ADMINISTRACION', 'NO', ''],
    ['COMITE ELECTORAL', 'CONSEJO DE ADMINISTRACION', 'NO', ''],
    ['SECRET. DE CONSEJO', 'CONSEJO DE ADMINISTRACION', 'NO', ''],
    ['COMITE DE RIESGOS', 'CONSEJO DE ADMINISTRACION', 'NO', ''],
    ['JEFE DE RIESGOS', 'COMITE DE RIESGOS', 'NO', ''],
    ['ASIST. DE RIESGOS', 'JEFE DE RIESGOS', 'NO', ''],
    ['COMITE PLAFT', 'CONSEJO DE ADMINISTRACION', 'NO', ''],
    ['OF. DE CUMPLIMIENTO', 'COMITE PLAFT', 'NO', ''],
    ['ASIST. DE OF. DE CUMPLIMIENTO', 'OF. DE CUMPLIMIENTO', 'NO', ''],
    ['GERENTE GENERAL', 'CONSEJO DE ADMINISTRACION', 'NO', ''],
    ['SECRET. DE GERENCIA', 'GERENTE GENERAL', 'NO', ''],
    ['ASESOR LEGAL', 'GERENTE GENERAL', 'NO', ''],
    ['COMITE DE CREDITOS', 'GERENTE GENERAL', 'NO', ''],
    ['CONSEJO DE VIGILANCIA', '', 'NO', 'Nivel de supervisión independiente'],
    ['AUDITORIA INTERNA', 'CONSEJO DE VIGILANCIA', 'NO', ''],
    ['ASIST. DE AUDITORIA', 'AUDITORIA INTERNA', 'NO', ''],
    ['UNIDAD DE TT.HH', 'GERENTE GENERAL', 'NO', 'Recursos Humanos'],
    ['SEGURIDAD', 'UNIDAD DE TT.HH', 'NO', ''],
    ['COMITES LABORALES', 'SEGURIDAD', 'NO', ''],
    ['UNIDAD DE CONTABILIDAD', 'GERENTE GENERAL', 'NO', ''],
    ['ASISTENTES CONTABLES', 'UNIDAD DE CONTABILIDAD', 'NO', ''],
    ['UNIDAD DE LOGISTICA', 'GERENTE GENERAL', 'NO', ''],
    ['ASIST. DE LOGISTICA', 'UNIDAD DE LOGISTICA', 'NO', ''],
    ['CONSERJE', 'ASIST. DE LOGISTICA', 'NO', ''],
    ['LIMPIEZA', 'CONSERJE', 'NO', ''],
    ['CAFETIN', 'LIMPIEZA', 'NO', ''],
    ['UNIDAD DE OPERACIONES', 'GERENTE GENERAL', 'NO', ''],
    ['ASIST. DE OPERACIONES', 'UNIDAD DE OPERACIONES', 'NO', ''],
    ['CAJERAS', 'ASIST. DE OPERACIONES', 'NO', ''],
    ['UNIDAD DE CREDITOS', 'GERENTE GENERAL', 'NO', ''],
    ['ANALISTAS DE CREDITOS', 'UNIDAD DE CREDITOS', 'NO', ''],
    ['ANALISTAS DE CREDITOS OTRAS OFIC.', 'UNIDAD DE CREDITOS', 'NO', ''],
    ['UNIDAD DE RECUPERACIONES', 'GERENTE GENERAL', 'NO', ''],
    ['ASIST. DE RECUPERACIONES', 'UNIDAD DE RECUPERACIONES', 'NO', ''],
    ['ADMISION', 'GERENTE GENERAL', 'NO', ''],
    ['ASIST. ADMISION', 'ADMISION', 'NO', ''],
    ['MARKETING', 'GERENTE GENERAL', 'NO', ''],
    ['ARCHIVO CENTRAL', 'GERENTE GENERAL', 'NO', ''],
    ['PLANIF. / SIST.', 'GERENTE GENERAL', 'NO', 'Sistemas y Planificación'],
    ['ASIST. SISTEMAS', 'PLANIF. / SIST.', 'NO', ''],
    ['SOP. TECNICO', 'ASIST. SISTEMAS', 'NO', ''],
    ['PREV. SOCIAL', 'GERENTE GENERAL', 'NO', ''],
    ['MED. GRAL', 'PREV. SOCIAL', 'NO', ''],
    ['T. FISICA', 'PREV. SOCIAL', 'NO', ''],
    ['GYM', 'PREV. SOCIAL', 'NO', ''],
    ['PSICOLOGIA', 'PREV. SOCIAL', 'NO', ''],
    ['PELUQUERIA', 'PREV. SOCIAL', 'NO', ''],
    ['OF. AREQUIPA', 'GERENTE GENERAL', 'SI', ''],
    ['OF. IQUITOS', 'GERENTE GENERAL', 'SI', ''],
    ['OF. PIURA', 'GERENTE GENERAL', 'SI', ''],
    ['OF. AYACUCHO', 'GERENTE GENERAL', 'SI', ''],
    ['OF. TARAPOTO', 'GERENTE GENERAL', 'SI', ''],
    ['OF. HUANCAYO', 'GERENTE GENERAL', 'SI', ''],
]

print("Insertando Unidades (Fase 1: Creación base)...")
created_units = {}
for u in unidades:
    name = u[0].strip()
    is_agency = u[2].strip() == 'SI'
    desc = u[3].strip()
    unit, _ = OrganizationalUnit.objects.get_or_create(
        name=name,
        defaults={'description': desc, 'is_agency': is_agency}
    )
    created_units[name] = unit

print("Insertando Unidades (Fase 2: Relaciones Padre-Hijo)...")
for u in unidades:
    name = u[0].strip()
    parent_name = u[1].strip()
    if parent_name and parent_name in created_units:
        unit = created_units[name]
        parent_unit = created_units[parent_name]
        unit.parent = parent_unit
        unit.save()

print(f"Total unidades insertadas/actualizadas: {OrganizationalUnit.objects.count()}")

procesos = [
    ['Gestión de Créditos', 'Proceso principal de evaluación y otorgamiento de créditos'],
    ['Gestión de Riesgo Operacional', 'Monitoreo de eventos de pérdida'],
    ['Gestión Contable', 'Procesamiento de asientos y conciliación'],
]

for p in procesos:
    Process.objects.get_or_create(
        name=p[0],
        defaults={'description': p[1]}
    )

subprocesos = [
    ['Gestión de Créditos', 'Evaluación Crediticia', 'Análisis de capacidad de pago'],
    ['Gestión de Créditos', 'Desembolso', 'Entrega de efectivo al socio'],
    ['Gestión de Riesgo Operacional', 'Registro de Posibles Pérdidas', 'Paso 1 del flujo de RO'],
]

for sp in subprocesos:
    parent_process = Process.objects.filter(name__iexact=sp[0]).first()
    if parent_process:
        Subprocess.objects.get_or_create(
            process=parent_process,
            name=sp[1],
            defaults={'description': sp[2]}
        )

print("¡Carga exitosa a la base de datos!")
