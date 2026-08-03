"""API tests for users app."""

import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from tests.factories import (
    UserFactory, OrganizationFactory, RoleFactory,
    AdminUserFactory, RiskManagerUserFactory
)

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.integration
class TestOrganizationAPI:
    """Test Organization API endpoints."""

    def setup_method(self):
        """Setup test client and users."""
        self.client = APIClient()
        self.admin = AdminUserFactory()
        self.user = UserFactory()

    def test_organization_list_authenticated(self):
        """Authenticated users can list organizations."""
        self.client.force_authenticate(user=self.user)
        org = OrganizationFactory()

        response = self.client.get('/api/v1/organizations/')

        assert response.status_code == status.HTTP_200_OK
        assert org.name in str(response.data)

    def test_organization_list_unauthenticated(self):
        """Unauthenticated users cannot list organizations."""
        response = self.client.get('/api/v1/organizations/')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_organization_create_admin_only(self):
        """Only admins can create organizations."""
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            '/api/v1/organizations/',
            {'name': 'New Org', 'ruc': '12345678'}
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_organization_create_admin(self):
        """Admins can create organizations."""
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            '/api/v1/organizations/',
            {'name': 'New Org', 'ruc': '20123456789', 'is_active': True}
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'New Org'

    def test_organization_retrieve(self):
        """Users can retrieve organization details."""
        self.client.force_authenticate(user=self.user)
        org = OrganizationFactory(name='Test Org')

        response = self.client.get(f'/api/v1/organizations/{org.id}/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Test Org'

    def test_organization_filter_by_active(self):
        """Can filter organizations by is_active."""
        self.client.force_authenticate(user=self.user)
        OrganizationFactory(is_active=True)
        OrganizationFactory(is_active=False)

        response = self.client.get('/api/v1/organizations/?is_active=true')

        assert response.status_code == status.HTTP_200_OK
        assert all(org['is_active'] for org in response.data)


@pytest.mark.django_db
@pytest.mark.integration
class TestUserAPI:
    """Test User API endpoints."""

    def setup_method(self):
        """Setup test client and users."""
        self.client = APIClient()
        self.admin = AdminUserFactory()
        self.user = UserFactory()

    def test_user_list_authenticated(self):
        """Authenticated users can list users."""
        self.client.force_authenticate(user=self.user)

        response = self.client.get('/api/v1/users/')

        assert response.status_code == status.HTTP_200_OK

    def test_user_list_unauthenticated(self):
        """Unauthenticated users cannot list users."""
        response = self.client.get('/api/v1/users/')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_user_create_admin_only(self):
        """Only admins can create users."""
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            '/api/v1/users/',
            {
                'username': 'newuser',
                'email': 'newuser@test.com',
                'password': 'securepass123',
                'password_confirm': 'securepass123'
            }
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_user_create_admin(self):
        """Admins can create users."""
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            '/api/v1/users/',
            {
                'username': 'newuser',
                'email': 'newuser@test.com',
                'password': 'securepass123',
                'password_confirm': 'securepass123'
            }
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['username'] == 'newuser'

    def test_user_retrieve(self):
        """Users can retrieve their info."""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(f'/api/v1/users/{self.user.id}/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == self.user.username

    def test_user_me_endpoint(self):
        """Can retrieve current user info via /me endpoint."""
        self.client.force_authenticate(user=self.user)

        response = self.client.get('/api/v1/users/me/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == self.user.id

    def test_user_permissions_endpoint(self):
        """Can retrieve user permissions."""
        risk_manager = RiskManagerUserFactory()
        self.client.force_authenticate(user=risk_manager)

        response = self.client.get(f'/api/v1/users/{risk_manager.id}/permissions/')

        assert response.status_code == status.HTTP_200_OK
        assert 'integral_risk' in response.data or response.data['is_staff'] is not None

    def test_user_filter_by_organization(self):
        """Can filter users by organization."""
        self.client.force_authenticate(user=self.admin)
        org = OrganizationFactory()
        user1 = UserFactory(organization=org)
        user2 = UserFactory(organization=OrganizationFactory())

        response = self.client.get(f'/api/v1/users/?organization={org.id}')

        assert response.status_code == status.HTTP_200_OK
        # Should include users from this organization

    def test_user_filter_by_is_staff(self):
        """Can filter users by is_staff."""
        self.client.force_authenticate(user=self.admin)
        staff_user = UserFactory(is_staff=True)
        regular_user = UserFactory(is_staff=False)

        response = self.client.get('/api/v1/users/?is_staff=true')

        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
@pytest.mark.integration
class TestRoleAPI:
    """Test Role API endpoints."""

    def setup_method(self):
        """Setup test client and users."""
        self.client = APIClient()
        self.admin = AdminUserFactory()
        self.user = UserFactory()

    def test_role_list_authenticated(self):
        """Authenticated users can list roles."""
        self.client.force_authenticate(user=self.user)
        RoleFactory()

        response = self.client.get('/api/v1/roles/')

        assert response.status_code == status.HTTP_200_OK

    def test_role_list_unauthenticated(self):
        """Unauthenticated users cannot list roles."""
        response = self.client.get('/api/v1/roles/')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_role_create_admin_only(self):
        """Only admins can create roles."""
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            '/api/v1/roles/',
            {'name': 'Auditor', 'description': 'Audit role'}
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_role_create_admin(self):
        """Admins can create roles."""
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            '/api/v1/roles/',
            {
                'name': 'Auditor',
                'description': 'Audit role',
                'permissions': {'integral_risk': {'acceder': True}}
            }
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'Auditor'

    def test_role_retrieve(self):
        """Users can retrieve role details."""
        self.client.force_authenticate(user=self.user)
        role = RoleFactory(name='Manager')

        response = self.client.get(f'/api/v1/roles/{role.id}/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Manager'
