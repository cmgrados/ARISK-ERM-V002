from django.urls import path
from . import views

app_name = 'liquidity_risk'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Cargas (Balance and Account Mapping moved to Utilities)
    path('carga/ahorros/', views.load_savings, name='load_savings'),
    path('carga/dpf/', views.load_term_deposits, name='load_term_deposits'),
    path('carga/aportes/', views.load_contributions, name='load_contributions'),
    path('carga/lineas/', views.load_funding, name='load_funding'),
    path('carga/inversiones/', views.load_investments, name='load_investments'),
    path('carga/cartera/', views.load_portfolio, name='load_portfolio'),
    path('carga/validaciones/', views.validations, name='validations'),
    
    # Analítica
    path('posicion-mensual/', views.monthly_position, name='monthly_position'),
    path('analisis-brecha/', views.gap_analysis, name='gap_analysis'),
    path('concentracion/', views.concentration, name='concentration'),
    path('stress-testing/', views.stress_testing, name='stress_testing'),
    
    # Parametrización
    path('sbs-parametros/', views.sbs_parameters, name='sbs_parameters'),
    path('lar-metodologia/', views.lar_methodology, name='lar_methodology'),
    path('lar-metodologia/eliminar/<int:pk>/', views.delete_lar_result, name='delete_lar_result'),
    path('lar-metodologia/aplicar/<int:pk>/', views.apply_lar_to_gap, name='apply_lar_to_gap'),
    path('carga/eliminar/<str:upload_type>/<int:pk>/', views.delete_lar_upload, name='delete_lar_upload'),
    path('maestro-cuentas/eliminar/<int:pk>/', views.delete_account_mapping, name='delete_account_mapping'),
    
    # Controles y Otros
    path('limites-alertas/', views.controls, name='controls'),
    path('contingencia/', views.contingency_plan, name='contingency_plan'),
    path('reportes/', views.reports, name='reports'),
    path('auditoria/', views.audit, name='audit'),
]
