import os
import django
import sys

# Add project root to sys.path
sys.path.append(r'c:\Users\VICTUS\Desktop\A.RISK ERM')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from liquidity_risk.models import LiqTimeBand

bands = LiqTimeBand.objects.all().order_by('order')
for b in bands:
    print(f"Band: {b.name}, Order: {b.order}, Start: {b.start_days}, End: {b.end_days}")
