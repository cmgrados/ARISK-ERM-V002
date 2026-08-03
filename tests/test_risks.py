"""Tests for risks app."""

import pytest
from tests.factories import RiskFactory, OrganizationFactory


@pytest.mark.django_db
@pytest.mark.unit
class TestRiskModel:
    """Test Risk model."""

    def test_create_risk(self):
        """Test creating a risk."""
        risk = RiskFactory(name='Market Risk')
        assert risk.pk is not None
        assert risk.name == 'Market Risk'
        assert risk.status == 'active'

    def test_risk_string_representation(self):
        """Test risk __str__ method."""
        risk = RiskFactory(name='Operational Risk')
        assert 'Operational Risk' in str(risk)

    def test_risk_organization_relationship(self):
        """Test risk organization relationship."""
        org = OrganizationFactory(name='Bank XYZ')
        risk = RiskFactory(organization=org)
        assert risk.organization == org

    def test_risk_status_choices(self):
        """Test risk status field."""
        risk_active = RiskFactory(status='active')
        assert risk_active.status == 'active'

    def test_multiple_risks_in_organization(self):
        """Test multiple risks in same organization."""
        org = OrganizationFactory()
        risks = RiskFactory.create_batch(3, organization=org)
        assert len(risks) == 3
        assert all(risk.organization == org for risk in risks)


@pytest.mark.django_db
@pytest.mark.integration
class TestRiskQueryOptimization:
    """Test risk queries for N+1 optimization."""

    def test_get_all_risks_for_organization(self):
        """Test fetching all risks for an organization."""
        org = OrganizationFactory()
        RiskFactory.create_batch(5, organization=org)

        # This should ideally use select_related or prefetch_related
        risks = org.risk_set.all()
        assert risks.count() == 5

    def test_risk_filtering(self):
        """Test filtering risks by status."""
        org = OrganizationFactory()
        RiskFactory.create_batch(3, organization=org, status='active')
        RiskFactory.create_batch(2, organization=org, status='inactive')

        active_risks = org.risk_set.filter(status='active')
        assert active_risks.count() == 3
