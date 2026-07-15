# -*- coding: utf-8 -*-
import os
import sys
import django

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from catalogs.models import Position

cargos = [
    ("Gerente General", "Máxima autoridad administrativa, responsable de la gestión integral de la cooperativa."),
    ("Gerente de Finanzas", "Responsable de la planeación financiera, tesorería y fondeo."),
    ("Gerente de Riesgos", "Responsable de la gestión integral de riesgos (crédito, liquidez, mercado, operacional)."),
    ("Gerente de Negocios", "Responsable de la estrategia comercial y colocación de créditos."),
    ("Gerente de Operaciones", "Responsable del back-office, procesos operativos y red de agencias."),
    ("Auditor Interno", "Responsable de evaluar y mejorar la eficacia de los procesos de gestión de riesgos y control."),
    ("Oficial de Cumplimiento", "Responsable del Sistema de Prevención de Lavado de Activos y Financiamiento del Terrorismo (SPLAFT)."),
    ("Jefe de Créditos", "Supervisa la evaluación, aprobación y desembolso de créditos."),
    ("Jefe de Cobranzas", "Responsable de la recuperación de la cartera morosa y gestión de cobranza."),
    ("Jefe de Sistemas y TI", "Responsable de la infraestructura tecnológica, seguridad de la información y sistemas."),
    ("Jefe de Recursos Humanos", "Responsable de la gestión del talento, planillas y clima laboral."),
    ("Jefe de Contabilidad / Contador General", "Responsable de los estados financieros, cumplimiento tributario y reportes normativos."),
    ("Administrador de Agencia", "Responsable de la gestión operativa y comercial de una agencia o sucursal."),
    ("Analista de Riesgos", "Evalúa y monitorea los riesgos de la cooperativa."),
    ("Analista de Créditos", "Evalúa las solicitudes de crédito y determina la capacidad de pago de los socios."),
    ("Asesor de Negocios", "Promueve y vende los productos financieros, captando y evaluando socios en campo."),
    ("Gestor de Cobranza", "Realiza la cobranza de campo y telefónica de los créditos atrasados."),
    ("Recibidor Pagador (Cajero)", "Realiza las transacciones de caja, depósitos, retiros y pagos."),
    ("Asesor de Plataforma / Atención al Socio", "Brinda información, afilia nuevos socios y atiende consultas y reclamos."),
    ("Asistente de Operaciones", "Apoya en labores de back-office, revisión de expedientes y conciliaciones."),
    ("Asistente Contable", "Apoya en el registro de comprobantes y conciliaciones bancarias."),
    ("Soporte Técnico / Asistente TI", "Atiende requerimientos tecnológicos y brinda soporte a usuarios."),
    ("Miembro del Consejo de Administración", "Directivo responsable de la dirección estratégica de la COOPAC."),
    ("Miembro del Consejo de Vigilancia", "Directivo responsable del control y fiscalización de la COOPAC."),
    ("Miembro del Comité de Riesgos", "Directivo que supervisa la gestión de riesgos de la entidad.")
]

# Delete corrupted positions
Position.objects.all().delete()

# Create correct positions
for nombre, desc in cargos:
    Position.objects.create(name=nombre, description=desc, is_active=True)

print(f"Se crearon {Position.objects.count()} cargos correctamente.")
