from django.shortcuts import render

def dashboard(request):
    context = {'page_title': 'Riesgo Reputacional - Dashboard'}
    return render(request, 'reputational_risk/dashboard.html', context)

def rep_data(request):
    context = {'page_title': 'Riesgo Reputacional - Monitoreo de Medios'}
    return render(request, 'reputational_risk/rep_data.html', context)

def methodologies(request):
    context = {'page_title': 'Riesgo Reputacional - Metodologías'}
    return render(request, 'reputational_risk/methodologies.html', context)

def controls(request):
    context = {'page_title': 'Riesgo Reputacional - Planes de Crisis'}
    return render(request, 'reputational_risk/controls.html', context)

def reports(request):
    context = {'page_title': 'Riesgo Reputacional - Reportes'}
    return render(request, 'reputational_risk/reports.html', context)
