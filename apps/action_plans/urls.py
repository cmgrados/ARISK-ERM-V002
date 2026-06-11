from django.urls import path
from . import views

app_name = 'action_plans'

urlpatterns = [
    path('', views.action_plan_list, name='plan_list'),
    path('nuevo/', views.create_action_plan, name='create_plan'),
    path('<int:pk>/', views.action_plan_detail, name='plan_detail'),
    path('<int:pk>/editar/', views.edit_action_plan, name='edit_plan'),
    path('<int:pk>/eliminar/', views.delete_action_plan, name='delete_plan'),
]
