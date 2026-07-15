import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.apps import apps
Factor = apps.get_model('goals', 'Factor')
for f in Factor.objects.all():
    print({k: v for k, v in f.__dict__.items() if not k.startswith('_')})
