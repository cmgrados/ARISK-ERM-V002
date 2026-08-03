import pytest
from rest_framework import status
from decimal import Decimal


@pytest.mark.django_db
class TestCustomerAPI:
    """Tests for Customer API endpoints"""
    
    def test_list_customers(self, authenticated_client, customer):
        """Authenticated user can list customers"""
        response = authenticated_client.get('/api/v1/customers/')
        assert response.status_code == status.HTTP_200_OK
    
    def test_retrieve_customer(self, authenticated_client, customer):
        """Retrieve single customer"""
        response = authenticated_client.get(f'/api/v1/customers/{customer.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == customer.name
    
    def test_customer_operations(self, authenticated_client, customer, credit_operation):
        """Get customer operations"""
        response = authenticated_client.get(f'/api/v1/customers/{customer.id}/operations/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
    
    def test_customer_portfolio_summary(self, authenticated_client, customer, credit_operation):
        """Get customer portfolio summary"""
        response = authenticated_client.get(f'/api/v1/customers/{customer.id}/portfolio_summary/')
        assert response.status_code == status.HTTP_200_OK
        assert 'total_amount' in response.data
        assert response.data['customer_id'] == customer.id
    
    def test_customer_dni_validation(self, admin_client):
        """Test DNI validation"""
        customer_data = {
            'name': 'Invalid DNI',
            'dni': 'invalid',  # Must be 8 digits
            'email': 'test@example.com'
        }
        response = admin_client.post('/api/v1/customers/', customer_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestCreditOperationAPI:
    """Tests for Credit Operation API endpoints"""
    
    def test_list_operations(self, authenticated_client, credit_operation):
        """Authenticated user can list operations"""
        response = authenticated_client.get('/api/v1/credit-operations/')
        assert response.status_code == status.HTTP_200_OK
    
    def test_retrieve_operation(self, authenticated_client, credit_operation):
        """Retrieve single operation"""
        response = authenticated_client.get(f'/api/v1/credit-operations/{credit_operation.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['amount'] == str(credit_operation.amount)
    
    def test_operation_summary(self, authenticated_client, credit_operation):
        """Get credit operations summary"""
        response = authenticated_client.get('/api/v1/credit-operations/summary/')
        assert response.status_code == status.HTTP_200_OK
        assert 'total_portfolio' in response.data
        assert 'total_loans' in response.data
    
    def test_high_risk_operations(self, authenticated_client, db):
        """Get high risk operations (days_past_due > 30)"""
        from credit_risk.models import Customer, CreditOperation
        from django.utils import timezone
        from decimal import Decimal
        
        customer = Customer.objects.create(
            name='High Risk Customer',
            dni='87654321',
            email='high@example.com'
        )
        
        high_risk_op = CreditOperation.objects.create(
            customer=customer,
            amount=Decimal('5000.00'),
            days_past_due=45,
            currency='PEN',
            interest_rate=Decimal('8.50')
        )
        
        response = authenticated_client.get('/api/v1/credit-operations/high_risk/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
    
    def test_operations_by_currency(self, authenticated_client, credit_operation):
        """Get operations by currency"""
        response = authenticated_client.get('/api/v1/credit-operations/by_currency/')
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
    
    def test_amount_validation(self, admin_client, customer):
        """Test amount validation (must be positive)"""
        from django.utils import timezone
        
        operation_data = {
            'customer': customer.id,
            'amount': Decimal('-1000.00'),  # Invalid: negative
            'currency': 'PEN',
            'disbursement_date': timezone.now().date(),
            'maturity_date': timezone.now().date(),
            'interest_rate': Decimal('8.50')
        }
        response = admin_client.post('/api/v1/credit-operations/', operation_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_interest_rate_validation(self, admin_client, customer):
        """Test interest rate validation (0-100)"""
        from django.utils import timezone
        
        operation_data = {
            'customer': customer.id,
            'amount': Decimal('1000.00'),
            'currency': 'PEN',
            'disbursement_date': timezone.now().date(),
            'maturity_date': timezone.now().date(),
            'interest_rate': Decimal('150.00')  # Invalid: > 100
        }
        response = admin_client.post('/api/v1/credit-operations/', operation_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
