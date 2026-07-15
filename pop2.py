import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from catalogs.models import Position

cargos = [
    ("Gerente General", "M\u00e1xima autoridad administrativa, responsable de la gesti\u00f3n integral de la cooperativa."),
    ("Gerente de Finanzas", "Responsable de la planeaci\u00f3n financiera, tesorer\u00eda y fondeo."),
    ("Gerente de Riesgos", "Responsable de la gesti\u00f3n integral de riesgos (cr\u00e9dito, liquidez, mercado, operacional)."),
    ("Gerente de Negocios", "Responsable de la estrategia comercial y colocaci\u00f3n de cr\u00e9ditos."),
    ("Gerente de Operaciones", "Responsable del back-office, procesos operativos y red de agencias."),
    ("Auditor Interno", "Responsable de evaluar y mejorar la eficacia de los procesos de gesti\u00f3n de riesgos y control."),
    ("Oficial de Cumplimiento", "Responsable del Sistema de Prevenci\u00f3n de Lavado de Activos y Financiamiento del Terrorismo (SPLAFT)."),
    ("Jefe de Cr\u00e9ditos", "Supervisa la evaluaci\u00f3n, aprobaci\u00f3n y desembolso de cr\u00e9ditos."),
    ("Jefe de Cobranzas", "Responsable de la recuperaci\u00f3n de la cartera morosa y gesti\u00f3n de cobranza."),
    ("Jefe de Sistemas y TI", "Responsable de la infraestructura tecnol\u00f3gica, seguridad de la informaci\u00f3n y sistemas."),
    ("Jefe de Recursos Humanos", "Responsable de la gesti\u00f3n del talento, planillas y clima laboral."),
    ("Jefe de Contabilidad / Contador General", "Responsable de los estados financieros, cumplimiento tributario y reportes normativos."),
    ("Administrador de Agencia", "Responsable de la gesti\u00f3n operativa y comercial de una agencia o sucursal."),
    ("Analista de Riesgos", "Eval\u00faa y monitorea los riesgos de la cooperativa."),
    ("Analista de Cr\u00e9ditos", "Eval\u00faa las solicitudes de cr\u00e9dito y determina la capacidad de pago de los socios."),
    ("Asesor de Negocios", "Promueve y vende los productos financieros, captando y evaluando socios en campo."),
    ("Gestor de Cobranza", "Realiza la cobranza de campo y telef\u00f3nica de los cr\u00e9ditos atrasados."),
    ("Recibidor Pagador (Cajero)", "Realiza las transacciones de caja, dep\u00f3sitos, retiros y pagos."),
    ("Asesor de Plataforma / Atenci\u00f3n al Socio", "Brinda informaci\u00f3n, afilia nuevos socios y atiende consultas y reclamos."),
    ("Asistente de Operaciones", "Apoya en labores de back-office, revisi\u00f3n de expedientes y conciliaciones."),
    ("Asistente Contable", "Apoya en el registro de comprobantes y conciliaciones bancarias."),
    ("Soporte T\u00e9cnico / Asistente TI", "Atiende requerimientos tecnol\u00f3gicos y brinda soporte a usuarios."),
    ("Miembro del Consejo de Administraci\u00f3n", "Directivo responsable de la direcci\u00f3n estrat\u00e9gica de la COOPAC."),
    ("Miembro del Consejo de Vigilancia", "Directivo responsable del control y fiscalizaci\u00f3n de la COOPAC."),
    ("Miembro del Comit\u00e9 de Riesgos", "Directivo que supervisa la gesti\u00f3n de riesgos de la entidad.")
]

Position.objects.all().delete()
for n, d in cargos:
    Position.objects.create(name=n, description=d, is_active=True)
