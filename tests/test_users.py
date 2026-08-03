"""Tests for users app."""

import pytest
from django.contrib.auth import get_user_model
from tests.factories import UserFactory, OrganizationFactory

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.unit
class TestUserModel:
    """Test User model."""

    def test_create_user(self):
        """Test creating a user."""
        user = UserFactory(username='testuser')
        assert user.pk is not None
        assert user.username == 'testuser'
        assert user.is_active is True

    def test_user_string_representation(self):
        """Test user __str__ method."""
        user = UserFactory(first_name='John', last_name='Doe')
        # Adjust based on actual User.__str__ implementation
        assert user.username in str(user) or user.email in str(user)

    def test_user_organization_relationship(self):
        """Test user organization relationship."""
        org = OrganizationFactory(name='Test Org')
        user = UserFactory(organization=org)
        assert user.organization == org
        assert user.organization.name == 'Test Org'

    def test_user_password_hashing(self):
        """Test that passwords are hashed."""
        user = UserFactory(password='mypassword123')
        assert user.check_password('mypassword123')
        assert not user.check_password('wrongpassword')

    def test_multiple_users_in_organization(self):
        """Test multiple users in same organization."""
        org = OrganizationFactory()
        user1 = UserFactory(organization=org)
        user2 = UserFactory(organization=org)
        assert user1.organization == user2.organization
        assert user1.pk != user2.pk


@pytest.mark.django_db
@pytest.mark.unit
class TestOrganizationModel:
    """Test Organization model."""

    def test_create_organization(self):
        """Test creating an organization."""
        org = OrganizationFactory(name='Acme Corp')
        assert org.pk is not None
        assert org.name == 'Acme Corp'

    def test_organization_string_representation(self):
        """Test organization __str__ method."""
        org = OrganizationFactory(name='Test Organization')
        assert 'Test Organization' in str(org)

    def test_organization_user_count(self):
        """Test counting users in organization."""
        org = OrganizationFactory()
        UserFactory.create_batch(5, organization=org)
        assert User.objects.filter(organization=org).count() == 5


@pytest.mark.django_db
@pytest.mark.integration
class TestUserAuthenticationFlow:
    """Test user authentication flows."""

    def test_user_login_with_email(self):
        """Test user can authenticate with credentials."""
        user = UserFactory(
            username='john',
            email='john@example.com',
            password='secure123'
        )
        assert user.check_password('secure123')
        # Can be used with authentication backend

    def test_user_is_staff_flag(self):
        """Test staff user flag."""
        staff_user = UserFactory(is_staff=True)
        regular_user = UserFactory(is_staff=False)
        assert staff_user.is_staff is True
        assert regular_user.is_staff is False
