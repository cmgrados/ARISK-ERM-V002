from strategic_risk.models import ObjetivoEstrategico

def run():
    print("Actualizando propuesta de valor para objetivos existentes...")
    
    # Mapping for proposals based on perspectives/areas
    proposals = {
        "Financiera": "Maximizar el valor para los accionistas mediante la optimización de recursos, asegurando la sostenibilidad financiera a largo plazo y manteniendo un crecimiento constante en los márgenes de rentabilidad.",
        "Cliente": "Proveer una experiencia de usuario excepcional que fidelice a nuestros clientes, ofreciendo soluciones ágiles, canales digitales de primer nivel y un servicio al cliente altamente resolutivo.",
        "Procesos": "Implementar estándares de calidad de clase mundial en nuestras operaciones diarias, apalancándonos en la automatización y la mejora continua para reducir tiempos de ciclo y minimizar riesgos operativos.",
        "Aprendizaje": "Fomentar una cultura organizacional de alto desempeño, invirtiendo en la capacitación continua del talento humano, promoviendo la innovación y asegurando un clima laboral óptimo."
    }
    
    objectives = ObjetivoEstrategico.objects.all()
    count = 0
    for obj in objectives:
        if not obj.descripcion or 'Propuesta de Valor:' not in obj.descripcion:
            # Determine which proposal to use based on perspective name
            pers_name = obj.perspectiva.nombre.lower() if obj.perspectiva else ""
            
            if "financiera" in pers_name:
                pv = proposals["Financiera"]
            elif "cliente" in pers_name or "soci" in pers_name:
                pv = proposals["Cliente"]
            elif "procesos" in pers_name:
                pv = proposals["Procesos"]
            else:
                pv = proposals["Aprendizaje"]
                
            # If description already has text, append the propuesta de valor
            # This matches the way we parse it in controls.html: desc.split('\n\nPropuesta de Valor:\n')
            current_desc = obj.descripcion or ""
            if current_desc:
                new_desc = f"{current_desc}\n\nPropuesta de Valor:\n{pv}"
            else:
                new_desc = f"Propuesta de Valor:\n{pv}"
                
            obj.descripcion = new_desc
            obj.save()
            count += 1
            
    print(f"Se actualizaron {count} objetivos con su respectiva propuesta de valor.")
