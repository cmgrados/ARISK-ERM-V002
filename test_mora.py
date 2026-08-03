import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from apps.financial_planning.models import SimulacionEscenario, ProyeccionMensual
sim = SimulacionEscenario.objects.filter(variable_id='mora_soles').first()
if sim:
    print([p.valor_base for p in ProyeccionMensual.objects.filter(escenario=sim).order_by('mes_proyeccion')[:12]])
else:
    print('No sim')
