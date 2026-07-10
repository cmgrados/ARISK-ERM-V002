import json

new_func = """
@require_http_methods(["POST"])
def api_apply_other_trends(request, plan_id):
    from django.http import JsonResponse
    from django.shortcuts import get_object_or_404
    from .models import PlanFinanciero, ProjectedBalanceAdjustment
    from liquidity_risk.models import LiqBalanceDetail
    from django.db.models import Q
    
    organization = request.user.organization
    if not organization:
        from users.models import Organization
        organization = Organization.objects.first()
        
    plan = get_object_or_404(PlanFinanciero, id=plan_id, organization=organization)
    base_year = plan.anio_base - 1
    
    # Identify first and last month for trend calculation
    months = list(LiqBalanceDetail.objects.filter(period__year=base_year, upload__status='SUCCESS').values_list('period__month', flat=True).distinct().order_by('period__month'))
    if not months or len(months) < 2:
        return JsonResponse({'error': 'No hay suficientes datos historicos para calcular tendencia anual.'}, status=400)
        
    first_month = months[0]
    last_month = months[-1]
    diff_months = last_month - first_month
    if diff_months <= 0: diff_months = 1
    
    upload_first = LiqBalanceDetail.objects.filter(period__year=base_year, period__month=first_month, upload__status='SUCCESS').order_by('-upload_id').values_list('upload_id', flat=True).first()
    upload_last = LiqBalanceDetail.objects.filter(period__year=base_year, period__month=last_month, upload__status='SUCCESS').order_by('-upload_id').values_list('upload_id', flat=True).first()
    
    qs_first = {x['account_code']: float(x['balance']) for x in LiqBalanceDetail.objects.filter(upload_id=upload_first).filter(Q(account_code__startswith='1') | Q(account_code__startswith='2') | Q(account_code__startswith='3')).values('account_code', 'balance')}
    qs_last = {x['account_code']: float(x['balance']) for x in LiqBalanceDetail.objects.filter(upload_id=upload_last).filter(Q(account_code__startswith='1') | Q(account_code__startswith='2') | Q(account_code__startswith='3')).values('account_code', 'balance')}
    
    scenarios = ['PESIMISTA', 'BASE', 'OPTIMISTA', 'MC_PESIMISTA', 'MC_BASE', 'MC_OPTIMISTA']
    
    adjustments_to_create = []
    
    # Process unhandled accounts
    for code, val_last in qs_last.items():
        if code.startswith('14') or code.startswith('21') or code.startswith('3101') or code.startswith('39'):
            continue
            
        val_first = qs_first.get(code, val_last)
        abs_last = abs(val_last)
        abs_first = abs(val_first)
        delta_monthly = (abs_last - abs_first) / diff_months
        
        if delta_monthly != 0.0:
            adj_dict = {str(i): delta_monthly for i in range(1, 37)}
            for sc in scenarios:
                ProjectedBalanceAdjustment.objects.filter(plan=plan, organization=organization, scenario=sc, account_code=code).delete()
                adjustments_to_create.append(
                    ProjectedBalanceAdjustment(
                        plan=plan,
                        organization=organization,
                        scenario=sc,
                        account_code=code,
                        adjustments=adj_dict
                    )
                )
    
    if adjustments_to_create:
        ProjectedBalanceAdjustment.objects.bulk_create(adjustments_to_create)
        
    return JsonResponse({'status': 'success', 'message': f'Tendencia historica aplicada a {len(adjustments_to_create)//len(scenarios)} cuentas para todos los escenarios.'})
"""

with open('apps/financial_planning/views.py', 'a', encoding='utf-8') as f:
    f.write('\n' + new_func + '\n')
