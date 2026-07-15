from django.db.models import Sum, Case, When, Value, DecimalField, F
from django.db.models.functions import Coalesce
from credit_risk.models import CreditOperation

def get_portfolio_by_buckets(cut_off_date):
    """
    Agrupa la cartera en buckets de mora usando el ORM puro.
    Bucket 0: 0 días
    Bucket 1: 1 a 30 días
    Bucket 2: 31 a 60 días
    Bucket 3: 61 a 90 días
    Bucket 4: > 90 días
    """
    qs = CreditOperation.objects.filter(load_date=cut_off_date)
    
    summary = qs.annotate(
        bucket_label=Case(
            When(days_past_due=0, then=Value('Bucket 0')),
            When(days_past_due__gte=1, days_past_due__lte=30, then=Value('Bucket 1')),
            When(days_past_due__gte=31, days_past_due__lte=60, then=Value('Bucket 2')),
            When(days_past_due__gte=61, days_past_due__lte=90, then=Value('Bucket 3')),
            When(days_past_due__gt=90, then=Value('Bucket 4')),
            default=Value('Desconocido')
        )
    ).values('bucket_label').annotate(
        total_balance=Sum('balance'),
        total_count=Sum(Value(1))
    ).order_by('bucket_label')
    
    return list(summary)

def calculate_hhi_concentration(cut_off_date, group_by_field='customer__economic_activity'):
    """
    Calcula el Índice de Herfindahl-Hirschman (HHI) para medir concentración.
    Se puede agrupar por sector económico ('customer__economic_activity'), 
    por cliente ('customer__document_id'), o por región ('customer__department').
    """
    qs = CreditOperation.objects.filter(load_date=cut_off_date)
    total_portfolio = qs.aggregate(t=Sum('balance'))['t'] or 1
    
    # Agrupamos por el campo solicitado y calculamos su cuota de participación
    groups = qs.values(group_by_field).annotate(
        group_balance=Sum('balance')
    )
    
    hhi = 0
    for group in groups:
        if group['group_balance']:
            share = (group['group_balance'] / total_portfolio) * 100
            hhi += (share ** 2)
            
    return hhi
