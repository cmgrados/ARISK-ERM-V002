"""Factories for risk models."""

import factory
from factory.django import DjangoModelFactory


class RiskFactory(DjangoModelFactory):
    """Factory for Risk model."""

    class Meta:
        model = 'risks.Risk'

    name = factory.Sequence(lambda n: f'Risk {n}')
    description = factory.Faker('text')
    status = 'active'
    organization = factory.SubFactory('tests.factories.users.OrganizationFactory')
