import os
import django
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncMonth

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from credit_risk.models import CreditOperation
from dateutil.relativedelta import relativedelta
import datetime

def aggregate_portfolio():
    # Example logic
    agencies = CreditOperation.objects.values_list('agency', flat=True).distinct().order_by('agency')
    
    # We want periods based on what we have in the DB
    periods = CreditOperation.objects.dates('load_date', 'month').order_by('load_date')
    print("Agencies:", list(agencies))
    print("Periods:", list(periods))

    # To calculate number of analysts per agency and month:
    for agency in agencies:
        print(f"\nAgency: {agency}")
        for p in periods:
            end_date = p + relativedelta(day=31)
            qs = CreditOperation.objects.filter(agency=agency, load_date__year=p.year, load_date__month=p.month)
            
            # Count distinct advisors
            advisors = qs.values('advisor').distinct().count()
            
            # Disbursements in this month
            # Wait, do we consider disbursements if disbursement_date is in this month AND load_date is in this month?
            # Yes, usually if load_date is the end of the month, any operation disbursed in this month will have disbursement_date in this month.
            # But they might have been disbursed and paid off? Usually we just look at the portfolio at load_date.
            disb_qs = qs.filter(disbursement_date__year=p.year, disbursement_date__month=p.month)
            
            disb_count = disb_qs.count()
            disb_sum = disb_qs.aggregate(t=Sum('original_amount'))['t'] or 0
            
            # Portfolio
            port_count = qs.count()
            port_sum = qs.aggregate(t=Sum('balance'))['t'] or 0
            
            # Vencida
            vcda_sum = qs.aggregate(t=Sum('past_due_portfolio'))['t'] or 0
            
            if port_count > 0:
                print(f"  {p.strftime('%b-%y')}: Analysts={advisors}, Disb=({disb_count}, {disb_sum}), Port=({port_count}, {port_sum}), Vcda={vcda_sum}")

aggregate_portfolio()
