import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from credit_risk.models import CreditOperation
from credit_risk.utils import generate_missing_metrics
from django.db.models import Max

def run():
    print("Generating missing metrics...")
    cut_off_dates = CreditOperation.objects.values_list('load_date', flat=True).distinct()
    for d in cut_off_dates:
        print(f"Generating for {d}...")
        created = generate_missing_metrics(d)
        print(f"Generated {created} metrics for {d}")

if __name__ == '__main__':
    run()
