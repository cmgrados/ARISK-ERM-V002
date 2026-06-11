from django.urls import path
from . import views

app_name = 'controls'

urlpatterns = [
    path('inventario/', views.control_list, name='control_inventory'),
]
