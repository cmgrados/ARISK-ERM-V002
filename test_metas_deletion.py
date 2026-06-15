import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from strategic_risk.models import Indicador, MetaPeriodo
from users.models import Organization

ind = Indicador.objects.first()
org = Organization.objects.first()

print("Original count:", MetaPeriodo.objects.filter(indicador=ind).count())

# Suppose we pass new periods
new_periodos = ["Febrero 2026", "Marzo 2026"]
MetaPeriodo.objects.filter(indicador=ind).exclude(periodo__in=new_periodos).delete()

print("New count:", MetaPeriodo.objects.filter(indicador=ind).count())
