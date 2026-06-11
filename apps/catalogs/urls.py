from django.urls import path
from . import views

app_name = 'catalogs'

urlpatterns = [
    path('dashboard/', views.catalogs_dashboard, name='dashboard'),
    path('estructura-organizacional/', views.catalogs_dashboard, name='org_structure'),
    path('mapa-procesos/', views.catalogs_dashboard, name='process_map'),
    
    # Bulk Load (Excel)
    path('plantilla/', views.download_catalogs_template, name='download_template'),
    path('importar/', views.import_catalogs_excel, name='import_excel'),
    
    # Unit CRUD
    path('unidad/nueva/', views.create_unit, name='create_unit'),
    path('unidad/<int:pk>/editar/', views.edit_unit, name='edit_unit'),
    path('unidad/<int:pk>/eliminar/', views.delete_unit, name='delete_unit'),
    
    # Process CRUD
    path('proceso/nuevo/', views.create_process, name='create_process'),
    path('proceso/<int:pk>/editar/', views.edit_process, name='edit_process'),
    path('proceso/<int:pk>/eliminar/', views.delete_process, name='delete_process'),
    path('proceso/<int:pk>/', views.process_detail, name='process_detail'),
    
    # Subprocess CRUD
    path('subproceso/nuevo/', views.create_subprocess, name='create_subprocess'),
    path('subproceso/<int:pk>/editar/', views.edit_subprocess, name='edit_subprocess'),
    path('subproceso/<int:pk>/eliminar/', views.delete_subprocess, name='delete_subprocess'),
]
