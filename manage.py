#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def get_settings_module():
    """Determine settings module based on ENVIRONMENT variable."""
    environment = os.environ.get('ENVIRONMENT', 'development').lower()

    if environment == 'production':
        return 'config.settings.production'
    elif environment == 'testing':
        return 'config.settings.testing'
    else:
        return 'config.settings.development'


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', get_settings_module())
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
