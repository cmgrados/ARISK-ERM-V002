import os
import django
import sys
import random
from datetime import date
from dateutil.relativedelta import relativedelta
from decimal import Decimal

# Setup Django environment
sys.path.append('c:/Users/VICTUS/Desktop/A.RISK ERM')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from liquidity_risk.models import LiqSavingsAccount, LiqSavingsUpload, LiqLoadStatus

def populate_lar_test_data():
    print("Generating historical savings data for LaR...")
    
    segments = [
        ('AHORRO PERSONA NATURAL', 1000000, 0.02), # Name, Avg Balance, Volatility
        ('AHORRO JURIDICA', 500000, 0.05),
        ('AHORRO CTS', 300000, 0.01)
    ]
    
    currencies = ['MN', 'ME']
    # Last 13 months to have 12 variations
    today = date(2026, 3, 31) # Matching the user's "Marzo" context
    
    for i in range(13):
        period = today - relativedelta(months=i)
        from calendar import monthrange
        _, last_day = monthrange(period.year, period.month)
        period = date(period.year, period.month, last_day)
        
        print(f"  Processing period: {period}")
        
        # Create Upload record
        upload, _ = LiqSavingsUpload.objects.get_or_create(
            period=period,
            defaults={'status': LiqLoadStatus.SUCCESS}
        )
        
        # Clear existing for this period to avoid duplicates
        LiqSavingsAccount.objects.filter(period=period).delete()
        
        for seg_name, avg_bal, vol in segments:
            for curr in currencies:
                # Generate a balance with some random variation
                # Bal = Avg * (1 + random_variation)
                variation = random.uniform(-vol, vol)
                total_bal = Decimal(str(avg_bal * (1 + variation)))
                
                # We'll create one aggregate record per segment/currency for simplicity in testing
                # but the system supports thousands
                LiqSavingsAccount.objects.create(
                    upload=upload,
                    period=period,
                    customer_id=f"SEG-{seg_name[:3]}",
                    customer_name=f"GRUPO {seg_name}",
                    document="99999999",
                    account_number=f"ACC-{seg_name[:3]}-{curr}",
                    product=seg_name,
                    currency=curr,
                    balance=total_bal,
                    opening_date=period - relativedelta(years=1),
                    agency="OFICINA PRINCIPAL",
                    segment=seg_name
                )

    print("Success: 13 months of historical data generated.")

if __name__ == "__main__":
    populate_lar_test_data()
