from django.urls import path
from . import views

app_name = 'utilities'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('carga-masiva/', views.bulk_load_credit, name='bulk_load_credit'),
    path('carga-masiva-pasivos/', views.bulk_load_liability, name='bulk_load_liability'),
    path('descargar-plantilla/', views.download_credit_template, name='download_credit_template'),
    path('descargar-plantilla-pasivos/', views.download_liability_template, name='download_liability_template'),
    path('descargar-plantilla-pasivos-csv/', views.download_liability_csv, name='download_liability_csv'),
    path('exportar-datos/', views.export_credit_data, name='export_credit_data'),
    path('exportar-pasivos/', views.export_liability_data, name='export_liability_data'),
    path('eliminar-log/<int:log_id>/', views.delete_bulk_load_log, name='delete_bulk_load_log'),
    path('eliminar-logs-masivo/', views.bulk_delete_logs, name='bulk_delete_logs'),
    path('detalle-carga-pasivos/<int:log_id>/', views.bulk_load_liability_detail, name='bulk_load_liability_detail'),

    # Carga Masiva Socios
    path('carga-masiva-socios/', views.bulk_load_socios, name='bulk_load_socios'),
    path('descargar-plantilla-socios/', views.download_socios_template, name='download_socios_template'),
    path('detalle-carga-socios/<int:log_id>/', views.bulk_load_socios_detail, name='bulk_load_socios_detail'),


    # Migrated from Liquidity Risk
    path('carga/balance/', views.load_balance, name='load_balance'),
    path('carga/balance/template/', views.download_balance_template, name='download_balance_template'),
    path('carga/balance/view/<int:upload_id>/', views.view_balance, name='view_balance'),
    path('carga/balance/download/<int:upload_id>/', views.download_balance_data, name='download_balance_data'),
    path('carga/balance/delete/<int:upload_id>/', views.delete_balance, name='delete_balance'),
    path('carga/balance/bulk_delete/', views.bulk_delete_balance_logs, name='bulk_delete_balance_logs'),
    path('maestro-cuentas/', views.account_mapping, name='account_mapping'),
    path('maestro-cuentas/modelo/eliminar/', views.delete_account_plan_model, name='delete_account_plan_model'),
    path('maestro-cuentas/eliminar/<int:mapping_id>/', views.delete_account_mapping, name='delete_account_mapping'),
    path('backups/', views.backup_manager, name='backup_manager'),
    path('backups/create/', views.create_backup, name='create_backup'),
    path('backups/download/<int:backup_id>/', views.download_backup, name='download_backup'),
    path('backups/delete/<int:backup_id>/', views.delete_backup, name='delete_backup'),
    path('backups/restore/', views.restore_backup, name='restore_backup'),
    path('backups/schedule/', views.schedule_backup, name='schedule_backup'),
]
