"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

def get_settings_module():
    """Determine settings module based on environment."""
    environment = os.environ.get('ENVIRONMENT', 'development').lower()

    if environment == 'production':
        return 'config.settings.production'
    elif environment == 'testing':
        return 'config.settings.testing'
    else:
        return 'config.settings.development'

os.environ.setdefault('DJANGO_SETTINGS_MODULE', get_settings_module())

application = get_wsgi_application()
