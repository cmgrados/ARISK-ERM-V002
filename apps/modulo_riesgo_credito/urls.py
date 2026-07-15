from django.urls import path
from . import views

app_name = 'modulo_riesgo_credito'

urlpatterns = [
    path('seguimiento/', views.dashboard_seguimiento, name='seguimiento'),
    path('exportar-anexo5/', views.descargar_anexo5, name='exportar_anexo5'),
    path('matrices-transicion/', views.transition_matrix_view, name='transition_matrix'),
    path('cosechas-vintage/', views.vintage_view, name='vintage'),
    path('stress-testing/', views.stress_testing_view, name='stress_testing'),
    path('excepciones/', views.overriding_view, name='overriding'),
]
