import sys
from financial_planning.models import *
sim=SimulacionEscenario.objects.filter(plan_id=1, variable_id='cartera').first()
print(sim)
projs=ProyeccionMensual.objects.filter(escenario=sim).order_by('mes_proyeccion')[:3]
print([p.valor_base for p in projs])
