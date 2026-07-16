from django.urls import path
from . import views

app_name = 'market_risk'

urlpatterns = [
    # Dashboard general redirige a Brechas (o puede ser otra vista consolidada)
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Submódulos
    path('posiciones/', views.positions_view, name='positions'),
    path('brechas/', views.gaps_view, name='gaps'),
    path('sensibilidad/', views.sensitivity_view, name='sensitivity'),
    path('estres/', views.stress_view, name='stress'),
    path('guia/', views.guide_view, name='guide'),
    path('limites/', views.limits_view, name='limits'),
    path('reportes/', views.reports_view, name='reports'),
    path('var/', views.var_view, name='var'),
    
    # Plantillas y Exportaciones
    path('plantilla-csv/', views.download_template_csv, name='download_template_csv'),
    path('exportar/brechas/', views.export_gaps_csv, name='export_gaps_csv'),
    path('exportar/estres/', views.export_stress_csv, name='export_stress_csv'),
]
