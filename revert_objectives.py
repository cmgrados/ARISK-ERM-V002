import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from strategic_risk.models import StrategicPlan, ObjetivoEstrategico

def run():
    plan = StrategicPlan.objects.order_by('-start_year').first()
    if not plan:
        print("No plan found")
        return

    # List of tuples (codigo, new_desc) matching the user screenshot
    updates = [
        ("OBJ-FIN-01", "Aumentar los ingresos netos"),
        ("OBJ-FIN-02", "Reducir los costos operativos"),
        ("OBJ-FIN-03", "Mejorar el margen de rentabilidad EBITDA"),
        ("OBJ-FIN-04", "Diversificar las fuentes de ingresos institucionales"),

        ("OBJ-CLI-01", "Mejorar la satisfacción general del socio/cliente"),
        ("OBJ-CLI-02", "Incrementar la tasa de retención de clientes"),
        ("OBJ-CLI-03", "Ampliar la cuota y penetración de mercado"),
        ("OBJ-CLI-04", "Ofrecer canales digitales más eficientes"),

        ("OBJ-PRO-01", "Optimizar los tiempos de aprobación de crédito"),
        ("OBJ-PRO-02", "Mejorar el aseguramiento de la calidad"),
        ("OBJ-PRO-03", "Automatizar los procesos operativos clave"),
        ("OBJ-PRO-04", "Fortalecer la gestión integral de riesgos"),

        ("OBJ-APR-01", "Cumplir el plan de capacitación del personal"),
        ("OBJ-APR-02", "Mejorar el clima laboral e índice de satisfacción"),
        ("OBJ-APR-03", "Retener y desarrollar al talento clave"),
        ("OBJ-APR-04", "Implementar un sistema de gestión de desempeño")
    ]

    objs = ObjetivoEstrategico.objects.filter(perspectiva__plan=plan)
    count = 0
    for obj in objs:
        for code, new_desc in updates:
            if obj.codigo == code:
                obj.descripcion = new_desc
                obj.save()
                count += 1
                break
            
    print(f"Se revirtieron y actualizaron {count} Objetivos Estratégicos.")

if __name__ == '__main__':
    run()
