"""
Django settings for A.RISK ERM project - Base configuration.
Uses Pydantic for validated environment-based settings.
"""

import os
import sys
from pathlib import Path
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))


class Settings(BaseSettings):
    """
    Django settings with Pydantic validation.
    Load from .env file or environment variables.
    """

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / '.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='allow',  # Allow extra env vars
    )

    # ============================================================================
    # CORE DJANGO SETTINGS
    # ============================================================================

    # SECRET_KEY - REQUIRED in production
    SECRET_KEY: str = Field(
        default='django-insecure-development-key-change-me-in-production-32chars',
        description='Secret key for Django. Override in production!'
    )

    @field_validator('SECRET_KEY')
    @classmethod
    def validate_secret_key(cls, v: str, info) -> str:
        """Ensure SECRET_KEY is strong in production."""
        if 'django-insecure' in v:
            import warnings
            warnings.warn(
                '⚠️ WARNING: Using insecure SECRET_KEY. '
                'Set SECRET_KEY in .env for production!',
                RuntimeWarning
            )
        if len(v) < 32:
            raise ValueError(
                f'SECRET_KEY must be at least 32 characters (got {len(v)})'
            )
        return v

    # DEBUG
    DEBUG: bool = Field(
        default=False,
        description='Turn off in production!'
    )

    # ALLOWED_HOSTS
    ALLOWED_HOSTS: list[str] = Field(
        default=['localhost', '127.0.0.1'],
        description='List of allowed hosts. Use * only in development!'
    )

    @field_validator('ALLOWED_HOSTS', mode='before')
    @classmethod
    def parse_allowed_hosts(cls, v):
        """Parse comma-separated ALLOWED_HOSTS."""
        if isinstance(v, str):
            return [h.strip() for h in v.split(',')]
        return v

    # ============================================================================
    # DATABASE
    # ============================================================================

    DATABASE_URL: str = Field(
        default='sqlite:///db.sqlite3',
        description='Database connection URL. Supports postgres, mysql, sqlite'
    )

    DATABASE_CONN_MAX_AGE: int = Field(
        default=600,
        description='Database connection pool max age (seconds)'
    )

    # ============================================================================
    # INSTALLED APPS
    # ============================================================================

    INSTALLED_APPS: list[str] = Field(
        default=[
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'django.contrib.staticfiles',
            'django.contrib.humanize',
            'rest_framework',
            'drf_spectacular',
            'django_filters',
            # Internal apps
            'core',
            'users',
            'catalogs',
            'audit',
            'utilities',
            'attachments',
            'dashboards',
            'reports',
            'risks',
            'controls',
            'action_plans',
            'indicators',
            'incidents',
            'credit_risk',
            'liquidity_risk',
            'market_risk',
            'operational_risk',
            'compliance_risk',
            'plaft_risk',
            'strategic_risk',
            'reputational_risk',
            'risk_appetite',
            'ai_assistant',
            'financial_planning',
            'apps.regulatory_reports',
        ]
    )

    # ============================================================================
    # MIDDLEWARE
    # ============================================================================

    MIDDLEWARE: list[str] = Field(
        default=[
            'django.middleware.security.SecurityMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'users.middleware.TenantMiddleware',
            'exception_logger.ExceptionLoggingMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
            'django.middleware.clickjacking.XFrameOptionsMiddleware',
        ]
    )

    # ============================================================================
    # INTERNATIONALIZATION
    # ============================================================================

    LANGUAGE_CODE: str = 'es-pe'
    TIME_ZONE: str = 'America/Lima'
    USE_I18N: bool = False
    USE_TZ: bool = True
    USE_THOUSAND_SEPARATOR: bool = True
    THOUSAND_SEPARATOR: str = ','
    DECIMAL_SEPARATOR: str = '.'
    NUMBER_GROUPING: int = 3

    # ============================================================================
    # STATIC & MEDIA FILES
    # ============================================================================

    STATIC_URL: str = 'static/'
    STATIC_ROOT: str = Field(
        default='staticfiles',
        description='Where to collect static files'
    )

    MEDIA_URL: str = '/media/'
    MEDIA_ROOT: str = Field(
        default='media',
        description='Directory for user uploads'
    )

    # ============================================================================
    # AUTHENTICATION
    # ============================================================================

    AUTH_USER_MODEL: str = 'users.User'
    LOGIN_URL: str = '/admin/login/'
    LOGIN_REDIRECT_URL: str = 'home'
    LOGOUT_REDIRECT_URL: str = 'home'

    # ============================================================================
    # SECURITY SETTINGS (Override in production)
    # ============================================================================

    SECURE_SSL_REDIRECT: bool = Field(
        default=False,
        description='Force HTTPS in production'
    )

    SECURE_HSTS_SECONDS: int = Field(
        default=0,
        description='HSTS header duration (seconds). Set to 31536000 in production'
    )

    SECURE_HSTS_INCLUDE_SUBDOMAINS: bool = False
    SECURE_HSTS_PRELOAD: bool = False

    SESSION_COOKIE_SECURE: bool = Field(
        default=False,
        description='Only send session cookie over HTTPS'
    )

    CSRF_COOKIE_SECURE: bool = Field(
        default=False,
        description='Only send CSRF cookie over HTTPS'
    )

    X_FRAME_OPTIONS: str = 'DENY'
    SECURE_CONTENT_TYPE_NOSNIFF: bool = True
    SECURE_BROWSER_XSS_FILTER: bool = True

    # ============================================================================
    # REST FRAMEWORK
    # ============================================================================

    REST_FRAMEWORK_DEFAULT_RENDERER_CLASSES: list[str] = Field(
        default=[
            'rest_framework.renderers.JSONRenderer',
            'rest_framework.renderers.BrowsableAPIRenderer',
        ]
    )

    # ============================================================================
    # EXTERNAL SERVICES (Supabase, etc.)
    # ============================================================================

    SUPABASE_URL: Optional[str] = Field(default=None)
    SUPABASE_ANON_KEY: Optional[str] = Field(default=None)
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = Field(default=None)

    # ============================================================================
    # LOGGING CONFIGURATION
    # ============================================================================

    LOG_LEVEL: str = Field(
        default='INFO',
        description='Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL'
    )

    # ============================================================================
    # DERIVED SETTINGS
    # ============================================================================

    @property
    def TEMPLATES(self) -> list[dict]:
        """Template configuration."""
        return [
            {
                'BACKEND': 'django.template.backends.django.DjangoTemplates',
                'DIRS': [str(BASE_DIR / 'templates')],
                'APP_DIRS': True,
                'OPTIONS': {
                    'context_processors': [
                        'django.template.context_processors.request',
                        'django.contrib.auth.context_processors.auth',
                        'django.contrib.messages.context_processors.messages',
                    ],
                },
            },
        ]

    @property
    def DATABASES(self) -> dict:
        """Database configuration from DATABASE_URL."""
        import dj_database_url

        db_config = dj_database_url.config(
            default=self.DATABASE_URL,
            conn_max_age=self.DATABASE_CONN_MAX_AGE,
            conn_health_checks=True,
        )

        # Add WAL mode for SQLite
        if 'sqlite' in self.DATABASE_URL:
            db_config['OPTIONS'] = {
                'timeout': 60,
                'init_command': 'PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL; PRAGMA cache_size=-64000;',
            }

        return {'default': db_config}

    @property
    def LOGGING(self) -> dict:
        """Logging configuration."""
        return {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'verbose': {
                    'format': '[{levelname}] {asctime} {name} {message}',
                    'style': '{',
                    'datefmt': '%Y-%m-%d %H:%M:%S',
                },
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'formatter': 'verbose',
                },
            },
            'root': {
                'handlers': ['console'],
                'level': self.LOG_LEVEL,
            },
            'loggers': {
                'django': {
                    'handlers': ['console'],
                    'level': self.LOG_LEVEL,
                    'propagate': False,
                },
                'apps': {
                    'handlers': ['console'],
                    'level': self.LOG_LEVEL,
                    'propagate': False,
                },
            },
        }


