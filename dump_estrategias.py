import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from strategic_risk.models import Estrategia

for e in Estrategia.objects.all():
    print(f'{e.id} | {e.tipo} | {e.descripcion}')
