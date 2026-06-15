import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from strategic_risk.models import StrategicPlan, ObjetivoEstrategico, CorporatePhilosophy

def run():
    plan = StrategicPlan.objects.order_by('-start_year').first()
    if not plan:
        print("No plan found")
        return

    # Create or update Corporate Philosophy for the Coop
    filo, created = CorporatePhilosophy.objects.get_or_create(plan=plan)
    filo.mission = "Brindar soluciones financieras ágiles, seguras y competitivas que mejoren la calidad de vida de nuestros socios y la comunidad, promoviendo los principios del cooperativismo."
    filo.vision = "Ser la cooperativa de ahorro y crédito líder a nivel nacional, reconocida por nuestra solidez financiera, innovación tecnológica y excelente calidad de servicio al socio."
    filo.values = "Integridad, Solidaridad, Transparencia, Compromiso, Excelencia."
    filo.save()

    # Dictionary mapping old codes to new cooperative-focused descriptions
    updates = {
        "OBJ-FIN-01": "Incrementar la captación de ahorros y depósitos a plazo fijo.",
        "OBJ-FIN-02": "Optimizar los costos operativos manteniendo la calidad del servicio.",
        "OBJ-FIN-03": "Maximizar la rentabilidad de la cartera de crédito y reducir morosidad.",
        "OBJ-FIN-04": "Desarrollar nuevos productos financieros adaptados a las necesidades de los socios.",
        "OBJ-CLI-01": "Aumentar la satisfacción general del socio y promover una excelente experiencia.",
        "OBJ-CLI-02": "Fidelizar a la base de socios activos y reducir la desafiliación.",
        "OBJ-CLI-03": "Ampliar la cobertura y penetración de la cooperativa en la comunidad.",
        "OBJ-CLI-04": "Fomentar la adopción masiva de canales digitales y banca móvil.",
        "OBJ-PRO-01": "Optimizar y reducir el tiempo de evaluación y aprobación de créditos.",
        "OBJ-PRO-02": "Asegurar la calidad y precisión en los procesos operativos en agencias.",
        "OBJ-PRO-03": "Modernizar el Core Financiero y automatizar procesos clave.",
        "OBJ-PRO-04": "Fortalecer la gestión integral de riesgos, cumplimiento y lavado de activos.",
        "OBJ-APR-01": "Capacitar continuamente al personal en principios financieros y servicio cooperativo.",
        "OBJ-APR-02": "Mejorar el clima laboral para promover una cultura de alto desempeño.",
        "OBJ-APR-03": "Retener el talento clave y desarrollar planes de carrera institucionales.",
        "OBJ-APR-04": "Implementar un sistema de gestión del desempeño basado en valores cooperativos."
    }

    objs = ObjetivoEstrategico.objects.filter(perspectiva__plan=plan)
    for obj in objs:
        if obj.codigo in updates:
            # We also strip the "Propuesta de Valor" if it was appended so it looks clean in the UI
            obj.descripcion = updates[obj.codigo]
            obj.save()
            
    print("Filosofía corporativa (Misión/Visión) y Objetivos Estratégicos actualizados para Cooperativa.")

if __name__ == '__main__':
    run()
