import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.apps import apps
for model in apps.get_models():
    if model._meta.app_label == 'goals':
        print(model.__name__)
