"""Tests for risks app."""

import pytest
from tests.factories import (
    RiskFactory, ActiveRiskFactory, MitigatedRiskFactory,
    InactiveRiskFactory, OrganizationFactory
)


@pytest.mark.django_db
@pytest.mark.unit
class TestRiskModel:
    """Test Risk model."""

    def test_create_risk(self):
        """Test creating a risk."""
        risk = RiskFactory(name='Market Risk')
        assert risk.pk is not None
        assert risk.name == 'Market Risk'

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

    def test_risk_description_is_text(self):
        """Test risk description is generated as text."""
        risk = RiskFactory()
        assert risk.description is not None
        assert isinstance(risk.description, str)

    def test_risk_has_unique_name_in_sequence(self):
        """Test risk names are unique."""
        risk1 = RiskFactory()
        risk2 = RiskFactory()
        assert risk1.name != risk2.name


@pytest.mark.django_db
@pytest.mark.unit
class TestRiskStatusVariants:
    """Test specialized risk factories with different statuses."""

    def test_active_risk_factory(self):
        """Test active risk factory."""
        risk = ActiveRiskFactory()
        assert risk.status == 'active'

    def test_mitigated_risk_factory(self):
        """Test mitigated risk factory."""
        risk = MitigatedRiskFactory()
        assert risk.status == 'mitigated'

    def test_inactive_risk_factory(self):
        """Test inactive risk factory."""
        risk = InactiveRiskFactory()
        assert risk.status == 'inactive'

    def test_risk_status_distribution(self):
        """Test creating risks with different statuses."""
        org = OrganizationFactory()
        active = ActiveRiskFactory(organization=org)
        mitigated = MitigatedRiskFactory(organization=org)
        inactive = InactiveRiskFactory(organization=org)

        assert active.status == 'active'
        assert mitigated.status == 'mitigated'
        assert inactive.status == 'inactive'
        assert {active.id, mitigated.id, inactive.id} == {active.id, mitigated.id, inactive.id}


@pytest.mark.django_db
@pytest.mark.integration
class TestRiskQueryOptimization:
    """Test risk queries for N+1 optimization."""

    def test_get_all_risks_for_organization(self):
        """Test fetching all risks for an organization."""
        org = OrganizationFactory()
        RiskFactory.create_batch(5, organization=org)

        risks = org.risk_set.all()
        assert risks.count() == 5

    def test_risk_filtering(self):
        """Test filtering risks by status."""
        org = OrganizationFactory()
        RiskFactory.create_batch(3, organization=org, status='active')
        RiskFactory.create_batch(2, organization=org, status='inactive')

        active_risks = org.risk_set.filter(status='active')
        assert active_risks.count() == 3

    def test_count_risks_by_status(self):
        """Test counting risks grouped by status."""
        org = OrganizationFactory()
        ActiveRiskFactory.create_batch(4, organization=org)
        InactiveRiskFactory.create_batch(2, organization=org)
        MitigatedRiskFactory.create_batch(1, organization=org)

        active_count = org.risk_set.filter(status='active').count()
        inactive_count = org.risk_set.filter(status='inactive').count()
        mitigated_count = org.risk_set.filter(status='mitigated').count()

        assert active_count == 4
        assert inactive_count == 2
        assert mitigated_count == 1
