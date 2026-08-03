"""
Testing settings for A.RISK ERM.
Use in-memory SQLite, disable migrations, mute logging.
"""

from .base import *  # noqa

# Use in-memory database for tests (fast)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable migrations in tests (use model definitions directly)
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


MIGRATION_MODULES = DisableMigrations()

# Reduce logging verbosity in tests
LOG_LEVEL = 'WARNING'

# Simple logging for tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'root': {
        'handlers': ['null'],
    },
}

# Faster password hashing in tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable CSRF in API tests
CSRF_TRUSTED_ORIGINS = ['http://testserver', 'http://127.0.0.1']