# Instantiate settings
settings = Settings()

# Export settings for Django to use
SECRET_KEY = settings.SECRET_KEY
DEBUG = settings.DEBUG
ALLOWED_HOSTS = settings.ALLOWED_HOSTS
INSTALLED_APPS = settings.INSTALLED_APPS
MIDDLEWARE = settings.MIDDLEWARE
DATABASES = settings.DATABASES
TEMPLATES = settings.TEMPLATES
LOGGING = settings.LOGGING

# Core settings
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

AUTH_USER_MODEL = settings.AUTH_USER_MODEL
LOGIN_URL = settings.LOGIN_URL
LOGIN_REDIRECT_URL = settings.LOGIN_REDIRECT_URL
LOGOUT_REDIRECT_URL = settings.LOGOUT_REDIRECT_URL

# Static/Media
STATIC_URL = settings.STATIC_URL
STATIC_ROOT = settings.STATIC_ROOT
MEDIA_URL = settings.MEDIA_URL
MEDIA_ROOT = settings.MEDIA_ROOT

# Internationalization
LANGUAGE_CODE = settings.LANGUAGE_CODE
TIME_ZONE = settings.TIME_ZONE
USE_I18N = settings.USE_I18N
USE_TZ = settings.USE_TZ
USE_THOUSAND_SEPARATOR = settings.USE_THOUSAND_SEPARATOR
THOUSAND_SEPARATOR = settings.THOUSAND_SEPARATOR
DECIMAL_SEPARATOR = settings.DECIMAL_SEPARATOR
NUMBER_GROUPING = settings.NUMBER_GROUPING

