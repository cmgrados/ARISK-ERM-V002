import datetime
from django.db.models import Count, Sum, Q, F
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET

@login_required
@require_GET
def api_available_passive_dates(request):
    try:
        from apps.liquidity_risk.models import LiqLiabilityDetail
        db_periods = LiqLiabilityDetail.objects.dates('period', 'month').order_by('-period')
        dates_list = [{"value": p.strftime("%Y-%m-%d"), "label": p.strftime("%Y-%m")} for p in db_periods]
        return JsonResponse({'status': 'success', 'data': dates_list})
    except Exception as e:
        return JsonResponse({'status': 'error', 'msg': str(e)}, status=500)

@login_required
@require_GET
def api_historical_passive_data(request):
    try:
        from apps.liquidity_risk.models import LiqLiabilityDetail
        from apps.utilities.models import Socio
        
        dates_param = request.GET.get('dates', '')
        selected_dates = []
        if dates_param:
            selected_dates = [datetime.datetime.strptime(d.strip(), "%Y-%m-%d").date() for d in dates_param.split(',') if d.strip()]
        
        if selected_dates:
            db_periods = sorted([datetime.date(d.year, d.month, 1) for d in selected_dates])
        else:
            db_periods = list(LiqLiabilityDetail.objects.dates('period', 'month').order_by('period'))
            
        # Get agencies from liabilities
        agencies = LiqLiabilityDetail.objects.exclude(agency__isnull=True).exclude(agency__exact='').values_list('agency', flat=True).distinct().order_by('agency')
        
        qs_liq = LiqLiabilityDetail.objects.exclude(agency__isnull=True).exclude(agency__exact='')
        if selected_dates:
            query = Q()
            for d in selected_dates:
                query |= Q(period__year=d.year, period__month=d.month)
            qs_liq = qs_liq.filter(query)

        qs_liq = qs_liq.annotate(month_trunc=TruncMonth('period'))
        
        liq_grouped = qs_liq.values('agency', 'month_trunc', 'funding_type').annotate(
            total_balance=Sum('balance')
        )
        
        qs_socio = Socio.objects.exclude(oficina__isnull=True).exclude(oficina__exact='')
        if selected_dates:
            query = Q()
            for d in selected_dates:
                query |= Q(corte__year=d.year, corte__month=d.month)
            qs_socio = qs_socio.filter(query)
            
        qs_socio = qs_socio.annotate(month_trunc=TruncMonth('corte'))
        
        socio_grouped = qs_socio.values('oficina', 'month_trunc').annotate(
            count=Count('id'),
            total_aportes=Sum('aportes')
        )
        
        data = {}
        month_names = {1:'Ene', 2:'Feb', 3:'Mar', 4:'Abr', 5:'May', 6:'Jun', 7:'Jul', 8:'Ago', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dic'}
        
        # Include agencies from socio if not in liabilities
        agencies_socio = Socio.objects.exclude(oficina__isnull=True).exclude(oficina__exact='').values_list('oficina', flat=True).distinct()
        all_agencies = sorted(list(set(list(agencies) + list(agencies_socio))))
        
        for agency in all_agencies:
            agency_name = str(agency).upper()
            data[agency_name] = {}
            for p in db_periods:
                p_str = f"{month_names[p.month]}-{str(p.year)[-2:]}"
                data[agency_name][(p.year, p.month)] = {
                    'period': p_str,
                    'ahorros': 0.0,
                    'dpf': 0.0,
                    'aportes': 0.0,
                    'socios': 0
                }
                
        for row in liq_grouped:
            agency = str(row['agency']).upper()
            year = row['month_trunc'].year
            month = row['month_trunc'].month
            funding_type = row['funding_type']
            
            if agency in data and (year, month) in data[agency]:
                if funding_type == 'AHORRO':
                    data[agency][(year, month)]['ahorros'] += float(row['total_balance'] or 0)
                elif funding_type == 'PLAZO':
                    data[agency][(year, month)]['dpf'] += float(row['total_balance'] or 0)

        for row in socio_grouped:
            agency = str(row['oficina']).upper()
            year = row['month_trunc'].year
            month = row['month_trunc'].month
            
            if agency in data and (year, month) in data[agency]:
                data[agency][(year, month)]['aportes'] += float(row['total_aportes'] or 0)
                data[agency][(year, month)]['socios'] += row['count']
                
        final_data = {}
        for agency_name, periods_dict in data.items():
            final_data[agency_name] = [periods_dict[(p.year, p.month)] for p in db_periods]
                
        return JsonResponse({'status': 'success', 'data': final_data})
    except Exception as e:
        return JsonResponse({'status': 'error', 'msg': str(e)}, status=500)
