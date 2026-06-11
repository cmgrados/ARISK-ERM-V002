from django.urls import path
from . import views

app_name = 'compliance_risk'

urlpatterns = [
    path('matriz/', views.matrix, name='matrix'),
    path('matriz/nueva/', views.create_risk, name='create_risk'),
    path('metodologias/', views.methodologies, name='methodologies'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('reportes/', views.reports, name='reports'),
]
