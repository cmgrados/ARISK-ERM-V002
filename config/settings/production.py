"""
Production settings for A.RISK ERM.
Security hardened, HTTPS required, no debug output.
"""

import os
from .base import *  # noqa

# ============================================================================
# SECURITY: MUST BE SET IN PRODUCTION
# ============================================================================

# 🔴 CRITICAL: SECRET_KEY must be overridden via environment
if 'django-insecure' in settings.SECRET_KEY:
    raise ValueError(
        '❌ FATAL: SECRET_KEY not configured for production! '
        'Set SECRET_KEY in environment variables or .env with a strong, unique key'
    )

# 🔴 CRITICAL: DEBUG must be OFF in production
DEBUG = False

# 🔴 CRITICAL: Set specific hosts, not wildcards
ALLOWED_HOSTS = settings.ALLOWED_HOSTS
if '*' in ALLOWED_HOSTS:
    raise ValueError(
        '❌ FATAL: ALLOWED_HOSTS contains "*" in production! '
        'Set specific hosts only (e.g., "myapp.com,www.myapp.com")'
    )

# ============================================================================
# HTTPS / SECURITY HEADERS
# ============================================================================

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# HSTS (1 year = 31536000 seconds)
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Additional security headers
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True

# ============================================================================
# DATABASE: Use PostgreSQL in production!
# ============================================================================

DATABASES = settings.DATABASES

# If SQLite is somehow used, fail loudly
if 'sqlite' in settings.DATABASE_URL.lower():
    import warnings
    warnings.warn(
        '⚠️ WARNING: SQLite detected in production! '
        'Use PostgreSQL for production databases. '
        'Set DATABASE_URL=postgres://...',
        RuntimeWarning
    )

# ============================================================================
# LOGGING: File-based with rotation
# ============================================================================

LOG_LEVEL = settings.LOG_LEVEL
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            'format': '%(asctime)s %(levelname)s %(name)s %(message)s',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/django/app.log',
            'maxBytes': 1024 * 1024 * 100,  # 100MB
            'backupCount': 10,
            'formatter': 'json',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': LOG_LEVEL,
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
        'apps': {
            'handlers': ['file'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
    },
}

# ============================================================================
# EMAIL: Configure for production
# ============================================================================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

# ============================================================================
# CACHING: Enable caching for performance
# ============================================================================

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1'),
    }
}

# ============================================================================
# SESSION & COOKIES
# ============================================================================

SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# ============================================================================
# STATIC FILES: Use CDN or whitenoise
# ============================================================================

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
