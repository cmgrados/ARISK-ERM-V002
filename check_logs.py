import os
import django
import sys

# Add project root to sys.path
sys.path.append('c:/Users/VICTUS/Desktop/A.RISK ERM')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from utilities.models import BulkLoadLog

logs = BulkLoadLog.objects.filter(load_type='LIABILITY').order_by('-load_date')
for l in logs:
    print(f"File: {l.file_name}, Date: {l.load_date}, Status: {l.status}, Processed: {l.records_processed}, Dates: {l.cut_off_dates}")
