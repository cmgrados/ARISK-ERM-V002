import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from utilities.models import BulkLoadLog

print("--- BulkLoadLog Data ---")
for log in BulkLoadLog.objects.all():
    print(f"ID: {log.id}, File: {log.file_name}, Cut-off dates: '{log.cut_off_dates}'")
