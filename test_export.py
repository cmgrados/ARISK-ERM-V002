import os
import django
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from credit_risk.models import CreditOperation
import pandas as pd

start = time.time()
qs = CreditOperation.objects.all().values(
    'load_date', 'agency', 'customer__document_number', 'customer__name', 
    'operation_code', 'product_name', 'balance', 'rate', 'disbursement_date', 'credit_type'
)
print("Querying...")
df = pd.DataFrame.from_records(qs)
print(f"Queried {len(df)} rows in {time.time()-start:.2f}s")
start = time.time()
df.to_excel('test_export.xlsx', index=False)
print(f"Exported to Excel in {time.time()-start:.2f}s")
