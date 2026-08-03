"""Factories for credit risk models."""

import factory
from factory.django import DjangoModelFactory
from datetime import date, timedelta
from decimal import Decimal


class CustomerFactory(DjangoModelFactory):
    """Factory for Customer model."""

    class Meta:
        model = 'credit_risk.Customer'

    dni = factory.Sequence(lambda n: f'{n:08d}')
    name = factory.Faker('name')
    organization = factory.SubFactory('tests.factories.users.OrganizationFactory')


class CreditOperationFactory(DjangoModelFactory):
    """Factory for CreditOperation model."""

    class Meta:
        model = 'credit_risk.CreditOperation'

    customer = factory.SubFactory(CustomerFactory)
    operation_code = factory.Sequence(lambda n: f'OP-{n:06d}')
    product = None  # Optional FK
    product_name = factory.Faker('word')

    # Financial fields
    disbursement_date = factory.LazyFunction(lambda: date.today() - timedelta(days=30))
    original_amount = Decimal('100000.00')
    currency = 'PEN'

    balance = Decimal('95000.00')
    rate = Decimal('12.50')
    term = 60  # months
    payment_periodicity = 30  # days
    maturity_date = factory.LazyFunction(lambda: date.today() + timedelta(days=30*30))

    last_movement_date = factory.LazyFunction(lambda: date.today() - timedelta(days=1))
    credit_type = 'CONSUMO'

    generic_provision = Decimal('1000.00')
    specific_provision = Decimal('500.00')
    required_provision = Decimal('1500.00')
    established_provision = Decimal('1500.00')
    interest_receivable = Decimal('500.00')
    interest_suspended = Decimal('0.00')

    current_portfolio = Decimal('95000.00')
    past_due_portfolio = Decimal('0.00')


class PastDueCreditFactory(CreditOperationFactory):
    """Factory for past-due credit operation."""

    current_portfolio = Decimal('0.00')
    past_due_portfolio = Decimal('95000.00')
    generic_provision = Decimal('5000.00')
    specific_provision = Decimal('10000.00')
