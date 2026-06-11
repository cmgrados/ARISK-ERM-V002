from django.urls import path
from . import views

app_name = 'risk_appetite'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('framework/', views.framework_config, name='framework_config'),
    path('statements/', views.statements, name='statements'),
    path('kri-catalog/', views.kri_catalog, name='kri_catalog'),
    path('thresholds/', views.threshold_config, name='threshold_config'),
    path('measurements/', views.measurements, name='measurements'),
    path('alerts/', views.alerts_panel, name='alerts_panel'),
    path('action-plans/', views.action_plans, name='action_plans'),
    path('approvals/', views.approvals, name='approvals'),
    path('history/', views.version_history, name='audit_history'),
    
    # Compatibility redirects
    path('parametros/', views.framework_config, name='parameters'),
    path('tolerancias/', views.threshold_config, name='tolerances'),
    path('monitoreo/', views.measurements, name='monitoring'),
    path('reportes/', views.version_history, name='reports'),
]
