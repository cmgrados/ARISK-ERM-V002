from django.urls import path
from . import views

app_name = 'liquidity_risk'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('metodologia-lar/', views.metodologia_lar, name='metodologia_lar'),
    path('parametrizacion-sbs/', views.parametrizacion_sbs, name='parametrizacion_sbs'),
    path('validacion/', views.validacion_maestra, name='validacion_maestra'),
]
