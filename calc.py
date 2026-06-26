import os, sys, django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from liquidity_risk.models import LiqLiabilityDetail
from django.db.models import Sum
p = LiqLiabilityDetail.objects.filter(period__year=2025, period__month=12)
print('DPF ME:', p.filter(product__icontains='ME', funding_type='PLAZO').aggregate(s=Sum('amount'))['s'])
print('AHORRO ME:', p.filter(product__icontains='DOLARES', funding_type='AHORRO').aggregate(s=Sum('amount'))['s'])
print('DPF MN:', p.filter(funding_type='PLAZO').exclude(product__icontains='ME').aggregate(s=Sum('amount'))['s'])
print('AHORRO MN:', p.filter(funding_type='AHORRO').exclude(product__icontains='DOLARES').aggregate(s=Sum('amount'))['s'])
