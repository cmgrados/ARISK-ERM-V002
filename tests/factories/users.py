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


class UserFactory(DjangoModelFactory):
    """Factory for User model."""

    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.Sequence(lambda n: f'user{n}@example.com')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    is_active = True

    @classmethod
    def create(cls, **kwargs):
        """Override create to handle password properly."""
        password = kwargs.pop('password', 'testpass123456')
        obj = super().create(**kwargs)
        obj.set_password(password)
        obj.save()
        return obj


class AdminUserFactory(UserFactory):
    """Factory for admin User."""

    is_staff = True
    is_superuser = True
