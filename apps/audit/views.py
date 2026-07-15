from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import ActivityLog
from django.core.paginator import Paginator

@login_required
def log_list(request):
    logs_list = ActivityLog.objects.all().select_related('user').order_by('-timestamp')
    paginator = Paginator(logs_list, 50)
    
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_title': 'Logs de Actividad',
        'page_obj': page_obj
    }
    return render(request, 'audit/log_list.html', context)
