"""
Monitoring and Error Tracking Configuration
"""
import os
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.redis import RedisIntegration


def init_sentry():
    """Initialize Sentry error tracking"""
    sentry_dsn = os.getenv('SENTRY_DSN')
    
    if sentry_dsn:
        sentry_sdk.init(
            dsn=sentry_dsn,
            integrations=[
                DjangoIntegration(),
                RedisIntegration(),
            ],
            traces_sample_rate=0.1,
            send_default_pii=False,
            environment=os.getenv('ENVIRONMENT', 'development'),
            # Performance Monitoring
            profiles_sample_rate=0.1,
        )


# Initialize monitoring
init_sentry()

# Prometheus metrics configuration
PROMETHEUS_EXPORT_MIGRATIONS = True

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs', 'django.log'),
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 10,
            'formatter': 'json',
        },
        'sentry': {
            'level': 'ERROR',
            'class': 'sentry_sdk.integrations.logging.EventHandler',
        },
    },
    'root': {
        'handlers': ['console', 'file', 'sentry'],
        'level': os.getenv('LOG_LEVEL', 'INFO'),
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file', 'sentry'],
            'level': os.getenv('LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG' if os.getenv('DEBUG') == 'True' else 'INFO',
            'propagate': False,
        },
    },
}
