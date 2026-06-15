from strategic_risk.models import ObjetivoEstrategico, Indicador, StrategicPlan, AreaResponsable

def run():
    plan = StrategicPlan.objects.order_by('-start_year').first()
    if not plan:
        print('No plan found')
        return

    # Delete existing indicators for the plan
    Indicador.objects.filter(objetivo__perspectiva__plan=plan).delete()

    # Define indicators for each perspective (tailored to cooperative needs)
    coop_indicators = {
        'FINANCIERA': [
            {
                'nombre': 'Crecimiento de Cartera de Crédito',
                'formula': '((Cartera N - Cartera N-1)/Cartera N-1)*100',
                'unidad_medida': 'Porcentaje',
                'responsable': 'Gerencia de Negocios',
                'tipo_objetivo': 'ESTRATEGICO',
                'medio_verificacion': 'Estados Financieros / Balance',
            },
            {
                'nombre': 'Índice de Morosidad',
                'formula': '(Cartera Atrasada / Cartera Total)*100',
                'unidad_medida': 'Porcentaje',
                'responsable': 'Área de Riesgos',
                'tipo_objetivo': 'ESTRATEGICO',
                'medio_verificacion': 'Reporte de Riesgos / Sistema Core',
            },
            {
                'nombre': 'Eficiencia en Gastos Operativos',
                'formula': '(Gastos Operativos / Ingresos Financieros)*100',
                'unidad_medida': 'Porcentaje',
                'responsable': 'Gerencia de Administración',
                'tipo_objetivo': 'OPERATIVO',
                'medio_verificacion': 'Estados de Resultados',
            }
        ],
        'SOCIO/CLIENTE': [
            {
                'nombre': 'Crecimiento de Socios Nuevos',
                'formula': 'Nuevos Socios - Socios Retirados',
                'unidad_medida': 'Cantidad',
                'responsable': 'Área de Negocios',
                'tipo_objetivo': 'TACTICO',
                'medio_verificacion': 'Reporte de Afiliaciones',
            },
            {
                'nombre': 'Nivel de Satisfacción del Socio (NPS)',
                'formula': '% Promotores - % Detractores',
                'unidad_medida': 'Porcentaje',
                'responsable': 'Atención al Socio',
                'tipo_objetivo': 'ESTRATEGICO',
                'medio_verificacion': 'Encuestas de Satisfacción',
            },
            {
                'nombre': 'Reclamos Atendidos en Plazo SLA',
                'formula': '(Reclamos en SLA / Total de Reclamos) * 100',
                'unidad_medida': 'Porcentaje',
                'responsable': 'Atención al Socio',
                'tipo_objetivo': 'OPERATIVO',
                'medio_verificacion': 'Libro de Reclamaciones / Sistema de Atención',
            }
        ],
        'PROCESOS INTERNOS': [
            {
                'nombre': 'Tiempo de Evaluación de Créditos',
                'formula': 'Sumatoria de horas de proceso / Total créditos desembolsados',
                'unidad_medida': 'Horas',
                'responsable': 'Área de Créditos',
                'tipo_objetivo': 'OPERATIVO',
                'medio_verificacion': 'Reporte de Tiempos del Core',
            },
            {
                'nombre': 'Eficiencia en Desembolsos',
                'formula': '(Créditos desembolsados / Solicitudes recibidas) * 100',
                'unidad_medida': 'Porcentaje',
                'responsable': 'Área de Operaciones',
                'tipo_objetivo': 'OPERATIVO',
                'medio_verificacion': 'Reporte de Operaciones',
            },
            {
                'nombre': 'Digitalización de Procesos Internos',
                'formula': '(Procesos automatizados / Total de procesos clave) * 100',
                'unidad_medida': 'Porcentaje',
                'responsable': 'Área de Sistemas',
                'tipo_objetivo': 'ESTRATEGICO',
                'medio_verificacion': 'Informes de TI / Proyectos',
            }
        ],
        'CRECIMIENTO Y APRENDIZAJE': [
            {
                'nombre': 'Cumplimiento Plan de Capacitación',
                'formula': '(Horas ejecutadas / Horas programadas) * 100',
                'unidad_medida': 'Porcentaje',
                'responsable': 'Recursos Humanos',
                'tipo_objetivo': 'TACTICO',
                'medio_verificacion': 'Registros de Capacitación / RRHH',
            },
            {
                'nombre': 'Retención de Personal Clave',
                'formula': '(Colaboradores clave retenidos / Total de colaboradores clave) * 100',
                'unidad_medida': 'Porcentaje',
                'responsable': 'Recursos Humanos',
                'tipo_objetivo': 'ESTRATEGICO',
                'medio_verificacion': 'Reportes de Rotación RRHH',
            },
            {
                'nombre': 'Mejora en Clima Laboral',
                'formula': 'Puntuación Promedio (Escala 1 al 100)',
                'unidad_medida': 'Puntos',
                'responsable': 'Recursos Humanos',
                'tipo_objetivo': 'TACTICO',
                'medio_verificacion': 'Encuestas de Clima Laboral',
            }
        ]
    }

    from users.models import Organization
    import datetime
    org = Organization.objects.first()

    objetivos = ObjetivoEstrategico.objects.filter(perspectiva__plan=plan)
    for obj in objetivos:
        perspectiva_nombre = obj.perspectiva.nombre.upper()
        # Find matching indicator templates based on perspective
        templates = None
        if 'FINANCIERA' in perspectiva_nombre:
            templates = coop_indicators['FINANCIERA']
        elif 'CLIENTE' in perspectiva_nombre or 'SOCIO' in perspectiva_nombre:
            templates = coop_indicators['SOCIO/CLIENTE']
        elif 'PROCESO' in perspectiva_nombre:
            templates = coop_indicators['PROCESOS INTERNOS']
        elif 'CRECIMIENTO' in perspectiva_nombre or 'APRENDIZAJE' in perspectiva_nombre:
            templates = coop_indicators['CRECIMIENTO Y APRENDIZAJE']
        else:
            templates = coop_indicators['FINANCIERA']  # fallback
            
        for i, t in enumerate(templates):
            Indicador.objects.create(
                objetivo=obj,
                organization=org,
                nombre=f"Ind {i+1}: {t['nombre']} - {obj.nombre[:50]}",
                formula=t['formula'],
                unidad_medida=t['unidad_medida'],
                frecuencia_medicion='MENSUAL',
                responsable=t['responsable'],
                peso=33.33,
                tipo_objetivo=t.get('tipo_objetivo', 'ESTRATEGICO'),
                medio_verificacion=t.get('medio_verificacion', 'Reportes Internos'),
                fecha_inicio=datetime.date(2026, 1, 1),
                fecha_fin=datetime.date(2026, 12, 31)
            )
            print(f"Created Indicator for {obj.nombre}: {t['nombre']}")
    
run()
