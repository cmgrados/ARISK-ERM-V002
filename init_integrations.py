import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.catalogs.models import SystemIntegration

SystemIntegration.objects.get_or_create(provider='gemini')
SystemIntegration.objects.get_or_create(provider='google_drive')
SystemIntegration.objects.get_or_create(provider='google_calendar')

print("Integrations initialized.")
