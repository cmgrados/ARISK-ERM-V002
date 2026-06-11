from django.shortcuts import render

def mark_data(request):
    context = {'page_title': 'Riesgo de Mercado - Posiciones y Precios'}
    return render(request, 'market_risk/mark_data.html', context)

def methodologies(request):
    context = {'page_title': 'Metodologías de Riesgo de Mercado (VaR, EaR)'}
    return render(request, 'market_risk/methodologies.html', context)

def controls(request):
    context = {'page_title': 'Controles y Límites de Mercado'}
    return render(request, 'market_risk/controls.html', context)

def dashboard(request):
    context = {'page_title': 'Dashboard de Riesgo de Mercado'}
    return render(request, 'market_risk/dashboard.html', context)

def reports(request):
    context = {'page_title': 'Reportes de Riesgo de Mercado'}
    return render(request, 'market_risk/reports.html', context)