# URLs
ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'

# Security (from settings)
SECURE_SSL_REDIRECT = settings.SECURE_SSL_REDIRECT
SECURE_HSTS_SECONDS = settings.SECURE_HSTS_SECONDS
SECURE_HSTS_INCLUDE_SUBDOMAINS = settings.SECURE_HSTS_INCLUDE_SUBDOMAINS
SECURE_HSTS_PRELOAD = settings.SECURE_HSTS_PRELOAD
SESSION_COOKIE_SECURE = settings.SESSION_COOKIE_SECURE
CSRF_COOKIE_SECURE = settings.CSRF_COOKIE_SECURE
X_FRAME_OPTIONS = settings.X_FRAME_OPTIONS
SECURE_CONTENT_TYPE_NOSNIFF = settings.SECURE_CONTENT_TYPE_NOSNIFF
SECURE_BROWSER_XSS_FILTER = settings.SECURE_BROWSER_XSS_FILTER

# Formats
FORMAT_MODULE_PATH = [
    'config.formats',
    'apps.core.formats',
]

# ============================================================================
# REST FRAMEWORK CONFIGURATION
# ============================================================================

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
    },
}

# ============================================================================
# SPECTACULAR/OpenAPI CONFIGURATION
# ============================================================================

SPECTACULAR_SETTINGS = {
    'TITLE': 'A.RISK ERM API',
    'DESCRIPTION': 'Enterprise Risk Management API with comprehensive risk analysis',
    'VERSION': '1.0.0',
    'SERVE_PERMISSIONS': ['rest_framework.permissions.IsAuthenticated'],
    'SERVE_INCLUDE_SCHEMA': False,
    'SCHEMA_PATH_PREFIX': r'/api/v1',
    'SECURITY_DEFINITIONS': {
        'basicAuth': {
            'type': 'http',
            'scheme': 'basic',
        },
        'sessionAuth': {
            'type': 'apiKey',
            'in': 'cookie',
            'name': 'sessionid',
        },
    },
    'TAGS': [
        {'name': 'users', 'description': 'User management and authentication'},
        {'name': 'organizations', 'description': 'Organization/Cooperative management'},
        {'name': 'roles', 'description': 'Role and permission management'},
        {'name': 'risks', 'description': 'Risk management and assessment'},
        {'name': 'credit-operations', 'description': 'Credit operations and portfolio'},
        {'name': 'customers', 'description': 'Customer/Member management'},
    ],
}
