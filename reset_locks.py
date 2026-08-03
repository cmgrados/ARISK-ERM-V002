import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from financial_planning.models import ProjectedBalanceAdjustment
count = 0
for a in ProjectedBalanceAdjustment.objects.all():
  if isinstance(a.adjustments, dict) and 'is_fixed' in a.adjustments:
    a.adjustments['is_fixed'] = False
    a.save()
    count += 1
print(f'Reset {count} locks.')
