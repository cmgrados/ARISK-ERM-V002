from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import (
    RAFFramework, RAFStatement, KRICatalog, RAFThreshold, 
    KRIMeasurement, RAFBreach, RAFActionPlan, RAFApproval, RAFChangeLog
)

def dashboard(request):
    """Dashboard general de apetito y tolerancia."""
    framework = RAFFramework.objects.filter(state='APPROVED').first()
    measurements = KRIMeasurement.objects.all().order_by('-cut_off_date')[:10]
    breaches = RAFBreach.objects.filter(state='OPEN')
    
    context = {
        'page_title': 'Dashboard Ejecutivo RAF',
        'framework': framework,
        'recent_measurements': measurements,
        'active_breaches': breaches,
    }
    return render(request, 'risk_appetite/dashboard.html', context)

def framework_config(request):
    """Configuración del marco institucional."""
    frameworks = RAFFramework.objects.all().order_by('-version')
    return render(request, 'risk_appetite/framework_config.html', {
        'page_title': 'Marco Institucional de Apetito',
        'frameworks': frameworks
    })

def statements(request):
    """Declaraciones de apetito por tipo de riesgo."""
    active_framework = RAFFramework.objects.filter(state='APPROVED').first()
    statements = RAFStatement.objects.filter(framework=active_framework) if active_framework else []
    return render(request, 'risk_appetite/statements.html', {
        'page_title': 'Declaraciones de Apetito',
        'statements': statements,
        'framework': active_framework
    })

def kri_catalog(request):
    """Catálogo maestro de KRIs."""
    kris = KRICatalog.objects.all().order_by('code')
    return render(request, 'risk_appetite/kri_catalog.html', {
        'page_title': 'Catálogo Maestro de KRIs',
        'kris': kris
    })

def threshold_config(request):
    """Configuración de límites y umbrales."""
    active_framework = RAFFramework.objects.filter(state='APPROVED').first()
    thresholds = RAFThreshold.objects.filter(framework=active_framework) if active_framework else []
    return render(request, 'risk_appetite/threshold_config.html', {
        'page_title': 'Límites y Umbrales Quantitative',
        'thresholds': thresholds,
        'framework': active_framework
    })

def measurements(request):
    """Carga y consulta de mediciones."""
    measurements = KRIMeasurement.objects.all().order_by('-cut_off_date')
    return render(request, 'risk_appetite/measurements.html', {
        'page_title': 'Registro de Mediciones KRIs',
        'measurements': measurements
    })

def alerts_panel(request):
    """Panel de alertas y excesos."""
    breaches = RAFBreach.objects.all().order_by('-event_date')
    return render(request, 'risk_appetite/alerts_panel.html', {
        'page_title': 'Panel de Alertas y Excesos',
        'breaches': breaches
    })

def action_plans(request):
    """Registro y seguimiento de acciones correctivas."""
    plans = RAFActionPlan.objects.all().order_by('-start_date')
    return render(request, 'risk_appetite/action_plans.html', {
        'page_title': 'Planes de Acción Correctiva',
        'plans': plans
    })

def approvals(request):
    """Flujo de revisión y aprobación."""
    approvals = RAFApproval.objects.all().order_by('-date')
    return render(request, 'risk_appetite/approvals.html', {
        'page_title': 'Gobernanza y Aprobaciones',
        'approvals': approvals
    })

def version_history(request):
    """Reportes e historial de versiones."""
    logs = RAFChangeLog.objects.all().order_by('-date')[:50]
    return render(request, 'risk_appetite/version_history.html', {
        'page_title': 'Historial de Versiones y Auditoría',
        'logs': logs
    })
