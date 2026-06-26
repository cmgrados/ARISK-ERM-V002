import os, sys, django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from liquidity_risk.models import LiqLiabilityDetail
from django.db.models import Sum
res = LiqLiabilityDetail.objects.filter(period__year=2025, period__month=12).values('funding_type', 'product').annotate(s=Sum('amount'))
for r in res:
    print(r['funding_type'], r['product'], r['s'])
