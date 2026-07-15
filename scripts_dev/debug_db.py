import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.credit_risk.models import CreditOperation
from django.db.models import Count, Sum

print("Total Operations:", CreditOperation.objects.count())

agencies = CreditOperation.objects.values('agency').annotate(count=Count('id'), total_bal=Sum('balance'))
for a in agencies:
    print(a)
