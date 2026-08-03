"""Tests for credit_risk app."""

import pytest
from decimal import Decimal
from datetime import date, timedelta
from tests.factories import (
    CustomerFactory, CreditOperationFactory,
    PastDueCreditFactory, OrganizationFactory
)


@pytest.mark.django_db
@pytest.mark.unit
class TestCustomerModel:
    """Test Customer model."""

    def test_create_customer(self):
        """Test creating a customer."""
        customer = CustomerFactory(name='John Doe')
        assert customer.pk is not None
        assert customer.name == 'John Doe'

    def test_customer_dni_uniqueness(self):
        """Test customer DNI is unique in sequence."""
        customer1 = CustomerFactory()
        customer2 = CustomerFactory()
        assert customer1.dni != customer2.dni

    def test_customer_organization_relationship(self):
        """Test customer organization relationship."""
        org = OrganizationFactory(name='Bank XYZ')
        customer = CustomerFactory(organization=org)
        assert customer.organization == org

    def test_customer_string_representation(self):
        """Test customer __str__ method."""
        customer = CustomerFactory(name='Juan Pérez')
        assert 'Juan Pérez' in str(customer) or customer.name in str(customer)

    def test_customer_dni_format(self):
        """Test customer DNI has correct format."""
        customer = CustomerFactory()
        assert len(customer.dni) == 8
        assert customer.dni.isdigit()


@pytest.mark.django_db
@pytest.mark.unit
class TestCreditOperationModel:
    """Test CreditOperation model."""

    def test_create_credit_operation(self):
        """Test creating a credit operation."""
        credit_op = CreditOperationFactory(operation_code='OP-000001')
        assert credit_op.pk is not None
        assert credit_op.operation_code == 'OP-000001'

    def test_credit_operation_customer_relationship(self):
        """Test credit operation customer relationship."""
        customer = CustomerFactory(name='Carlos Mendez')
        credit_op = CreditOperationFactory(customer=customer)
        assert credit_op.customer == customer
        assert credit_op.customer.name == 'Carlos Mendez'

    def test_credit_operation_financial_fields(self):
        """Test credit operation financial fields."""
        credit_op = CreditOperationFactory()
        assert credit_op.original_amount == Decimal('100000.00')
        assert credit_op.balance == Decimal('95000.00')
        assert credit_op.rate == Decimal('12.50')
        assert isinstance(credit_op.original_amount, Decimal)

    def test_credit_operation_currency_default(self):
        """Test credit operation currency default."""
        credit_op = CreditOperationFactory()
        assert credit_op.currency in ['PEN', 'USD']

    def test_credit_operation_dates(self):
        """Test credit operation date fields."""
        credit_op = CreditOperationFactory()
        assert credit_op.disbursement_date is not None
        assert credit_op.maturity_date is not None
        assert credit_op.disbursement_date <= credit_op.maturity_date

    def test_credit_operation_provisions(self):
        """Test credit operation provision fields."""
        credit_op = CreditOperationFactory()
        assert isinstance(credit_op.generic_provision, Decimal)
        assert isinstance(credit_op.specific_provision, Decimal)
        assert credit_op.generic_provision >= 0
        assert credit_op.specific_provision >= 0

    def test_credit_operation_portfolio_fields(self):
        """Test credit operation portfolio fields."""
        credit_op = CreditOperationFactory()
        assert isinstance(credit_op.current_portfolio, Decimal)
        assert isinstance(credit_op.past_due_portfolio, Decimal)
        assert credit_op.current_portfolio >= 0
        assert credit_op.past_due_portfolio >= 0

    def test_multiple_credit_operations_for_customer(self):
        """Test multiple credit operations for same customer."""
        customer = CustomerFactory()
        credit_op1 = CreditOperationFactory(customer=customer)
        credit_op2 = CreditOperationFactory(customer=customer)

        customer_operations = customer.creditoperation_set.all()
        assert customer_operations.count() == 2
        assert credit_op1 in customer_operations
        assert credit_op2 in customer_operations


