import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.apps import apps
Factor = apps.get_model('goals', 'Factor')

f1 = Factor.objects.get(id=1)
f1.weight = Decimal('60.00')
f1.save()

f2 = Factor.objects.get(id=2)
f2.weight = Decimal('5.00')
f2.save()

f3 = Factor.objects.get(id=3)
f3.name = 'MORA COSECHA'
f3.description = 'MORA COSECHA'
f3.weight = Decimal('35.00')
f3.save()
print('Actualizado correctamente.')
