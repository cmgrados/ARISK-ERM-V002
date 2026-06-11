from django.urls import path
from . import views

app_name = 'plaft_risk'

urlpatterns = [
    path('datos/', views.plaft_data, name='plaft_data'),
    path('metodologias/', views.methodologies, name='methodologies'),
    path('controles/', views.controls, name='controls'),
    path('graficos/', views.dashboard, name='dashboard'),
    path('reportes/', views.reports, name='reports'),
]
