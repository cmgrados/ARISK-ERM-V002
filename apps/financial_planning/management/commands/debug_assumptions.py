import os
import django
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arisk_erm.settings')
django.setup()

from credit_risk.models import CreditOperation
from dateutil.relativedelta import relativedelta
import datetime
from django.db.models import Count, Sum, Q, F
from django.db.models.functions import TruncMonth

def test_optimized():
    start = time.time()
    
    selected_dates = [] # Empty for all
    
    qs = CreditOperation.objects.all()
    if selected_dates:
        query = Q()
        for d in selected_dates:
            query |= Q(load_date__year=d.year, load_date__month=d.month)
        qs = qs.filter(query)

    qs = qs.annotate(month_trunc=TruncMonth('load_date'))

    print("Running advisors_qs...")
    advisors_qs = qs.values('agency', 'month_trunc').annotate(advisors=Count('advisor', distinct=True))
    advisors_dict = {(row['agency'], row['month_trunc']): row['advisors'] for row in advisors_qs}

    print("Running port_qs...")
    port_qs = qs.values('agency', 'month_trunc', 'credit_type').annotate(
        count=Count('id'),
        total=Sum('balance'),
        vcda=Sum('past_due_portfolio')
    )

    print("Running disb_qs...")
    disb_qs = qs.filter(
        disbursement_date__year=F('load_date__year'),
        disbursement_date__month=F('load_date__month')
    ).values('agency', 'month_trunc', 'credit_type').annotate(
        count=Count('id'),
        total=Sum('original_amount')
    )
    
    print(f"Optimized queries took {time.time() - start:.2f}s")
    
    print(f"Records loaded: Advisors {len(advisors_dict)}, Port {len(port_qs)}, Disb {len(disb_qs)}")
    return True

if __name__ == '__main__':
    test_optimized()
