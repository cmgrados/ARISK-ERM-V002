import os
import django
import sys
from decimal import Decimal

# Add project root to sys.path
sys.path.append('c:/Users/VICTUS/Desktop/A.RISK ERM')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from liquidity_risk.models import LiqSavingsAccount, LiqTermDeposit, LiqSavingsUpload, LiqTermDepositUpload
from django.db import transaction

def normalize_simple(text):
    if not text: return ""
    return str(text).upper().strip().replace(' ', '_').replace('.', '')

SAVINGS_KEYWORDS = ['AHORRO', 'VISTA', 'SOCIAL', 'CORRIENTE', 'DEVOLUCION', 'DISPONIBLE', 'FOMENTO', 'SOCIOS', 'PERSONA', 'JURIDICA', 'CTS', 'PREFERENCIAL', 'ADMISION', 'KIDS', 'SNACKS', 'BEBIDAS', 'CAFETERIA', 'PROMOCIONAL']

def fix_misclassified_liabilities():
    print("Starting data recovery...")
    misclassified = LiqTermDeposit.objects.all()
    moved_count = 0
    
    with transaction.atomic():
        for dpf in misclassified:
            prod_norm = normalize_simple(dpf.product)
            is_savings = any(k in prod_norm for k in SAVINGS_KEYWORDS)
            
            if is_savings:
                # Create corresponding Savings record
                savings_upload, _ = LiqSavingsUpload.objects.get_or_create(period=dpf.period)
                
                LiqSavingsAccount.objects.create(
                    upload=savings_upload,
                    period=dpf.period,
                    customer_id=dpf.customer_id,
                    customer_name=dpf.customer_name,
                    document=dpf.document,
                    account_number=dpf.certificate_number,
                    product=dpf.product,
                    currency=dpf.currency,
                    balance=dpf.balance,
                    opening_date=dpf.opening_date,
                    agency=dpf.agency,
                    opening_agency=dpf.opening_agency,
                    customer_age=dpf.customer_age,
                    customer_gender=dpf.customer_gender,
                    customer_birth_date=dpf.customer_birth_date,
                    created_by_user_code=dpf.created_by_user_code,
                    captador=dpf.captador,
                    is_major_depositor=dpf.is_major_depositor,
                    customer_type=dpf.customer_type,
                    segment=dpf.product[:50]
                )
                dpf.delete()
                moved_count += 1
                
    print(f"Recovery complete. Moved {moved_count} records from Term Deposits to Savings.")

if __name__ == "__main__":
    fix_misclassified_liabilities()
