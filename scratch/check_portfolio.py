from liquidity_risk.models import LiqBalanceDetail
from django.db.models import Sum

qs = LiqBalanceDetail.objects.filter(account_code__startswith='14').values('account_code', 'account_name').annotate(total=Sum('balance')).order_by('account_code')
for x in qs:
    print(f"{x['account_code']}: {x['account_name']} -> {x['total']}")
