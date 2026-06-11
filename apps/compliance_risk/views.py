from django.shortcuts import render, redirect
from .models import ComplianceRequirement, ComplianceRisk, ComplianceFinding
from .forms import ComplianceRiskForm
from django.db.models import Count, Q

def dashboard(request):
    risks = ComplianceRisk.objects.all()
    # Stats for dashboard
    by_source = ComplianceRequirement.objects.values('source').annotate(count=Count('id'))
    
    context = {
        'page_title': 'Dashboard de Cumplimiento',
        'risks': risks,
        'by_source': by_source,
    }
    return render(request, 'compliance_risk/dashboard.html', context)

def matrix(request):
    risks = ComplianceRisk.objects.select_related('requirement', 'requirement__responsible_area').all()
    context = {
        'page_title': 'Matriz de Riesgos de Cumplimiento',
        'risks': risks,
    }
    return render(request, 'compliance_risk/matrix.html', context)

def create_risk(request):
    if request.method == 'POST':
        form = ComplianceRiskForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('compliance_risk:matrix')
    else:
        form = ComplianceRiskForm()
    
    context = {
        'page_title': 'Nueva Evaluación de Cumplimiento',
        'form': form,
    }
    return render(request, 'compliance_risk/risk_form.html', context)

def methodologies(request):
    context = {'page_title': 'Riesgo de Cumplimiento - Metodologías'}
    return render(request, 'compliance_risk/methodologies.html', context)

def reports(request):
    context = {'page_title': 'Riesgo de Cumplimiento - Reportes'}
    return render(request, 'compliance_risk/reports.html', context)
