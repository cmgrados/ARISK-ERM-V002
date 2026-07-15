import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.cache import cache
from financial_planning.models import FinancialPlan

cache.clear()

for plan in FinancialPlan.objects.all():
    hist_data = plan.historical_data or {}
    updated = False
    if 'portfolio_cache' in hist_data:
        del hist_data['portfolio_cache']
        updated = True
    if 'passive_cache' in hist_data:
        del hist_data['passive_cache']
        updated = True
    if updated:
        plan.historical_data = hist_data
        plan.save(update_fields=['historical_data'])
        
print("All caches cleared successfully.")
