from django.urls import path
from . import views

app_name = 'credit_risk'

urlpatterns = [
    path('datos/', views.credit_data, name='data'),
    path('metodologias/', views.methodologies, name='methodologies'),
    path('metodologias/export/excel/', views.export_methodologies_excel, name='export_methodologies_excel'),
    path('metodologias/export/word/', views.export_methodologies_word, name='export_methodologies_word'),
    path('metodologias/export/pdf/', views.export_methodologies_pdf, name='export_methodologies_pdf'),
    path('controles/', views.controls, name='controls'),
    path('graficos/', views.dashboard, name='dashboard'),
    path('transiciones/', views.transition_matrix, name='transition_matrix'),
    path('cosechas/', views.vintage_analysis, name='vintage_analysis'),
    path('perdida-esperada/', views.expected_loss_analysis, name='expected_loss_analysis'),
    path('perdida-esperada/export/word/', views.export_expected_loss_word, name='export_expected_loss_word'),
    path('reportes/', views.reports, name='reports'),
    path('reportes/sbs-pdf/', views.export_sbs_annex_pdf, name='export_sbs_annex_pdf'),
    path('reportes/sbs-excel/', views.export_sbs_annex_excel, name='export_sbs_annex_excel'),
    path('reportes/provisiones-excel/', views.export_provisions_excel, name='export_provisions_excel'),
    path('reportes/consolidado-pdf/', views.export_consolidated_report, name='export_consolidated_report'),
    path('scoring/', views.scoring_segment, name='scoring_segment'),
    path('concentracion/', views.concentration, name='concentration'),
    path('alertas/', views.deterioration_alerts, name='deterioration_alerts'),
]
