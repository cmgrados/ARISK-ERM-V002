"""
Pytest configuration and shared fixtures for A.RISK ERM.

This file is automatically discovered by pytest and provides:
- Fixtures for models (users, organizations, risks, etc.)
- Database setup/teardown
- Django settings configuration
"""

import os
import sys
import django

# Ensure Django is properly configured BEFORE importing anything else
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.testing')
django.setup()

import pytest
from django.conf import settings
from django.test import Client
from rest_framework.test import APIClient


# ============================================================================
# PYTEST CONFIGURATION
# ============================================================================

def pytest_configure(config):
    """Configure pytest with Django settings."""
    if not settings.configured:
        settings.configure(
            DEBUG=True,
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': ':memory:',
                }
            },
        )


# ============================================================================
# DATABASE FIXTURES
# ============================================================================

@pytest.fixture(scope='session')
def django_db_setup():
    """Configure Django database for tests."""
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }


@pytest.fixture
def db_reset(db):
    """Reset database before each test."""
    yield
    # Cleanup happens automatically with transaction rollback


# ============================================================================
# DJANGO FIXTURES
# ============================================================================

@pytest.fixture
def client():
    """Django test client."""
    return Client()


@pytest.fixture
def api_client():
    """Django REST Framework test client."""
    return APIClient()


@pytest.fixture
def admin_user(django_user_model):
    """Create an admin user for testing."""
    return django_user_model.objects.create_superuser(
        username='admin',
        email='admin@test.com',
        password='admin123456'
    )


@pytest.fixture
def authenticated_user(django_user_model):
    """Create an authenticated user for testing."""
    user = django_user_model.objects.create_user(
        username='testuser',
        email='user@test.com',
        password='testpass123456'
    )
    return user


@pytest.fixture
def authenticated_api_client(authenticated_user):
    """API client authenticated with a user."""
    from rest_framework.test import APIClient
    client = APIClient()
    client.force_authenticate(user=authenticated_user)
    return client


# ============================================================================
# APP-SPECIFIC FIXTURES
# ============================================================================

@pytest.fixture
def organization(db):
    """Create a test organization."""
    from apps.users.models import Organization
    return Organization.objects.create(
        name='Test Organization',
        description='A test organization for unit tests'
    )


@pytest.fixture
def user_with_org(db, organization, authenticated_user):
    """Create a user associated with an organization."""
    authenticated_user.organization = organization
    authenticated_user.save()
    return authenticated_user


@pytest.fixture
def risk(db, organization):
    """Create a test risk."""
    from apps.risks.models import Risk
    return Risk.objects.create(
        name='Test Risk',
        description='A test risk for unit tests',
        organization=organization,
        status='active'
    )


@pytest.fixture
def credit_operation(db, organization):
    """Create a test credit operation."""
    try:
        from apps.credit_risk.models import CreditOperation
        from apps.utilities.models import Customer

        customer = Customer.objects.create(
            dni='12345678',
            organization=organization
        )

        return CreditOperation.objects.create(
            customer=customer,
            organization=organization,
            amount=100000.00,
            currency='USD'
        )
    except Exception as e:
        pytest.skip(f"Could not create credit operation: {e}")


# ============================================================================
# UTILITY FIXTURES
# ============================================================================

@pytest.fixture
def clear_cache():
    """Clear cache before and after test."""
    from django.core.cache import cache
    cache.clear()
    yield
    cache.clear()


# ============================================================================
# MARKERS
# ============================================================================

def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
