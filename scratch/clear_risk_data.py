import os
import sys
import django

# Add current directory to path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.apps import apps
from django.db import transaction

# Apps that contain transactional/test data
DATA_APPS = [
    'credit_risk',
    'compliance_risk',
    'operational_risk',
    'market_risk',
    'plaft_risk',
    'strategic_risk',
    'liquidity_risk',
    'reputational_risk',
    'risks',
    'incidents',
    'indicators',
    'action_plans',
    'audit',
    'attachments'
]

# Structural apps (don't clear unless requested)
STRUCTURAL_APPS = ['users', 'catalogs', 'core', 'dashboards']

print("--- Iniciando limpieza de base de datos de prueba ---")

try:
    with transaction.atomic():
        for app_label in DATA_APPS:
            try:
                app_config = apps.get_app_config(app_label)
                for model in app_config.get_models():
                    count = model.objects.all().count()
                    if count > 0:
                        print(f"Eliminando {count} registros de {app_label}.{model.__name__}...")
                        model.objects.all().delete()
            except LookupError:
                # App might not be installed or named differently
                pass
    print("--- Limpieza completada con éxito ---")
except Exception as e:
    print(f"ERROR durante la limpieza: {e}")
