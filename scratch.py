import os, django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings'); django.setup(); from liquidity_risk.models import LiqBalanceDetail; qs = LiqBalanceDetail.objects.filter(period__year=2025, period__month=12, upload__status='SUCCESS').order_by('-upload_id'); uid = qs.values_list('upload_id', flat=True).first(); rows = qs.filter(upload_id=uid, account_code__startswith='1').values_list('account_code', 'balance'); all_codes = [r[0] for r in rows]; leaves = []; 
for c, b in rows:
  is_leaf = not any(other.startswith(c) and len(other) > len(c) for other in all_codes)
  leaves.append((c, float(b), is_leaf));
leaves.sort(key=lambda x: x[0]); 
print('\n'.join(f'{c}: {b} (leaf={l})' for c, b, l in leaves)); 
print('Sum of leaves:', sum(b for c, b, l in leaves if l))
