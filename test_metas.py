import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.strategic_risk.models import Indicador, MetaPeriodo

print("Indicadores:")
for i in Indicador.all_objects.all():
    print(f"ID: {i.id}, Nombre: {i.nombre}, Org: {i.organization}")

print("\nMetas:")
for m in MetaPeriodo.all_objects.all():
    print(f"Ind ID: {m.indicador.id}, Periodo: {m.periodo}, Prog: {m.meta_programada}")
