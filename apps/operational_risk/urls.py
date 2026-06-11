from django.urls import path
from . import views

app_name = 'operational_risk'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('datos/', views.op_data, name='op_data'),
    path('diagnostico/', views.coso_diagnostic, name='coso_diagnostic'),
    path('save-coso/', views.save_coso_assessment, name='save_coso_assessment'),
    path('matriz/', views.risk_matrix, name='risk_matrix'),
    path('matriz/guardar-rcsa/', views.save_rcsa, name='save_rcsa'),
    path('matriz/exportar/', views.export_op_risk_excel, name='export_excel'),
    path('matriz/importar-rcsa/', views.import_rcsa_excel, name='import_rcsa_excel'),
    path('matriz/plantilla-rcsa/', views.download_rcsa_template, name='download_rcsa_template'),
    path('importar/', views.import_op_risk_excel, name='import_excel'),
    path('plantilla/', views.download_op_risk_template, name='download_template'),
    path('guardar-evento/', views.save_event, name='save_event'),
    path('eliminar-evento/', views.delete_event, name='delete_event'),
    path('eliminar-masivo/', views.bulk_delete, name='bulk_delete'),
    
    # Posibles Pérdidas
    path('posibles-perdidas/', views.potential_loss_list, name='potential_loss_list'),
    path('posibles-perdidas/nuevo/', views.potential_loss_create, name='potential_loss_create'),
    path('posibles-perdidas/<int:pk>/', views.potential_loss_detail, name='potential_loss_detail'),
    path('posibles-perdidas/<int:pk>/editar/', views.potential_loss_edit, name='potential_loss_edit'),
    path('posibles-perdidas/<int:pk>/eliminar/', views.potential_loss_delete, name='potential_loss_delete'),
    path('posibles-perdidas/<int:pk>/ajustar/', views.potential_loss_adjust, name='potential_loss_adjust'),
    path('posibles-perdidas/exportar/', views.export_potential_losses_excel, name='export_potential_losses_excel'),
    path('posibles-perdidas/importar/', views.import_potential_losses_excel, name='import_potential_losses_excel'),
    path('posibles-perdidas/plantilla/', views.download_potential_loss_template, name='download_potential_loss_template'),
    
    # Detalle de Riesgo y Evaluación
    path('matriz/riesgo/nuevo/', views.create_risk, name='create_risk'),
    path('matriz/riesgo/<int:pk>/', views.risk_detail, name='risk_detail'),
    path('matriz/riesgo/<int:pk>/eliminar/', views.delete_risk, name='delete_risk'),
    path('matriz/riesgo/<int:pk>/evaluar/', views.save_risk_assessment, name='save_risk_assessment'),
    
    # Flujo y Reportes
    path('ciclo-gestion/', views.management_cycle, name='management_cycle'),
    path('informe-ejecutivo/', views.executive_report, name='executive_report'),
    path('ai-chat/', views.op_risk_ai_chat, name='ai_chat'),
]
