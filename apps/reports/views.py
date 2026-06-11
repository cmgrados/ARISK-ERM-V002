from django.shortcuts import render

def dashboard(request):
    context = {'page_title': 'Consolidado de Reportes e Informes de Riesgo'}
    return render(request, 'reports/dashboard.html', context)
