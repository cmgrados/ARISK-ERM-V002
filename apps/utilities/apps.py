from django.apps import AppConfig

class UtilitiesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'utilities'

    def ready(self):
        # Solo ejecutar el scheduler en runserver y en el hilo principal de trabajo
        import sys
        import os
        if 'runserver' not in sys.argv or os.environ.get('RUN_MAIN') != 'true':
            return
            
        try:
            from apscheduler.schedulers.background import BackgroundScheduler
            from django_apscheduler.jobstores import DjangoJobStore, register_events
            from apps.utilities.backup_utils import perform_sqlite_backup
            from django_apscheduler.models import DjangoJob
            from django.conf import settings
            
            scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
            scheduler.add_jobstore(DjangoJobStore(), "default")
            
            if not DjangoJob.objects.filter(id='daily_db_backup').exists():
                scheduler.add_job(
                    perform_sqlite_backup,
                    trigger="cron",
                    hour=2,
                    minute=0,
                    id="daily_db_backup",
                    max_instances=1,
                    replace_existing=True,
                    kwargs={'is_scheduled': True}
                )
                print(">> Scheduler inicializado: Backup diario a las 02:00 AM")
                
            register_events(scheduler)
            scheduler.start()
        except Exception as e:
            print(f"No se pudo iniciar el scheduler de backups: {e}")
