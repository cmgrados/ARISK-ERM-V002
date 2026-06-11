from django.shortcuts import render
from .models import RiskControl

def control_list(request):
    controls = RiskControl.objects.all().select_related('risk')
    context = {
        'page_title': 'Inventario de Controles',
        'controls': controls,
    }
    return render(request, 'controls/control_list.html', context)
