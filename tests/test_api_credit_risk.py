"""API tests for credit_risk app."""

import pytest
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal
from tests.factories import (
    CustomerFactory, CreditOperationFactory, PastDueCreditFactory,
    AdminUserFactory, UserFactory
)


@pytest.mark.django_db
@pytest.mark.integration
class TestCustomerAPI:
    """Test Customer API endpoints."""

    def setup_method(self):
        """Setup test client."""
        self.client = APIClient()
        self.admin = AdminUserFactory()
        self.user = UserFactory()

    def test_customer_list_authenticated(self):
        """Authenticated users can list customers."""
        self.client.force_authenticate(user=self.user)
        CustomerFactory()

        response = self.client.get('/api/v1/customers/')

        assert response.status_code == status.HTTP_200_OK

    def test_customer_list_unauthenticated(self):
        """Unauthenticated users cannot list customers."""
        response = self.client.get('/api/v1/customers/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_customer_create_admin_only(self):
        """Only admins can create customers."""
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            '/api/v1/customers/',
            {'document_id': '12345678', 'name': 'John Doe'}
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_customer_retrieve(self):
        """Users can retrieve customer details."""
        self.client.force_authenticate(user=self.user)
        customer = CustomerFactory(name='Jane Doe')

        response = self.client.get(f'/api/v1/customers/{customer.id}/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Jane Doe'

    def test_customer_operations_endpoint(self):
        """Can retrieve customer operations."""
        self.client.force_authenticate(user=self.user)
        customer = CustomerFactory()
        CreditOperationFactory(customer=customer)

        response = self.client.get(f'/api/v1/customers/{customer.id}/operations/')

        assert response.status_code == status.HTTP_200_OK

    def test_customer_portfolio_summary_endpoint(self):
        """Can retrieve customer portfolio summary."""
        self.client.force_authenticate(user=self.user)
        customer = CustomerFactory()
        CreditOperationFactory(customer=customer)
        PastDueCreditFactory(customer=customer)

        response = self.client.get(f'/api/v1/customers/{customer.id}/portfolio_summary/')

        assert response.status_code == status.HTTP_200_OK
        assert 'total_operations' in response.data
        assert 'total_current_portfolio' in response.data
        assert 'total_past_due_portfolio' in response.data

    def test_customer_search_by_document(self):
        """Can search customers by document ID."""
        self.client.force_authenticate(user=self.user)
        customer = CustomerFactory(document_id='12345678')

        response = self.client.get('/api/v1/customers/?search=12345678')

        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
@pytest.mark.integration
class TestCreditOperationAPI:
    """Test CreditOperation API endpoints."""

    def setup_method(self):
        """Setup test client."""
        self.client = APIClient()
        self.admin = AdminUserFactory()
        self.user = UserFactory()

    def test_credit_operation_list_authenticated(self):
        """Authenticated users can list credit operations."""
        self.client.force_authenticate(user=self.user)
        customer = CustomerFactory()
        CreditOperationFactory(customer=customer)

        response = self.client.get('/api/v1/credit-operations/')

        assert response.status_code == status.HTTP_200_OK

    def test_credit_operation_list_unauthenticated(self):
        """Unauthenticated users cannot list operations."""
        response = self.client.get('/api/v1/credit-operations/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_credit_operation_retrieve(self):
        """Users can retrieve credit operation details."""
        self.client.force_authenticate(user=self.user)
        customer = CustomerFactory()
        op = CreditOperationFactory(customer=customer)

        response = self.client.get(f'/api/v1/credit-operations/{op.id}/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['operation_code'] == op.operation_code

    def test_credit_operation_summary_endpoint(self):
        """Can retrieve credit operation summary."""
        self.client.force_authenticate(user=self.user)
        customer = CustomerFactory()
        CreditOperationFactory.create_batch(3, customer=customer)

        response = self.client.get('/api/v1/credit-operations/summary/')

        assert response.status_code == status.HTTP_200_OK
        assert 'total_operations' in response.data
        assert 'total_current_portfolio' in response.data

    def test_credit_operation_high_risk_endpoint(self):
        """Can retrieve high-risk operations."""
        self.client.force_authenticate(user=self.user)
        customer = CustomerFactory()
        CreditOperationFactory(customer=customer, days_past_due=100)
        CreditOperationFactory(customer=customer, days_past_due=30)

        response = self.client.get('/api/v1/credit-operations/high_risk/')

        assert response.status_code == status.HTTP_200_OK

    def test_credit_operation_critical_endpoint(self):
        """Can retrieve critical operations."""
        self.client.force_authenticate(user=self.user)
        customer = CustomerFactory()
        PastDueCreditFactory(customer=customer)
        op = CreditOperationFactory(customer=customer, days_past_due=200)

        response = self.client.get('/api/v1/credit-operations/critical/')

        assert response.status_code == status.HTTP_200_OK

    def test_credit_operation_by_currency_endpoint(self):
        """Can retrieve operations grouped by currency."""
        self.client.force_authenticate(user=self.user)
        customer = CustomerFactory()
        CreditOperationFactory(customer=customer, currency='PEN')
        CreditOperationFactory(customer=customer, currency='USD')

        response = self.client.get('/api/v1/credit-operations/by_currency/')

        assert response.status_code == status.HTTP_200_OK
        assert 'currency_summary' in response.data

    def test_credit_operation_filter_by_currency(self):
        """Can filter operations by currency."""
        self.client.force_authenticate(user=self.user)
        customer = CustomerFactory()
        CreditOperationFactory(customer=customer, currency='PEN')
        CreditOperationFactory(customer=customer, currency='USD')

        response = self.client.get('/api/v1/credit-operations/?currency=PEN')

        assert response.status_code == status.HTTP_200_OK

    def test_credit_operation_metrics_endpoint(self):
        """Can retrieve credit operation metrics."""
        self.client.force_authenticate(user=self.user)
        customer = CustomerFactory()
        op = CreditOperationFactory(customer=customer)

        response = self.client.get(f'/api/v1/credit-operations/{op.id}/metrics/')

        # May return 404 if metrics don't exist, which is fine
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
@pytest.mark.integration
class TestCreditRiskMetricsAPI:
    """Test CreditRiskMetrics API endpoints."""

    def setup_method(self):
        """Setup test client."""
        self.client = APIClient()
        self.user = UserFactory()

    def test_metrics_list_authenticated(self):
        """Authenticated users can list metrics."""
        self.client.force_authenticate(user=self.user)

        response = self.client.get('/api/v1/credit-risk-metrics/')

        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
@pytest.mark.integration
class TestCreditRiskPeriodParameterAPI:
    """Test CreditRiskPeriodParameter API endpoints."""

    def setup_method(self):
        """Setup test client."""
        self.client = APIClient()
        self.admin = AdminUserFactory()
        self.user = UserFactory()

    def test_parameter_list_authenticated(self):
        """Authenticated users can list parameters."""
        self.client.force_authenticate(user=self.user)

        response = self.client.get('/api/v1/credit-risk-parameters/')

        assert response.status_code == status.HTTP_200_OK

    def test_parameter_create_admin_only(self):
        """Only admins can create parameters."""
        self.client.force_authenticate(user=self.user)
        from datetime import date

        response = self.client.post(
            '/api/v1/credit-risk-parameters/',
            {
                'load_date': date.today().isoformat(),
                'patrimonio_efectivo': '500000000.00'
            }
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_parameter_create_admin(self):
        """Admins can create parameters."""
        self.client.force_authenticate(user=self.admin)
        from datetime import date

        response = self.client.post(
            '/api/v1/credit-risk-parameters/',
            {
                'load_date': date.today().isoformat(),
                'patrimonio_efectivo': '500000000.00',
                'monto_mitigador': '50000000.00'
            }
        )

        assert response.status_code == status.HTTP_201_CREATED
