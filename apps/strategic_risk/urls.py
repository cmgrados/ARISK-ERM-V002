from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = 'strategic_risk'

urlpatterns = [
    path('', RedirectView.as_view(url='graficos/', permanent=False), name='index'),
    path('datos/', views.strat_data, name='strat_data'),
    path('metodologias/', views.methodologies, name='methodologies'),
    path('controles/', views.controls, name='controls'),
    path('graficos/', views.dashboard, name='dashboard'),
    path('graficos/crear-plan/', views.plan_create, name='plan_create'),
    path('graficos/editar-plan/<int:pk>/', views.plan_update, name='plan_update'),
    path('graficos/set-active/<int:pk>/', views.set_active_plan, name='set_active_plan'),
    path('reportes/', views.reports, name='reports'),
    
    # AJAX Endpoints
    path('ajax/save-matrix/', views.save_matrix, name='save_matrix'),
    path('ajax/save-canvas/', views.save_canvas, name='save_canvas'),
    path('ajax/save-mpc/', views.save_mpc, name='save_mpc'),
    path('ajax/save-philosophy/', views.save_philosophy, name='save_philosophy'),
    path('ajax/add-objective/', views.add_objective, name='add_objective'),
    path('ajax/add-kpi/', views.add_kpi, name='add_kpi'),
    path('ajax/save-metas-planeadas/', views.save_metas_planeadas, name='save_metas_planeadas'),
]
