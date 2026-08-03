import sys
from financial_planning.models import *
for s in SimulacionEscenario.objects.filter(plan_id=1): print(s.variable_id)
