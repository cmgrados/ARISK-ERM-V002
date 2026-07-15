import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from credit_risk.models import CreditOperation
from utilities.models import BulkLoadLog
from decimal import Decimal

ops = CreditOperation.objects.all()
updated = 0
for op in ops:
    expected_venc = op.balance if op.days_past_due > 30 else Decimal('0.0')
    if op.past_due_portfolio != expected_venc:
        op.past_due_portfolio = expected_venc
        op.save(update_fields=['past_due_portfolio'])
        updated += 1

print(f'Updated {updated} records for Mora (>30 dias)')
