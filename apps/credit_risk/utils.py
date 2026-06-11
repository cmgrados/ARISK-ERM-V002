from decimal import Decimal
from django.db import transaction
from .models import CreditOperation, CreditRiskMetrics

def generate_missing_metrics(load_date=None, force_recalculate=False):
    """
    Generates or updates CreditRiskMetrics for operations.
    """
    # Mapping SBS Classifications to standard PD (Case-insensitive)
    pd_map = {
        'NORMAL': Decimal('0.70'),
        '0': Decimal('0.70'),
        'A': Decimal('0.70'),
        'CPP': Decimal('5.00'),
        'B': Decimal('5.00'),
        'PROBLEMA': Decimal('5.00'),
        'POTENCIAL': Decimal('5.00'),
        '1': Decimal('5.00'),
        'DEFICIENTE': Decimal('25.00'),
        'C': Decimal('25.00'),
        '2': Decimal('25.00'),
        'DUDOSO': Decimal('60.00'),
        'D': Decimal('60.00'),
        '3': Decimal('60.00'),
        'PERDIDA': Decimal('100.00'),
        'PÉRDIDA': Decimal('100.00'),
        'E': Decimal('100.00'),
        '4': Decimal('100.00'),
    }
    lgd_standard = Decimal('45.00')
    
    if force_recalculate:
        query = CreditOperation.objects.all()
    else:
        query = CreditOperation.objects.filter(metrics__isnull=True)
        
    if load_date:
        query = query.filter(load_date=load_date)
        
    # Use values to avoid model instantiation overhead
    ops_data = query.values('id', 'sbs_classification', 'balance', 'days_past_due', 'metrics__id')
    
    metrics_to_create = []
    metrics_to_update = []
    
    # Pre-compiled mapping keys for faster lookup - SORTED BY LENGTH DESCENDING
    # This prevents substring matches (like 'A' in 'PERDIDA') from taking priority.
    pd_keys = sorted(pd_map.keys(), key=len, reverse=True)
    
    for op in ops_data:
        classification = (op['sbs_classification'] or '').upper().strip()
        pd_val = Decimal('0.70') # Default to Normal
        
        # 1. PD based on SBS Classification
        if classification in pd_map:
            pd_val = pd_map[classification]
        else:
            # Fallback to substring matching if no exact match
            for key in pd_keys:
                if key in classification:
                    pd_val = pd_map[key]
                    break
                    
        # 2. PD based on Days Past Due (Conservative Fallback)
        dpd = op.get('days_past_due') or 0
        dpd_pd = Decimal('0.70')
        if dpd > 120:
            dpd_pd = Decimal('100.00') # PERDIDA
        elif dpd > 60:
            dpd_pd = Decimal('60.00')  # DUDOSO
        elif dpd > 30:
            dpd_pd = Decimal('25.00')  # DEFICIENTE
        elif dpd > 8:
            dpd_pd = Decimal('5.00')   # CPP
            
        # Use the most conservative (highest) PD
        final_pd = max(pd_val, dpd_pd)
        
        ead_val = op['balance']
        el_val = (final_pd / Decimal('100')) * ead_val * (lgd_standard / Decimal('100'))
        
        metrics_id = op['metrics__id']
        if metrics_id:
            # Updating existing metric
            metrics_to_update.append(
                CreditRiskMetrics(
                    id=metrics_id,
                    pd=final_pd, ead=ead_val, 
                    lgd=lgd_standard, expected_loss=el_val
                )
            )
        else:
            # Creating new metric
            metrics_to_create.append(
                CreditRiskMetrics(
                    operation_id=op['id'], 
                    pd=final_pd, ead=ead_val, 
                    lgd=lgd_standard, expected_loss=el_val
                )
            )
    
    with transaction.atomic():
        if metrics_to_create:
            CreditRiskMetrics.objects.bulk_create(metrics_to_create, batch_size=1000, ignore_conflicts=True)
        if metrics_to_update:
            CreditRiskMetrics.objects.bulk_update(metrics_to_update, ['pd', 'ead', 'lgd', 'expected_loss'], batch_size=1000)
    
    return len(metrics_to_create) + len(metrics_to_update)
