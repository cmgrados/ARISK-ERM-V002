from django.urls import path
from . import views

app_name = 'op_risk'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('procesos/', views.process_list, name='process_list'),
    path('riesgos/', views.risk_matrix, name='risk_matrix'),
    path('controles/', views.control_matrix, name='control_matrix'),
    path('eventos/', views.event_log, name='event_log'),
    path('kris/', views.kpi_kri, name='kpi_kri'),
    path('planes-accion/', views.action_plans, name='action_plans'),
    path('documentos/', views.documents, name='documents'),
    path('reportes/', views.reports, name='reports'),
    path('reportes/ejecutivo/', views.executive_report, name='executive_report'),
    path('reportes/ejecutivo/pdf/', views.download_executive_pdf, name='executive_report_pdf'),
    path('reportes/ejecutivo/docx/', views.download_executive_docx, name='executive_report_docx'),
    path('capital/', views.capital_list, name='capital_list'),
    path('reporte-rapido/', views.quick_report, name='quick_report'),
    path('api/ai-copilot/', views.ai_copilot, name='ai_copilot'),
    path('api/ai-chat/', views.ai_chat_assistant, name='ai_chat_assistant'),
    path('api/global-ai-chat/', views.global_ai_chat, name='global_ai_chat'),
    
    # Generic CRUD Frontend Views
    path('crear/<str:tipo>/', views.GenericCreateView.as_view(), name='generic_create'),
    path('editar/<str:tipo>/<int:pk>/', views.GenericUpdateView.as_view(), name='generic_update'),
    path('eliminar/<str:tipo>/<int:pk>/', views.GenericDeleteView.as_view(), name='generic_delete'),
]