@pytest.mark.django_db
@pytest.mark.unit
class TestPastDueCreditOperation:
    """Test past-due credit operation scenario."""

    def test_past_due_credit_factory(self):
        """Test creating a past-due credit."""
        past_due = PastDueCreditFactory()
        assert past_due.pk is not None

    def test_past_due_credit_portfolio_status(self):
        """Test past-due credit has correct portfolio status."""
        past_due = PastDueCreditFactory()
        assert past_due.current_portfolio == Decimal('0.00')
        assert past_due.past_due_portfolio == Decimal('95000.00')

    def test_past_due_credit_high_provisions(self):
        """Test past-due credit has higher provisions."""
        normal_credit = CreditOperationFactory()
        past_due = PastDueCreditFactory()

        assert past_due.generic_provision > normal_credit.generic_provision
        assert past_due.specific_provision > normal_credit.specific_provision

    def test_distinguish_current_vs_past_due(self):
        """Test distinguishing current vs past-due credits."""
        customer = CustomerFactory()
        current = CreditOperationFactory(customer=customer)
        past_due = PastDueCreditFactory(customer=customer)

        current_ops = customer.creditoperation_set.filter(past_due_portfolio=Decimal('0.00'))
        overdue_ops = customer.creditoperation_set.filter(current_portfolio=Decimal('0.00'))

        assert current in current_ops
        assert past_due in overdue_ops


@pytest.mark.django_db
@pytest.mark.integration
class TestCreditOperationQueries:
    """Test credit operation queries."""

    def test_get_all_credits_for_customer(self):
        """Test fetching all credits for a customer."""
        customer = CustomerFactory()
        CreditOperationFactory.create_batch(5, customer=customer)

        operations = customer.creditoperation_set.all()
        assert operations.count() == 5

    def test_filter_by_currency(self):
        """Test filtering credit operations by currency."""
        customer = CustomerFactory()
        CreditOperationFactory.create_batch(3, customer=customer, currency='PEN')
        CreditOperationFactory.create_batch(2, customer=customer, currency='USD')

        pen_ops = customer.creditoperation_set.filter(currency='PEN')
        usd_ops = customer.creditoperation_set.filter(currency='USD')

        assert pen_ops.count() == 3
        assert usd_ops.count() == 2

    def test_credit_risk_portfolio_summary(self):
        """Test calculating portfolio summary for customer."""
        customer = CustomerFactory()
        current1 = CreditOperationFactory(
            customer=customer,
            current_portfolio=Decimal('50000.00'),
            past_due_portfolio=Decimal('0.00')
        )
        current2 = CreditOperationFactory(
            customer=customer,
            current_portfolio=Decimal('30000.00'),
            past_due_portfolio=Decimal('0.00')
        )
        past_due = PastDueCreditFactory(
            customer=customer,
            current_portfolio=Decimal('0.00'),
            past_due_portfolio=Decimal('20000.00')
        )

        operations = customer.creditoperation_set.all()
        assert operations.count() == 3

        total_current = sum(op.current_portfolio for op in operations)
        total_past_due = sum(op.past_due_portfolio for op in operations)

        assert total_current == Decimal('80000.00')
        assert total_past_due == Decimal('20000.00')

    def test_credits_by_organization(self):
        """Test retrieving credits by organization."""
        org1 = OrganizationFactory()
        org2 = OrganizationFactory()

        customer1 = CustomerFactory(organization=org1)
        customer2 = CustomerFactory(organization=org2)

        CreditOperationFactory.create_batch(3, customer=customer1)
        CreditOperationFactory.create_batch(2, customer=customer2)

        org1_customers = customer1.organization.customer_set.all()
        org2_customers = customer2.organization.customer_set.all()

        # Count credits for each organization
        org1_credit_count = sum(
            c.creditoperation_set.count() for c in org1_customers
        )
        org2_credit_count = sum(
            c.creditoperation_set.count() for c in org2_customers
        )

        assert org1_credit_count == 3
        assert org2_credit_count == 2

    def test_high_risk_credits_identification(self):
        """Test identifying high-risk credits (past-due with high provisions)."""
        customer = CustomerFactory()
        normal = CreditOperationFactory(customer=customer)
        high_risk = PastDueCreditFactory(customer=customer)

        # High-risk criteria: past_due_portfolio > 0 and provisions > 5000
        high_risk_ops = customer.creditoperation_set.filter(
            past_due_portfolio__gt=Decimal('0.00')
        ).filter(
            generic_provision__gte=Decimal('5000.00')
        )

        assert normal not in high_risk_ops
        assert high_risk in high_risk_ops
