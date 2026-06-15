import os, django, datetime
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import Organization
from strategic_risk.models import StrategicPlan, Indicador, MetaPeriodo

def get_monthly_distribution(base, meta, months):
    # simple linear interpolation
    step = (meta - base) / months
    return [round(base + step * i, 2) for i in range(1, months + 1)]

def run():
    org = Organization.objects.first()
    plan = StrategicPlan.objects.order_by('-start_year').first()
    if not plan:
        print("No plan found.")
        return

    meses = [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]
    year = 2026

    # Delete existing MetaPeriodos for the plan
    MetaPeriodo.objects.filter(indicador__objetivo__perspectiva__plan=plan).delete()

    indicadores = Indicador.objects.filter(objetivo__perspectiva__plan=plan)

    for ind in indicadores:
        nombre = ind.nombre.lower()
        
        # Default numeric goals depending on indicator context
        if 'crecimiento de cartera' in nombre:
            linea_base = 10.0 # 10%
            meta_final = 18.0 # 18%
        elif 'morosidad' in nombre:
            linea_base = 8.0 # 8%
            meta_final = 5.0 # 5% (reduce)
        elif 'gastos operativos' in nombre:
            linea_base = 65.0
            meta_final = 55.0 # (reduce)
        elif 'socios nuevos' in nombre:
            linea_base = 100
            meta_final = 500 # qty
        elif 'satisfacción' in nombre:
            linea_base = 60.0
            meta_final = 85.0
        elif 'reclamos' in nombre:
            linea_base = 70.0
            meta_final = 95.0
        elif 'tiempo' in nombre and 'evaluación' in nombre:
            linea_base = 48.0 # hours
            meta_final = 24.0 # (reduce)
        elif 'desembolsos' in nombre:
            linea_base = 80.0
            meta_final = 98.0
        elif 'digitalización' in nombre:
            linea_base = 30.0
            meta_final = 75.0
        elif 'capacitación' in nombre:
            linea_base = 40.0
            meta_final = 100.0
        elif 'retención' in nombre:
            linea_base = 85.0
            meta_final = 95.0
        elif 'clima' in nombre:
            linea_base = 70.0
            meta_final = 90.0
        else:
            linea_base = 50.0
            meta_final = 80.0

        ind.linea_base = linea_base
        ind.meta_final = meta_final
        ind.save()

        # Generate partial goals
        monthly_goals = get_monthly_distribution(linea_base, meta_final, 12)
        
        for i, mes in enumerate(meses):
            periodo_str = f"{mes} {year}"
            MetaPeriodo.objects.create(
                organization=org,
                indicador=ind,
                periodo=periodo_str,
                meta_programada=monthly_goals[i]
            )
        
        print(f"Metas generadas para {ind.nombre}: LB={linea_base}, MF={meta_final}")

if __name__ == '__main__':
    run()
