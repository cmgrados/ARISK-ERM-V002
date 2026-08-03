"""Serializers for credit_risk app."""

from rest_framework import serializers
from decimal import Decimal
from .models import Customer, CreditOperation, CreditRiskMetrics, CreditRiskPeriodParameter


class CustomerSerializer(serializers.ModelSerializer):
    """Serializer for Customer model."""

    class Meta:
        model = Customer
        fields = [
            'id', 'document_id', 'external_id', 'name',
            'age', 'gender', 'birth_date',
            'address', 'district', 'province', 'department',
            'segment', 'economic_activity', 'zone'
        ]
        read_only_fields = ['id']

    def validate_document_id(self, value):
        """Validate document ID uniqueness."""
        qs = Customer.objects.filter(document_id=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Customer with this document ID already exists.")
        return value

    def validate_age(self, value):
        """Validate age is realistic."""
        if value and (value < 0 or value > 150):
            raise serializers.ValidationError("Age must be between 0 and 150.")
        return value


class CreditRiskMetricsSerializer(serializers.ModelSerializer):
    """Serializer for CreditRiskMetrics model."""

    class Meta:
        model = CreditRiskMetrics
        fields = [
            'id', 'operation', 'pd', 'ead', 'lgd', 'expected_loss'
        ]
        read_only_fields = ['id', 'expected_loss']

    def validate_pd(self, value):
        """Validate PD is between 0 and 100."""
        if not (Decimal('0') <= value <= Decimal('100')):
            raise serializers.ValidationError("PD must be between 0 and 100.")
        return value

    def validate_lgd(self, value):
        """Validate LGD is between 0 and 100."""
        if not (Decimal('0') <= value <= Decimal('100')):
            raise serializers.ValidationError("LGD must be between 0 and 100.")
        return value


class CreditOperationListSerializer(serializers.ModelSerializer):
    """Simplified serializer for CreditOperation list view."""

    customer_name = serializers.CharField(source='customer.name', read_only=True)
    portfolio_status = serializers.SerializerMethodField()
    risk_level = serializers.SerializerMethodField()

    class Meta:
        model = CreditOperation
        fields = [
            'id', 'operation_code', 'customer_name',
            'original_amount', 'balance', 'currency',
            'days_past_due', 'portfolio_status', 'risk_level',
            'load_date'
        ]
        read_only_fields = fields

    def get_portfolio_status(self, obj):
        """Determine portfolio status (vigente/vencido)."""
        if obj.past_due_portfolio > 0:
            return 'past_due'
        return 'current'

    def get_risk_level(self, obj):
        """Calculate risk level based on provisions and days past due."""
        if obj.days_past_due > 180:
            return 'critical'
        elif obj.days_past_due > 90:
            return 'high'
        elif obj.days_past_due > 30:
            return 'medium'
        return 'low'


class CreditOperationDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for CreditOperation model."""

    customer = CustomerSerializer(read_only=True)
    customer_id = serializers.IntegerField(write_only=True)
    metrics = CreditRiskMetricsSerializer(read_only=True)
    portfolio_status = serializers.SerializerMethodField()
    risk_level = serializers.SerializerMethodField()
    total_portfolio = serializers.SerializerMethodField()

    class Meta:
        model = CreditOperation
        fields = [
            'id', 'customer', 'customer_id',
            'operation_code', 'product', 'product_name',
            'disbursement_date', 'maturity_date', 'original_amount',
            'currency', 'balance', 'rate', 'term', 'payment_periodicity',
            'last_movement_date', 'credit_type',
            'generic_provision', 'specific_provision',
            'required_provision', 'established_provision',
            'interest_receivable', 'interest_suspended',
            'current_portfolio', 'past_due_portfolio',
            'refinanced_current', 'refinanced_past_due',
            'restructured_current', 'restructured_past_due',
            'judicial_portfolio',
            'agreement', 'advisor_code',
            'guarantee_type', 'guarantee_value',
            'agency', 'advisor',
            'bucket', 'days_past_due', 'sbs_classification',
            'is_refinanced', 'load_date',
            'portfolio_status', 'risk_level', 'total_portfolio',
            'metrics'
        ]
        read_only_fields = [
            'id', 'portfolio_status', 'risk_level', 'total_portfolio', 'metrics'
        ]

    def get_portfolio_status(self, obj):
        """Determine portfolio status."""
        if obj.past_due_portfolio > 0:
            return 'past_due'
        return 'current'

    def get_risk_level(self, obj):
        """Calculate risk level."""
        if obj.days_past_due > 180:
            return 'critical'
        elif obj.days_past_due > 90:
            return 'high'
        elif obj.days_past_due > 30:
            return 'medium'
        return 'low'

    def get_total_portfolio(self, obj):
        """Calculate total portfolio."""
        return str(
            obj.current_portfolio + obj.past_due_portfolio +
            obj.refinanced_current + obj.refinanced_past_due +
            obj.restructured_current + obj.restructured_past_due +
            obj.judicial_portfolio
        )

    def validate_balance(self, value):
        """Validate balance is non-negative."""
        if value < 0:
            raise serializers.ValidationError("Balance cannot be negative.")
        return value

    def validate_rate(self, value):
        """Validate rate is between 0 and 100."""
        if not (Decimal('0') <= value <= Decimal('100')):
            raise serializers.ValidationError("Rate must be between 0 and 100.")
        return value

    def validate_currency(self, value):
        """Validate currency is PEN or USD."""
        if value not in ['PEN', 'USD']:
            raise serializers.ValidationError("Currency must be PEN or USD.")
        return value


class CreditOperationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating credit operations."""

    class Meta:
        model = CreditOperation
        fields = [
            'customer', 'operation_code', 'product', 'product_name',
            'disbursement_date', 'maturity_date', 'original_amount',
            'currency', 'balance', 'rate', 'term', 'payment_periodicity',
            'credit_type', 'agency', 'advisor'
        ]

    def validate_currency(self, value):
        """Validate currency."""
        if value not in ['PEN', 'USD']:
            raise serializers.ValidationError("Currency must be PEN or USD.")
        return value


class CreditRiskPeriodParameterSerializer(serializers.ModelSerializer):
    """Serializer for CreditRiskPeriodParameter model."""

    class Meta:
        model = CreditRiskPeriodParameter
        fields = [
            'id', 'load_date', 'patrimonio_efectivo',
            'monto_mitigador', 'description'
        ]
        read_only_fields = ['id']

    def validate_patrimonio_efectivo(self, value):
        """Validate patrimonio is positive."""
        if value <= 0:
            raise serializers.ValidationError("Patrimonio must be positive.")
        return value

    def validate_monto_mitigador(self, value):
        """Validate monto is positive."""
        if value < 0:
            raise serializers.ValidationError("Monto must be non-negative.")
        return value


class CreditPortfolioSummarySerializer(serializers.Serializer):
    """Serializer for portfolio summary statistics."""

    total_customers = serializers.IntegerField()
    total_operations = serializers.IntegerField()
    total_current_portfolio = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_past_due_portfolio = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_provisions = serializers.DecimalField(max_digits=15, decimal_places=2)
    average_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    high_risk_operations = serializers.IntegerField()
    critical_operations = serializers.IntegerField()
