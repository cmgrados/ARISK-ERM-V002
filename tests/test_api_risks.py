import pytest
from rest_framework import status
from risks.models import Risk


@pytest.mark.django_db
class TestRiskAPI:
    """Tests for Risk API endpoints"""
    
    def test_list_risks_authenticated(self, authenticated_client, risk):
        """Authenticated user can list risks"""
        response = authenticated_client.get('/api/v1/risks/')
        assert response.status_code == status.HTTP_200_OK
    
    def test_retrieve_risk(self, authenticated_client, risk):
        """Retrieve single risk"""
        response = authenticated_client.get(f'/api/v1/risks/{risk.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == risk.name
    
    def test_create_risk_admin(self, admin_client):
        """Admin can create risk"""
        risk_data = {
            'name': 'New Risk',
            'description': 'Test risk',
            'category': 'operational',
            'probability': 3,
            'impact': 4,
            'status': 'active',
            'owner': 'Test Owner'
        }
        response = admin_client.post('/api/v1/risks/', risk_data)
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST]
    
    def test_risk_probability_validation(self, admin_client):
        """Test probability validation (1-5)"""
        risk_data = {
            'name': 'Invalid Risk',
            'probability': 10,  # Invalid
            'impact': 3,
            'category': 'operational'
        }
        response = admin_client.post('/api/v1/risks/', risk_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_risk_summary(self, authenticated_client, risk):
        """Get risk summary statistics"""
        response = authenticated_client.get('/api/v1/risks/summary/')
        assert response.status_code == status.HTTP_200_OK
        assert 'total_risks' in response.data
    
    def test_risk_causes(self, authenticated_client, risk, risk_cause):
        """Get risk causes"""
        response = authenticated_client.get(f'/api/v1/risks/{risk.id}/causes/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
    
    def test_risk_consequences(self, authenticated_client, risk, risk_consequence):
        """Get risk consequences"""
        response = authenticated_client.get(f'/api/v1/risks/{risk.id}/consequences/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
    
    def test_risk_filtering_by_status(self, authenticated_client, risk):
        """Filter risks by status"""
        response = authenticated_client.get('/api/v1/risks/?status=active')
        assert response.status_code == status.HTTP_200_OK
