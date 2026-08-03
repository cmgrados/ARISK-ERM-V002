
import os, django, json
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.test import RequestFactory
from financial_planning.views import api_get_projected_balance_data
from django.contrib.auth import get_user_model
CustomUser = get_user_model()
from financial_planning.models import PlanFinanciero, SimulacionEscenario, ProyeccionMensual

plan = PlanFinanciero.objects.get(id=3)
scenario_name = 'BASE'
scenario_types = {
    'BASE': 'Tendencia',
    'OPT': 'Optimista',
    'PES': 'Pesimista'
}

sim_cartera = SimulacionEscenario.objects.filter(
    plan=plan, variable_id='cartera', tipo_escenario=scenario_types[scenario_name], agencia='Consolidado'
).first()

if sim_cartera:
    vals = list(ProyeccionMensual.objects.filter(escenario=sim_cartera).order_by('mes_proyeccion').values_list('valor_base', flat=True))
    print(f'Cartera {scenario_name}: {vals[:2]}')
else:
    print('SimulacionEscenario not found!')

