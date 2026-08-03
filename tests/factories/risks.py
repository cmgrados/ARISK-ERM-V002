"""Factories for risk models."""

import factory
from factory.django import DjangoModelFactory


class RiskFactory(DjangoModelFactory):
    """Factory for Risk model."""

    class Meta:
        model = 'risks.Risk'

    name = factory.Sequence(lambda n: f'Risk {n}')
    description = factory.Faker('text')
    status = factory.Faker('random_element', elements=['active', 'inactive', 'mitigated'])
    organization = factory.SubFactory('tests.factories.users.OrganizationFactory')


class ActiveRiskFactory(RiskFactory):
    """Factory for active risk."""

    status = 'active'


class MitigatedRiskFactory(RiskFactory):
    """Factory for mitigated risk."""

    status = 'mitigated'


class InactiveRiskFactory(RiskFactory):
    """Factory for inactive risk."""

    status = 'inactive'
