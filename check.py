import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from apps.financial_planning.models import LiqBalanceDetail

for row in LiqBalanceDetail.objects.filter(account__icontains='vendid').values_list('account', flat=True).distinct():
    print(row)

for row in LiqBalanceDetail.objects.filter(account__startswith='140').values_list('account', flat=True).distinct():
    print(row)
