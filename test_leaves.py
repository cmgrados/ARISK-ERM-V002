import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from liquidity_risk.models import LiqBalanceDetail

qs = LiqBalanceDetail.objects.filter(
    period__year=2025,
    period__month=12,
    upload__status='SUCCESS'
).values('account_code', 'balance')

base_dict = {str(q['account_code']): float(q['balance']) for q in qs}

leaf_codes = [k for k in base_dict.keys() if k.startswith('14') and not any(other.startswith(k) and len(other) > len(k) for other in base_dict.keys())]
c_base_val = sum(base_dict[k] for k in leaf_codes)
print(f"Parent 14: {base_dict.get('14', 0)}")
print(f"Leaves sum: {c_base_val}")
