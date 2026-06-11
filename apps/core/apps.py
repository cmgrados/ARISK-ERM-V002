from django.apps import AppConfig
from django.db.backends.signals import connection_created
from django.dispatch import receiver

class CoreConfig(AppConfig):
    name = 'core'
    verbose_name = 'Sistema Core'

    def ready(self):
        # Database optimization signals
        pass

@receiver(connection_created)
def set_sqlite_pragma(sender, connection, **kwargs):
    if connection.vendor == 'sqlite':
        cursor = connection.cursor()
        # Enable WAL mode for better concurrency
        cursor.execute('PRAGMA journal_mode=WAL;')
        # Set synchronous to NORMAL for faster writes (safe in WAL mode)
        cursor.execute('PRAGMA synchronous=NORMAL;')
        # Increase cache size (default is 2000 pages)
        cursor.execute('PRAGMA cache_size=-64000;') # ~64MB
        # Optimize memory usage
        cursor.execute('PRAGMA temp_store=MEMORY;')
