from django.shortcuts import render
from .models import Risk, RiskAssessment

def risk_list(request):
    risks = Risk.objects.all().select_related('process', 'risk_type')
    context = {
        'page_title': 'Inventario de Riesgos',
        'risks': risks,
    }
    return render(request, 'risks/risk_list.html', context)

def evaluation_dashboard(request):
    assessments = RiskAssessment.objects.all().order_by('-assessment_date')
    context = {
        'page_title': 'Panel de Evaluación de Riesgos',
        'assessments': assessments,
    }
    return render(request, 'risks/evaluation_dashboard.html', context)
