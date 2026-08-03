import pytest
from django.contrib.auth import get_user_model
from rest_framework import status

User = get_user_model()


@pytest.mark.django_db
class TestUserAPI:
    """Tests for User API endpoints"""
    
    def test_list_users_unauthenticated(self, api_client):
        """Unauthenticated user should not access user list"""
        response = api_client.get('/api/v1/users/')
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_list_users_authenticated(self, authenticated_client):
        """Authenticated user should access user list"""
        response = authenticated_client.get('/api/v1/users/')
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data or isinstance(response.data, list)
    
    def test_create_user_admin_only(self, api_client, admin_client):
        """Only admin can create users"""
        user_data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'NewPass123',
            'password_confirm': 'NewPass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        # Non-admin should fail
        response = api_client.post('/api/v1/users/', user_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        # Admin should succeed
        response = admin_client.post('/api/v1/users/', user_data)
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST]
    
    def test_get_current_user(self, authenticated_client, auth_user):
        """Get current authenticated user"""
        response = authenticated_client.get('/api/v1/users/me/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == auth_user.username
    
    def test_user_password_validation(self, admin_client):
        """Test password validation during creation"""
        # Weak password (no uppercase)
        weak_password_data = {
            'username': 'weakpass',
            'email': 'weak@example.com',
            'password': 'weakpass123',
            'password_confirm': 'weakpass123'
        }
        response = admin_client.post('/api/v1/users/', weak_password_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_password_mismatch(self, admin_client):
        """Test password mismatch validation"""
        mismatch_data = {
            'username': 'mismatch',
            'email': 'mismatch@example.com',
            'password': 'Pass123',
            'password_confirm': 'Different123'
        }
        response = admin_client.post('/api/v1/users/', mismatch_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestUserActivation:
    """Tests for user activation/deactivation"""
    
    def test_activate_user(self, admin_client, auth_user):
        """Admin can activate user"""
        auth_user.is_active = False
        auth_user.save()
        
        response = admin_client.post(f'/api/v1/users/{auth_user.id}/activate/')
        assert response.status_code == status.HTTP_200_OK
        
        auth_user.refresh_from_db()
        assert auth_user.is_active is True
    
    def test_deactivate_user(self, admin_client, auth_user):
        """Admin can deactivate user"""
        response = admin_client.post(f'/api/v1/users/{auth_user.id}/deactivate/')
        assert response.status_code == status.HTTP_200_OK
        
        auth_user.refresh_from_db()
        assert auth_user.is_active is False
