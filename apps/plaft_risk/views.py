from django.shortcuts import render
from .models import PlaftAlert, PlaftCustomerProfile

def dashboard(request):
    alerts = PlaftAlert.objects.all().order_by('-date_triggered')
    context = {
        'page_title': 'Riesgo PLAFT - Gráficos Analíticos',
        'alerts': alerts,
    }
    return render(request, 'plaft_risk/dashboard.html', context)

def plaft_data(request):
    profiles = PlaftCustomerProfile.objects.all()
    context = {'page_title': 'Riesgo PLAFT - Perfilado de Cliente', 'profiles': profiles}
    return render(request, 'plaft_risk/plaft_data.html', context)

def methodologies(request):
    context = {'page_title': 'Riesgo PLAFT - Matriz de Factores'}
    return render(request, 'plaft_risk/methodologies.html', context)

def controls(request):
    context = {'page_title': 'Riesgo PLAFT - Filtros y Monitoreo'}
    return render(request, 'plaft_risk/controls.html', context)

def reports(request):
    context = {'page_title': 'Riesgo PLAFT - Reportes ROS/RO'}
    return render(request, 'plaft_risk/reports.html', context)
