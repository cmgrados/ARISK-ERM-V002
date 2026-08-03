"""Factories for user models."""

import factory
from factory.django import DjangoModelFactory
from django.contrib.auth import get_user_model

User = get_user_model()


class OrganizationFactory(DjangoModelFactory):
    """Factory for Organization model."""

    class Meta:
        model = 'users.Organization'

    name = factory.Sequence(lambda n: f'Organization {n}')
    ruc = factory.Sequence(lambda n: f'{n:011d}')
    is_active = True


class RoleFactory(DjangoModelFactory):
    """Factory for Role model."""

    class Meta:
        model = 'users.Role'

    name = factory.Sequence(lambda n: f'Role {n}')
    description = factory.Faker('text', max_nb_chars=200)
    permissions = {
        'integral_risk': {'acceder': True, 'editar': True},
        'financial_planning': {'acceder': True},
        'strategic_planning': {'acceder': True},
    }


class UserFactory(DjangoModelFactory):
    """Factory for User model."""

    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.Sequence(lambda n: f'user{n}@example.com')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    is_active = True
    organization = factory.SubFactory(OrganizationFactory)
    role = factory.SubFactory(RoleFactory)
    is_risk_manager = False
    is_auditor = False

    @classmethod
    def create(cls, **kwargs):
        """Override create to handle password properly."""
        password = kwargs.pop('password', 'testpass123456')
        obj = super().create(**kwargs)
        obj.set_password(password)
        obj.save()
        return obj


class RiskManagerUserFactory(UserFactory):
    """Factory for risk manager user."""

    is_risk_manager = True


class AuditorUserFactory(UserFactory):
    """Factory for auditor user."""

    is_auditor = True


class AdminUserFactory(UserFactory):
    """Factory for admin User."""

    is_staff = True
    is_superuser = True
