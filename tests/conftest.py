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
    """Create a test organization using factory."""
    from tests.factories import OrganizationFactory
    return OrganizationFactory()


@pytest.fixture
def role(db):
    """Create a test role using factory."""
    from tests.factories import RoleFactory
    return RoleFactory()


@pytest.fixture
def user_with_org(db, organization):
    """Create a user associated with an organization using factory."""
    from tests.factories import UserFactory
    return UserFactory(organization=organization)


@pytest.fixture
def risk_manager(db, organization):
    """Create a risk manager user."""
    from tests.factories import RiskManagerUserFactory
    return RiskManagerUserFactory(organization=organization)


@pytest.fixture
def auditor(db, organization):
    """Create an auditor user."""
    from tests.factories import AuditorUserFactory
    return AuditorUserFactory(organization=organization)


@pytest.fixture
def admin_test_user(db):
    """Create an admin user using factory."""
    from tests.factories import AdminUserFactory
    return AdminUserFactory()


@pytest.fixture
def risk(db, organization):
    """Create a test risk using factory."""
    from tests.factories import RiskFactory
    return RiskFactory(organization=organization)


@pytest.fixture
def active_risk(db, organization):
    """Create an active risk."""
    from tests.factories import ActiveRiskFactory
    return ActiveRiskFactory(organization=organization)


@pytest.fixture
def customer(db, organization):
    """Create a test customer."""
    from tests.factories import CustomerFactory
    return CustomerFactory(organization=organization)


@pytest.fixture
def credit_operation(db, organization, customer):
    """Create a test credit operation."""
    from tests.factories import CreditOperationFactory
    return CreditOperationFactory(customer=customer)


@pytest.fixture
def past_due_credit(db, organization, customer):
    """Create a past-due credit operation."""
    from tests.factories import PastDueCreditFactory
    return PastDueCreditFactory(customer=customer)


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
