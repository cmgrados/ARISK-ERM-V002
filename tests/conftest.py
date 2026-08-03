import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from decimal import Decimal

from risks.models import Risk, RiskCause, RiskConsequence, RiskAssessment
from credit_risk.models import Customer, CreditOperation
from django.utils import timezone

User = get_user_model()


@pytest.fixture
def api_client():
    """Authenticated API client"""
    return APIClient()


@pytest.fixture
def auth_user(db):
    """Create authenticated user"""
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='TestPass123'
    )
    return user


@pytest.fixture
def auth_admin(db):
    """Create authenticated admin user"""
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='AdminPass123'
    )
    return admin


@pytest.fixture
def authenticated_client(api_client, auth_user):
    """API client with authenticated user"""
    api_client.force_authenticate(user=auth_user)
    return api_client


@pytest.fixture
def admin_client(api_client, auth_admin):
    """API client with admin user"""
    api_client.force_authenticate(user=auth_admin)
    return api_client


@pytest.fixture
def customer(db):
    """Create test customer"""
    return Customer.objects.create(
        name='Test Customer',
        dni='12345678',
        email='customer@example.com',
        phone='+51999999999',
        address='Test Street 123'
    )


@pytest.fixture
def credit_operation(db, customer):
    """Create test credit operation"""
    return CreditOperation.objects.create(
        customer=customer,
        amount=Decimal('10000.00'),
        currency='PEN',
        disbursement_date=timezone.now().date(),
        maturity_date=(timezone.now() + timezone.timedelta(days=365)).date(),
        interest_rate=Decimal('8.50'),
        status='active',
        pd=Decimal('0.05'),
        lgd=Decimal('0.40')
    )


@pytest.fixture
def risk(db):
    """Create test risk"""
    return Risk.objects.create(
        name='Test Risk',
        description='Test risk description',
        category='operational',
        probability=3,
        impact=4,
        status='active',
        owner='Test Owner'
    )


@pytest.fixture
def risk_cause(db, risk):
    """Create test risk cause"""
    return RiskCause.objects.create(
        risk=risk,
        description='Test cause',
        likelihood=2
    )


@pytest.fixture
def risk_consequence(db, risk):
    """Create test risk consequence"""
    return RiskConsequence.objects.create(
        risk=risk,
        description='Test consequence',
        severity=4
    )


@pytest.fixture
def risk_assessment(db, risk, auth_user):
    """Create test risk assessment"""
    return RiskAssessment.objects.create(
        risk=risk,
        assessment_date=timezone.now().date(),
        probability=3,
        impact=4,
        assessor=auth_user
    )
