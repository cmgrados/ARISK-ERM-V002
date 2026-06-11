from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('lista/', views.user_list, name='user_list'),
    path('nuevo/', views.user_create, name='user_create'),
    path('<int:pk>/editar/', views.user_update, name='user_update'),
    path('<int:pk>/eliminar/', views.user_delete, name='user_delete'),
    path('perfiles/', views.role_list, name='role_list'),
    path('perfiles/nuevo/', views.role_create, name='role_create'),
    path('perfiles/<int:pk>/editar/', views.role_update, name='role_update'),
    path('auditoria/', views.audit_log, name='audit_log'),
]
