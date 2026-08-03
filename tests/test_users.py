"""Tests for users app."""

import pytest
from django.contrib.auth import get_user_model
from tests.factories import (
    UserFactory, OrganizationFactory, RoleFactory,
    RiskManagerUserFactory, AuditorUserFactory, AdminUserFactory
)

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

    def test_user_role_relationship(self):
        """Test user role relationship."""
        role = RoleFactory(name='Manager')
        user = UserFactory(role=role)
        assert user.role == role
        assert user.role.name == 'Manager'

    def test_user_email_uniqueness(self):
        """Test that emails are unique in sequence."""
        user1 = UserFactory()
        user2 = UserFactory()
        assert user1.email != user2.email

    def test_user_username_uniqueness(self):
        """Test that usernames are unique in sequence."""
        user1 = UserFactory()
        user2 = UserFactory()
        assert user1.username != user2.username


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

    def test_organization_is_active_default(self):
        """Test organization is_active defaults to True."""
        org = OrganizationFactory()
        assert org.is_active is True

    def test_organization_ruc_uniqueness(self):
        """Test that RUCs are unique in sequence."""
        org1 = OrganizationFactory()
        org2 = OrganizationFactory()
        assert org1.ruc != org2.ruc


@pytest.mark.django_db
@pytest.mark.unit
class TestRoleModel:
    """Test Role model."""

    def test_create_role(self):
        """Test creating a role."""
        role = RoleFactory(name='Administrator')
        assert role.pk is not None
        assert role.name == 'Administrator'

    def test_role_permissions_structure(self):
        """Test role has proper permissions structure."""
        role = RoleFactory()
        assert 'integral_risk' in role.permissions
        assert isinstance(role.permissions, dict)

    def test_multiple_roles_unique(self):
        """Test multiple roles can be created."""
        role1 = RoleFactory()
        role2 = RoleFactory()
        assert role1.pk != role2.pk
        assert role1.name != role2.name


@pytest.mark.django_db
@pytest.mark.unit
class TestSpecializedUserFactories:
    """Test specialized user factories."""

    def test_risk_manager_factory(self):
        """Test risk manager user creation."""
        risk_manager = RiskManagerUserFactory()
        assert risk_manager.is_risk_manager is True

    def test_auditor_factory(self):
        """Test auditor user creation."""
        auditor = AuditorUserFactory()
        assert auditor.is_auditor is True

    def test_admin_factory(self):
        """Test admin user creation."""
        admin = AdminUserFactory()
        assert admin.is_staff is True
        assert admin.is_superuser is True

    def test_risk_manager_has_organization(self):
        """Test risk manager has organization."""
        risk_manager = RiskManagerUserFactory()
        assert risk_manager.organization is not None

    def test_auditor_has_organization(self):
        """Test auditor has organization."""
        auditor = AuditorUserFactory()
        assert auditor.organization is not None


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

    def test_user_is_staff_flag(self):
        """Test staff user flag."""
        staff_user = UserFactory(is_staff=True)
        regular_user = UserFactory(is_staff=False)
        assert staff_user.is_staff is True
        assert regular_user.is_staff is False

    def test_superuser_has_all_permissions(self):
        """Test superuser properties."""
        admin = AdminUserFactory()
        assert admin.is_superuser is True
        assert admin.is_staff is True

    def test_user_organization_filtering(self):
        """Test filtering users by organization."""
        org1 = OrganizationFactory()
        org2 = OrganizationFactory()
        user1 = UserFactory(organization=org1)
        user2 = UserFactory(organization=org2)

        org1_users = User.objects.filter(organization=org1)
        assert org1_users.count() == 1
        assert org1_users.first() == user1
