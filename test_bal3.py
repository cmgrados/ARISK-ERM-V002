import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from financial_planning.models import ProyeccionMensual
print(list(ProyeccionMensual.objects.filter(plan_id=3, simulacion__escenario='BASE').values_list('cartera_vigente', flat=True).order_by('mes')))
