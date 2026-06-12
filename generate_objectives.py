from strategic_risk.models import StrategicPlan, Perspectiva, ObjetivoEstrategico

def run():
    plan = StrategicPlan.objects.first()
    if not plan:
        print("No se encontró ningún Plan Estratégico.")
        return

    perspectivas = Perspectiva.objects.filter(plan=plan)
    if not perspectivas:
        print("No se encontraron perspectivas para el plan. Asegúrate de tener perspectivas creadas.")
        return

    # Delete existing test ones to avoid duplicates/mess
    # ObjetivoEstrategico.objects.filter(perspectiva__plan=plan).delete()

    objectives_data = {
        "Financiera": [
            {"nombre": "Aumentar los ingresos netos", "tipo": "Estratégico", "area": "Gerencia Financiera", "resp": "Gerente Financiero", "desc": "Incrementar las ventas en un 15% anual.", "pv": "Maximizar el valor para los accionistas mediante la optimización de recursos, asegurando la sostenibilidad financiera a largo plazo y manteniendo un crecimiento constante en los márgenes de rentabilidad."},
            {"nombre": "Reducir los costos operativos", "tipo": "Estratégico", "area": "Gerencia de Operaciones", "resp": "Gerente de Operaciones", "desc": "Optimizar el uso de recursos para disminuir los costos en un 10%.", "pv": "Maximizar el valor para los accionistas mediante la optimización de recursos, asegurando la sostenibilidad financiera a largo plazo y manteniendo un crecimiento constante en los márgenes de rentabilidad."},
            {"nombre": "Mejorar el margen de rentabilidad EBITDA", "tipo": "Estratégico", "area": "Gerencia Financiera", "resp": "Gerente Financiero", "desc": "Incrementar el margen de rentabilidad a más del 25%.", "pv": "Maximizar el valor para los accionistas mediante la optimización de recursos, asegurando la sostenibilidad financiera a largo plazo y manteniendo un crecimiento constante en los márgenes de rentabilidad."},
            {"nombre": "Diversificar las fuentes de ingresos institucionales", "tipo": "Estratégico", "area": "Gerencia Comercial", "resp": "Gerente Comercial", "desc": "Lanzar al menos 2 nuevos productos de crédito o ahorro.", "pv": "Maximizar el valor para los accionistas mediante la optimización de recursos, asegurando la sostenibilidad financiera a largo plazo y manteniendo un crecimiento constante en los márgenes de rentabilidad."}
        ],
        "Cliente": [
            {"nombre": "Mejorar la satisfacción general del socio/cliente", "tipo": "Estratégico", "area": "Atención al Cliente", "resp": "Jefe de Servicio", "desc": "Alcanzar un indicador Net Promoter Score (NPS) superior a 80 puntos.", "pv": "Proveer una experiencia de usuario excepcional que fidelice a nuestros clientes, ofreciendo soluciones ágiles, canales digitales de primer nivel y un servicio al cliente altamente resolutivo."},
            {"nombre": "Incrementar la tasa de retención de clientes", "tipo": "Estratégico", "area": "Marketing", "resp": "Gerente de Marketing", "desc": "Disminuir la tasa de abandono anual en un 5%.", "pv": "Proveer una experiencia de usuario excepcional que fidelice a nuestros clientes, ofreciendo soluciones ágiles, canales digitales de primer nivel y un servicio al cliente altamente resolutivo."},
            {"nombre": "Ampliar la cuota y penetración de mercado", "tipo": "Estratégico", "area": "Ventas", "resp": "Gerente de Ventas", "desc": "Captar un 10% adicional de participación en el mercado objetivo.", "pv": "Proveer una experiencia de usuario excepcional que fidelice a nuestros clientes, ofreciendo soluciones ágiles, canales digitales de primer nivel y un servicio al cliente altamente resolutivo."},
            {"nombre": "Ofrecer canales digitales más eficientes", "tipo": "Estratégico", "area": "Canales Digitales", "resp": "Jefe de Canales", "desc": "Aumentar el uso de la banca móvil en un 30%.", "pv": "Proveer una experiencia de usuario excepcional que fidelice a nuestros clientes, ofreciendo soluciones ágiles, canales digitales de primer nivel y un servicio al cliente altamente resolutivo."}
        ],
        "Procesos": [
            {"nombre": "Optimizar los tiempos de aprobación de crédito", "tipo": "Estratégico", "area": "Riesgos y Crédito", "resp": "Jefe de Riesgos", "desc": "Reducir el tiempo promedio de aprobación de crédito en un 20%.", "pv": "Implementar estándares de calidad de clase mundial en nuestras operaciones diarias, apalancándonos en la automatización y la mejora continua para reducir tiempos de ciclo y minimizar riesgos operativos."},
            {"nombre": "Mejorar el aseguramiento de la calidad", "tipo": "Operativo", "area": "Operaciones", "resp": "Jefe de Calidad", "desc": "Reducir la tasa de reprocesos a menos del 1%.", "pv": "Implementar estándares de calidad de clase mundial en nuestras operaciones diarias, apalancándonos en la automatización y la mejora continua para reducir tiempos de ciclo y minimizar riesgos operativos."},
            {"nombre": "Automatizar los procesos operativos clave", "tipo": "Estratégico", "area": "Tecnología (TI)", "resp": "Gerente de TI", "desc": "Implementar un nuevo Core Bancario para eficiencia.", "pv": "Implementar estándares de calidad de clase mundial en nuestras operaciones diarias, apalancándonos en la automatización y la mejora continua para reducir tiempos de ciclo y minimizar riesgos operativos."},
            {"nombre": "Fortalecer la gestión integral de riesgos", "tipo": "Estratégico", "area": "Riesgos", "resp": "Gerente de Riesgos", "desc": "Actualizar y digitalizar la matriz de riesgos institucionales.", "pv": "Implementar estándares de calidad de clase mundial en nuestras operaciones diarias, apalancándonos en la automatización y la mejora continua para reducir tiempos de ciclo y minimizar riesgos operativos."}
        ],
        "Aprendizaje": [
            {"nombre": "Cumplir el plan de capacitación del personal", "tipo": "Operativo", "area": "Recursos Humanos", "resp": "Jefe de RRHH", "desc": "Ejecutar el 100% del plan de capacitación programado en el año.", "pv": "Fomentar una cultura organizacional de alto desempeño, invirtiendo en la capacitación continua del talento humano, promoviendo la innovación y asegurando un clima laboral óptimo."},
            {"nombre": "Mejorar el clima laboral e índice de satisfacción", "tipo": "Estratégico", "area": "Recursos Humanos", "resp": "Jefe de RRHH", "desc": "Lograr un 85% o más en la encuesta anual de clima organizacional.", "pv": "Fomentar una cultura organizacional de alto desempeño, invirtiendo en la capacitación continua del talento humano, promoviendo la innovación y asegurando un clima laboral óptimo."},
            {"nombre": "Retener y desarrollar al talento clave", "tipo": "Estratégico", "area": "Recursos Humanos", "resp": "Jefe de RRHH", "desc": "Reducir la rotación de personal clave a menos del 5%.", "pv": "Fomentar una cultura organizacional de alto desempeño, invirtiendo en la capacitación continua del talento humano, promoviendo la innovación y asegurando un clima laboral óptimo."},
            {"nombre": "Implementar un sistema de gestión de desempeño", "tipo": "Estratégico", "area": "Gerencia General", "resp": "Gerente General", "desc": "Evaluar al 100% del personal bajo KPIs estandarizados.", "pv": "Fomentar una cultura organizacional de alto desempeño, invirtiendo en la capacitación continua del talento humano, promoviendo la innovación y asegurando un clima laboral óptimo."}
        ]
    }

    def clean_name(name):
        name_lower = name.lower()
        if "financiera" in name_lower: return "Financiera"
        if "cliente" in name_lower or "soci" in name_lower: return "Cliente"
        if "procesos" in name_lower: return "Procesos"
        if "aprendizaje" in name_lower or "crecimiento" in name_lower: return "Aprendizaje"
        return "Financiera"

    for p in perspectivas:
        key = clean_name(p.nombre)
        objs = objectives_data.get(key, objectives_data["Financiera"])
        print(f"Generando para la perspectiva: {p.nombre}...")
        for i, data in enumerate(objs):
            codigo = f"OBJ-P{p.id}-{i+1}"
            
            full_desc = f"{data['desc']}\n\nPropuesta de Valor:\n{data.get('pv', '')}"
            
            obj, created = ObjetivoEstrategico.objects.get_or_create(
                perspectiva=p,
                nombre=data["nombre"],
                organization=p.organization,
                defaults={
                    "codigo": codigo,
                    "descripcion": full_desc,
                    "tipo_objetivo": data["tipo"],
                    "area_responsable": data["area"],
                    "responsable": data["resp"]
                }
            )
            if created:
                print(f" -> Creado: {obj.nombre}")
            else:
                print(f" -> Ya existía: {obj.nombre}")

if __name__ == "__main__":
    run()
