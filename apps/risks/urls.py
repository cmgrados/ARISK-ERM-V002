from django.urls import path
from . import views

app_name = 'risks'

urlpatterns = [
    path('inventario/', views.risk_list, name='risk_inventory'),
    path('evaluacion/', views.evaluation_dashboard, name='evaluation_dashboard'),
]
