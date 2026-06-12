import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.strategic_risk.models import ObjetivoEstrategico
from django.template.defaultfilters import escapejs

for obj in ObjetivoEstrategico.objects.all():
    print(f'ID: {obj.id}')
    try:
        s = f"onclick=\"editObjective({obj.id}, '{obj.perspectiva.id}', '{escapejs(obj.tipo_objetivo)}', '{escapejs(obj.nombre)}', '{escapejs(obj.descripcion)}', '{escapejs(obj.area_responsable)}', '{escapejs(obj.responsable)}')\""
        print(s)
    except Exception as e:
        print(f'ERROR: {e}')
