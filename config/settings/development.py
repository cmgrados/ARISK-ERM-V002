"""
Development settings for A.RISK ERM.
Enable DEBUG, verbose logging, no HTTPS enforcement.
"""

from .base import *  # noqa

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Development database (SQLite by default)
# Override with: DATABASE_URL=postgres://... python manage.py runserver
DATABASES = settings.DATABASES

# Detailed logging in development
LOG_LEVEL = 'DEBUG'
LOGGING = settings.LOGGING

# Disable HTTPS enforcement in development
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Easier password validation in development
AUTH_PASSWORD_VALIDATORS = []

# Email backend for development (prints to console)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
