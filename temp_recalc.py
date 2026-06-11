import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.credit_risk.utils import generate_missing_metrics

# Recalculate metrics for everything to fix the lost SBS classifications issue
print("Recalculating metrics...")
updated = generate_missing_metrics(force_recalculate=True)
print(f"Done! Updated/Created {updated} metrics.")
