import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from strategic_risk.models import Estrategia, PortafolioPOA
from users.models import Organization

org = Organization.objects.first()

# Map of Strategy ID to a list of Projects (nombre, descripcion, anio, presupuesto, lider)
project_map = {
    25: [
        ("Campaña publicitaria 'Confianza 50 Años'", "Diseño y difusión de campaña en medios tradicionales y digitales.", 2026, 12000, "Marketing"),
        ("Programa de captación en bases militares", "Visitas presenciales y stands interactivos en bases del norte y centro.", 2026, 8000, "Gerencia Comercial")
    ],
    26: [
        ("Diseño de Crédito Consumo Ágil", "Estructuración de un nuevo producto de crédito de consumo con desembolso en 24h.", 2026, 5000, "Gerencia de Negocios"),
        ("Prueba piloto de nuevo crédito", "Lanzamiento controlado del crédito de consumo ágil en 3 agencias principales.", 2027, 4500, "Operaciones")
    ],
    27: [
        ("Mapeo y firma de convenios institucionales", "Identificar y firmar 10 convenios con empresas de retail y salud.", 2026, 2000, "Relaciones Institucionales"),
        ("Integración tecnológica de servicios externos", "Conectar los sistemas de la cooperativa con los nuevos aliados estratégicos.", 2027, 15000, "TI")
    ],
    28: [
        ("Desarrollo de plataforma 'EducaAhorro'", "Creación de módulo e-learning sobre educación financiera para socios.", 2026, 10000, "Educación Cooperativa"),
        ("Talleres presenciales de finanzas", "Ejecución de 20 talleres anuales en colegios y universidades aliadas.", 2026, 6000, "Marketing")
    ],
    29: [
        ("Apertura de 3 Agentes Corresponsales", "Selección e implementación de agentes en zonas rurales clave.", 2026, 15000, "Operaciones"),
        ("Adquisición de tecnología móvil para asesores", "Equipamiento con tablets y software de campo para promotores.", 2027, 25000, "TI")
    ],
    30: [
        ("Campaña de endomarketing cooperativo", "Reforzar los valores cooperativos en el personal para mejorar la atención.", 2026, 3000, "Recursos Humanos"),
        ("Renovación de identidad visual", "Actualización de la marca y señalética en todas las agencias.", 2027, 20000, "Marketing")
    ],
    31: [
        ("Plataforma de créditos digitales", "Desarrollo de portal web para pre-aprobación de créditos.", 2026, 35000, "TI"),
        ("Integración con bases de datos del Estado", "Conexión API con RENIEC y otras entidades para validación inmediata.", 2026, 12000, "Riesgos")
    ],
    32: [
        ("Actualización Core Bancario", "Migración a la nueva versión del core para soportar banca móvil.", 2026, 80000, "TI"),
        ("Lanzamiento de Banca Web 3.0", "Rediseño completo de la experiencia de usuario en la web transaccional.", 2027, 25000, "Canales Digitales")
    ],
    33: [
        ("Implementación de Cloud Computing", "Migración de servidores no críticos a AWS/Azure para reducir costos.", 2026, 30000, "TI"),
        ("Contrato de soporte tecnológico especializado", "Tercerización del soporte nivel 2 y 3 con empresa partner.", 2026, 18000, "Gerencia General")
    ],
    34: [
        ("Campaña 'Ahorro Programado Plus'", "Nuevo producto de ahorro con tasas escalonadas y beneficios adicionales.", 2026, 5000, "Gerencia de Negocios"),
        ("Feria del Ahorro 2027", "Evento masivo para captación de depósitos a plazo fijo.", 2027, 10000, "Marketing")
    ],
    35: [
        ("Consultoría en reingeniería de procesos", "Contratación de firma externa para mapear y optimizar flujos crediticios.", 2026, 22000, "Organización y Métodos"),
        ("Automatización de flujo de aprobaciones", "Implementación de herramienta BPM para reducir uso de papel.", 2027, 14000, "TI")
    ],
    36: [
        ("App Móvil Transaccional", "Desarrollo y lanzamiento de aplicación móvil para Android y iOS.", 2026, 45000, "Canales Digitales"),
        ("Programa de adopción digital", "Campañas y promotores en agencias para enseñar a usar la App.", 2027, 8000, "Marketing")
    ],
    37: [
        ("Creación del Laboratorio de Innovación", "Espacio físico y equipo dedicado a la creación de productos ágiles.", 2026, 20000, "Gerencia General"),
        ("Hackathon Financiera Interna", "Evento interno para generación de ideas innovadoras con el personal.", 2026, 4000, "Recursos Humanos")
    ],
    38: [
        ("Estudio de mercado para nuevos segmentos", "Investigación sobre necesidades financieras de microempresarios y emprendedores.", 2026, 6000, "Inteligencia de Negocios"),
        ("Lanzamiento de Microcrédito Emprendedor", "Nuevo producto enfocado en un perfil ocupacional diferente al militar.", 2027, 12000, "Gerencia Comercial")
    ],
    39: [
        ("Programa de Lealtad 'Socio VIP'", "Beneficios exclusivos y tasas preferenciales para socios antiguos.", 2026, 15000, "Gerencia de Negocios"),
        ("Call Center de Retención", "Equipo dedicado a contactar socios que solicitan retiros importantes.", 2026, 10000, "Atención al Socio")
    ],
    40: [
        ("Implementación de Motor de Riesgos", "Adopción de software estadístico para scoring crediticio automatizado.", 2026, 40000, "Riesgos"),
        ("Capacitación en técnicas de cobranza", "Taller avanzado para oficiales de recuperación de cartera.", 2026, 3000, "Recursos Humanos")
    ],
    41: [
        ("Plan de eficiencia energética y operativa", "Reducción de gastos en servicios básicos y papelería a nivel nacional.", 2026, 2000, "Administración"),
        ("Renegociación de contratos a largo plazo", "Evaluación y ajuste de contratos con proveedores principales.", 2026, 0, "Logística")
    ],
    42: [
        ("Programa 'Agencia Modelo'", "Remodelación de agencia piloto enfocada en servicio hiper-personalizado.", 2026, 35000, "Gerencia Comercial"),
        ("Integración de CRM Corporativo", "Plataforma 360 grados para conocer el historial de interacciones del socio.", 2027, 28000, "TI")
    ],
    43: [
        ("Onboarding 100% Digital", "Proceso de afiliación de nuevos socios sin necesidad de pisar agencia.", 2026, 50000, "Canales Digitales"),
        ("Campaña Digital 'Tu Coop en tu Bolsillo'", "Marketing digital enfocado en el segmento menor de 35 años.", 2026, 15000, "Marketing")
    ],
    44: [
        ("Comité de Alianzas Estratégicas", "Formación de equipo evaluador de fusiones o integraciones sistémicas.", 2026, 5000, "Directorio"),
        ("Implementación de software RegTech", "Herramienta tecnológica para facilitar reportes regulatorios a la SBS.", 2027, 25000, "Cumplimiento")
    ],
    45: [
        ("Emisión de bonos o deuda subordinada", "Estructuración legal y financiera para buscar fondeo mayorista.", 2026, 30000, "Finanzas"),
        ("Diversificación de inversiones", "Optimización del portafolio de liquidez para maximizar retornos seguros.", 2026, 5000, "Finanzas")
    ],
    46: [
        ("Tercerización de impresión y valijas", "Contratación de proveedor logístico para reducir carga operativa.", 2026, 8000, "Operaciones"),
        ("Chatbot de Atención al Socio", "Implementación de IA para resolver consultas frecuentes 24/7.", 2027, 12000, "Canales Digitales")
    ],
    47: [
        ("Campaña 'Ponte al Día'", "Condonación parcial de moras e intereses para liquidaciones al contado.", 2026, 10000, "Cobranzas"),
        ("Contratación de estudio jurídico de cobranzas", "Gestión de cartera en pérdida mayor a 120 días.", 2026, 0, "Legal")
    ],
    48: [
        ("Actualización de Estatutos", "Revisión legal integral para adaptar la gobernanza a nuevas normativas.", 2026, 15000, "Legal"),
        ("Sistema de Gestión de Sesiones de Directorio", "Portal seguro para votaciones y actas digitales.", 2027, 8000, "TI")
    ]
}

# Clean existing projects if any, to avoid duplicates on re-runs (optional, but good for clean demo)
# PortafolioPOA.objects.all().delete()

for estrategia_id, projects in project_map.items():
    try:
        e = Estrategia.objects.get(id=estrategia_id)
        
        # Skip if strategy already has POAs
        if PortafolioPOA.objects.filter(estrategia=e).exists():
            print(f"Skipping Estrategia {estrategia_id}: Already has projects.")
            continue
            
        for p in projects:
            nombre, desc, anio, pres, lider = p
            PortafolioPOA.objects.create(
                organization=org,
                estrategia=e,
                anio=anio,
                nombre_proyecto=nombre,
                descripcion=desc,
                presupuesto=pres,
                lider_proyecto=lider
            )
        print(f"Created {len(projects)} projects for Estrategia {estrategia_id}")
    except Estrategia.DoesNotExist:
        print(f"Estrategia {estrategia_id} not found.")
