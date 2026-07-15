from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('', views.UserListView.as_view(), name='user_list'),
    path('crear/', views.UserCreateView.as_view(), name='user_create'),
    path('editar/<int:pk>/', views.UserUpdateView.as_view(), name='user_update'),
    path('estado/<int:pk>/', views.user_toggle_active, name='user_toggle_active'),
    path('ajax/load-positions/', views.load_positions, name='ajax_load_positions'),
]
