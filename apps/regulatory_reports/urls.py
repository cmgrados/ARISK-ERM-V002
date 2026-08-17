from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = 'regulatory_reports'

urlpatterns = [
    path('', RedirectView.as_view(url='portal/', permanent=False), name='portal_redirect'),
    path('portal/', views.portal_anexos, name='portal_anexos'),
    path('reporte-13/', views.reporte_13, name='reporte_13'),
    # Placeholder URLs for other reports to not break links in portal
    path('anexo-2a/', views.anexo_2a, name='anexo_2a'),
    path('anexo-2d/', views.anexo_2d, name='anexo_2d'),
    path('anexo-13/', views.anexo_13, name='anexo_13'),
    path('anexo-15/', views.anexo_15, name='anexo_15'),
    path('anexo-17b/', views.anexo_17b, name='anexo_17b'),
    path('anexo-15a/', views.anexo_15a, name='anexo_15a'),
    path('anexo-5/', views.anexo_5, name='anexo_5'),
    path('anexo-17a/', views.anexo_17a, name='anexo_17a'),
]
