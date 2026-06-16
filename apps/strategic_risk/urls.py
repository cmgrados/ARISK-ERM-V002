from django.urls import path
from django.views.generic import RedirectView
from . import views
from .api_views import (
    PerspectivaViewSet, ObjetivoEstrategicoViewSet, IndicadorViewSet, 
    MetaPeriodoViewSet, BulkMetasPlaneadasView,
    ProyectoIniciativaViewSet, EjecucionPresupuestariaViewSet, HitoProyectoViewSet,
    DashboardSummaryView, PortafolioPOAViewSet, ActividadPOAViewSet
)
app_name = 'strategic_risk'

urlpatterns = [
    path('', RedirectView.as_view(url='graficos/', permanent=False), name='index'),
    path('datos/', views.strat_data, name='strat_data'),
    path('metodologias/', views.methodologies, name='methodologies'),
    path('controles/', views.controls, name='controls'),
    path('estrategias/', views.estrategias, name='estrategias'),
    path('elaboracion-poa/', views.elaboracion_poa, name='elaboracion_poa'),
    path('graficos/', views.dashboard, name='dashboard'),
    path('graficos/crear-plan/', views.plan_create, name='plan_create'),
    path('graficos/editar-plan/<int:pk>/', views.plan_update, name='plan_update'),
    path('graficos/copiar-plan/<int:pk>/', views.plan_copy, name='plan_copy'),
    path('graficos/eliminar-plan/<int:pk>/', views.plan_delete, name='plan_delete'),
    path('graficos/set-active/<int:pk>/', views.set_active_plan, name='set_active_plan'),
    path('reportes/', views.reports, name='reports'),
    path('exportar/bsc/', views.export_bsc_excel, name='export_bsc_excel'),
    path('public_survey/<str:survey_id>/', views.public_survey, name='public_survey'),
    
    # AJAX Endpoints
    path('ajax/save-matrix/', views.save_matrix, name='save_matrix'),
    path('ajax/save-canvas/', views.save_canvas, name='save_canvas'),
    path('ajax/save-mpc/', views.save_mpc, name='save_mpc'),
    path('ajax/save-philosophy/', views.save_philosophy, name='save_philosophy'),
    path('ajax/add-objective/', views.add_objective, name='add_objective'),
    path('ajax/delete-objective/<int:pk>/', views.delete_objective, name='delete_objective'),
    path('ajax/save-ponderaciones/', views.save_ponderaciones, name='save_ponderaciones'),
    path('ajax/add-kpi/', views.add_kpi, name='add_kpi'),
    path('ajax/delete-kpi/<int:pk>/', views.delete_kpi, name='delete_kpi'),
    path('ajax/delete-multiple-kpis/', views.delete_multiple_kpis, name='delete_multiple_kpis'),
    path('ajax/save-metas-planeadas/', views.save_metas_planeadas, name='save_metas_planeadas'),
    path('ajax/get-kpi-metas/<int:pk>/', views.get_kpi_metas, name='get_kpi_metas'),
    path('ajax/save-kpi-metas/<int:pk>/', views.save_kpi_metas, name='save_kpi_metas'),
    path('estrategias/save-imported/', views.save_imported_strategies, name='save_imported_strategies'),
]

# API Router Setup
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'perspectivas', PerspectivaViewSet, basename='api-perspectiva')
router.register(r'objetivos', ObjetivoEstrategicoViewSet, basename='api-objetivo')
router.register(r'indicadores', IndicadorViewSet, basename='api-indicador')
router.register(r'metas', MetaPeriodoViewSet, basename='api-meta')
router.register(r'proyectos', ProyectoIniciativaViewSet, basename='api-proyecto')
router.register(r'ejecuciones', EjecucionPresupuestariaViewSet, basename='api-ejecucion')
router.register(r'hitos', HitoProyectoViewSet, basename='api-hito')
router.register(r'portafolio-poa', PortafolioPOAViewSet, basename='api-portafolio-poa')
router.register(r'actividades-poa', ActividadPOAViewSet, basename='api-actividades-poa')

from django.urls import include
urlpatterns += [
    path('api/', include(router.urls)),
    path('api/dashboard-summary/', DashboardSummaryView.as_view(), name='dashboard_summary'),
]
