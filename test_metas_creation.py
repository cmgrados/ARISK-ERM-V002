import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from strategic_risk.models import Indicador, MetaPeriodo
from users.models import Organization

ind = Indicador.objects.first()
org = Organization.objects.first()
print(f"Using Indicador: {ind.id} - {ind.nombre}")

try:
    meta_obj, created = MetaPeriodo.objects.update_or_create(
        indicador=ind,
        periodo="Enero 2026",
        defaults={
            'meta_programada': 15.5,
            'organization': org
        }
    )
    print(f"Success! Created: {created}, Meta: {meta_obj.meta_programada}")
except Exception as e:
    print(f"Error: {e}")

