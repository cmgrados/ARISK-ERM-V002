"""API tests for risks app."""

import pytest
from rest_framework.test import APIClient
from rest_framework import status
from tests.factories import (
    RiskFactory, ActiveRiskFactory, OrganizationFactory,
    AdminUserFactory, UserFactory
)


@pytest.mark.django_db
@pytest.mark.integration
class TestRiskAPI:
    """Test Risk API endpoints."""

    def setup_method(self):
        """Setup test client."""
        self.client = APIClient()
        self.admin = AdminUserFactory()
        self.user = UserFactory()

    def test_risk_list_authenticated(self):
        """Authenticated users can list risks."""
        self.client.force_authenticate(user=self.user)
        risk = RiskFactory()

        response = self.client.get('/api/v1/risks/')

        assert response.status_code == status.HTTP_200_OK

    def test_risk_list_unauthenticated(self):
        """Unauthenticated users cannot list risks."""
        response = self.client.get('/api/v1/risks/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_risk_create_admin_only(self):
        """Only admins can create risks."""
        self.client.force_authenticate(user=self.user)

        response = self.client.post('/api/v1/risks/', {'name': 'Test Risk'})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_risk_retrieve(self):
        """Users can retrieve risk details."""
        self.client.force_authenticate(user=self.user)
        risk = RiskFactory(name='Market Risk')

        response = self.client.get(f'/api/v1/risks/{risk.id}/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Market Risk'

    def test_risk_filter_by_category(self):
        """Can filter risks by category."""
        self.client.force_authenticate(user=self.user)
        RiskFactory(category='OPERATIONAL')
        RiskFactory(category='TECHNOLOGICAL')

        response = self.client.get('/api/v1/risks/?category=OPERATIONAL')

        assert response.status_code == status.HTTP_200_OK

    def test_risk_summary_endpoint(self):
        """Risk summary endpoint works."""
        self.client.force_authenticate(user=self.user)
        ActiveRiskFactory.create_batch(3)
        RiskFactory.create_batch(2, criticallity='HIGH')

        response = self.client.get('/api/v1/risks/summary/')

        assert response.status_code == status.HTTP_200_OK
        assert 'total_risks' in response.data

    def test_risk_causes_endpoint(self):
        """Can retrieve risk causes."""
        self.client.force_authenticate(user=self.user)
        risk = RiskFactory()

        response = self.client.get(f'/api/v1/risks/{risk.id}/causes/')

        assert response.status_code == status.HTTP_200_OK

    def test_risk_consequences_endpoint(self):
        """Can retrieve risk consequences."""
        self.client.force_authenticate(user=self.user)
        risk = RiskFactory()

        response = self.client.get(f'/api/v1/risks/{risk.id}/consequences/')

        assert response.status_code == status.HTTP_200_OK

    def test_risk_assessments_endpoint(self):
        """Can retrieve risk assessments."""
        self.client.force_authenticate(user=self.user)
        risk = RiskFactory()

        response = self.client.get(f'/api/v1/risks/{risk.id}/assessments/')

        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
@pytest.mark.integration
class TestProbabilityScaleAPI:
    """Test ProbabilityScale API endpoints."""

    def setup_method(self):
        """Setup test client."""
        self.client = APIClient()
        self.user = UserFactory()

    def test_probability_scale_list(self):
        """Can list probability scales."""
        self.client.force_authenticate(user=self.user)

        response = self.client.get('/api/v1/probability-scales/')

        assert response.status_code == status.HTTP_200_OK

    def test_probability_scale_readonly(self):
        """Probability scales are read-only."""
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            '/api/v1/probability-scales/',
            {'name': 'New Scale', 'value': 1}
        )

        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_405_METHOD_NOT_ALLOWED]


@pytest.mark.django_db
@pytest.mark.integration
class TestImpactScaleAPI:
    """Test ImpactScale API endpoints."""

    def setup_method(self):
        """Setup test client."""
        self.client = APIClient()
        self.user = UserFactory()

    def test_impact_scale_list(self):
        """Can list impact scales."""
        self.client.force_authenticate(user=self.user)

        response = self.client.get('/api/v1/impact-scales/')

        assert response.status_code == status.HTTP_200_OK

    def test_impact_scale_readonly(self):
        """Impact scales are read-only."""
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            '/api/v1/impact-scales/',
            {'name': 'New Scale', 'value': 1}
        )

        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_405_METHOD_NOT_ALLOWED]
