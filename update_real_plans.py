import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from action_plans.models import ActionPlan

real_plans = [
    ("Actualización de Firewall Core", "Migrar las reglas del firewall principal hacia la nueva infraestructura en la nube para mitigar ataques DDoS."),
    ("Capacitación Anual Anti-Phishing", "Ejecutar campaña interactiva y simulacros de phishing para todo el personal administrativo y operativo."),
    ("Implementación de Doble Factor (2FA)", "Obligar el uso de 2FA (Autenticador de Google/Microsoft) para el acceso a la VPN corporativa."),
    ("Auditoría de Accesos a Base de Datos", "Revisar y revocar permisos de usuarios inactivos o con privilegios excesivos en los servidores de BD."),
    ("Renovación de Póliza de Seguros", "Actualizar la póliza de riesgo cibernético y riesgo operativo con la nueva corredora."),
    ("Revisión de Contratos de Proveedores TI", "Añadir cláusulas de SLA y penalidades por caída de servicio a los 5 proveedores principales."),
    ("Simulacro de Recuperación ante Desastres (DRP)", "Apagar el servidor principal y medir el tiempo de recuperación en el sitio alterno (RTO/RPO)."),
    ("Automatización de Conciliación Bancaria", "Reemplazar las macros de Excel por un script en Python para evitar errores de digitación humana."),
    ("Actualización de Manual de Funciones (MOF)", "Reflejar las nuevas responsabilidades de control interno para el departamento de operaciones."),
    ("Mantenimiento Preventivo de UPS", "Programar mantenimiento semestral del sistema ininterrumpido de energía del Data Center principal."),
    ("Segmentación de Redes VLAN", "Separar la red de servidores críticos de la red de usuarios generales e invitados."),
    ("Campaña de Concientización COSO", "Difundir la importancia de la integridad y valores éticos mediante boletines mensuales."),
    ("Cifrado de Discos Duros en Laptops", "Aplicar BitLocker o FileVault a todas las laptops asignadas a gerencia y ejecutivos de cuenta."),
    ("Contratación de Oficial de Seguridad", "Reclutar y seleccionar a un CISO (Chief Information Security Officer) a tiempo completo."),
    ("Actualización del Plan de Continuidad (BCP)", "Incorporar escenarios de pandemia y trabajo remoto masivo al BCP institucional."),
    ("Refuerzo de Seguridad Física", "Instalar cámaras CCTV y controles biométricos en la entrada del archivo central de contratos."),
    ("Depuración de Archivo Muerto", "Destruir documentación confidencial con antigüedad mayor a 10 años según normativa vigente."),
    ("Auditoría Externa de Sistemas", "Contratar firma especializada para realizar Ethical Hacking y Pentesting a la aplicación móvil."),
    ("Monitoreo de Transacciones Atípicas", "Afinar los umbrales del software de monitoreo transaccional para reducir falsos positivos."),
    ("Actualización de Antivirus Corporativo", "Migrar a una solución EDR (Endpoint Detection and Response) basada en inteligencia artificial.")
]

plans = ActionPlan.objects.all()

print("Actualizando planes de acción con ejemplos reales...")
for i, plan in enumerate(plans):
    # Pick a real plan based on index, loop if needed
    name, description = real_plans[i % len(real_plans)]
    plan.title = name
    plan.description = description
    plan.save()

print(f"{plans.count()} planes actualizados exitosamente.")
