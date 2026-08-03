from rest_framework import serializers
from credit_risk.models import Customer, CreditOperation
from decimal import Decimal
from typing import Any, Dict


class CustomerSerializer(serializers.ModelSerializer):
    """Customer information"""
    
    class Meta:
        model = Customer
        fields = ['id', 'name', 'dni', 'ruc', 'email', 'phone', 'address', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def validate_dni(self, value: str) -> str:
        if not (len(value) == 8 and value.isdigit()):
            raise serializers.ValidationError("DNI must be 8 digits")
        return value
    
    def validate_ruc(self, value: str) -> str:
        if value and not (len(value) == 11 and value.isdigit()):
            raise serializers.ValidationError("RUC must be 11 digits")
        return value


class CreditOperationListSerializer(serializers.ModelSerializer):
    """Lightweight credit operation list"""
    
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    
    class Meta:
        model = CreditOperation
        fields = ['id', 'customer', 'customer_name', 'amount', 'currency', 'status', 'created_at']
        read_only_fields = ['id', 'created_at']


class CreditOperationDetailSerializer(serializers.ModelSerializer):
    """Detailed credit operation"""
    
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    portfolio_status = serializers.SerializerMethodField()
    risk_level = serializers.SerializerMethodField()
    
    class Meta:
        model = CreditOperation
        fields = ['id', 'customer', 'customer_name', 'amount', 'currency',
                 'disbursement_date', 'maturity_date', 'interest_rate',
                 'status', 'days_past_due', 'portfolio_status', 'risk_level',
                 'pd', 'lgd', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_portfolio_status(self, obj: CreditOperation) -> str:
        if obj.days_past_due > 90:
            return "high_risk"
        elif obj.days_past_due > 30:
            return "medium_risk"
        elif obj.days_past_due > 0:
            return "low_risk"
        return "current"
    
    def get_risk_level(self, obj: CreditOperation) -> str:
        expected_loss = (obj.amount * (obj.pd or Decimal('0.01')) * (obj.lgd or Decimal('0.5')))
        if expected_loss > obj.amount * Decimal('0.1'):
            return "high"
        elif expected_loss > obj.amount * Decimal('0.05'):
            return "medium"
        return "low"


class CreditOperationCreateSerializer(serializers.ModelSerializer):
    """Create credit operations"""
    
    def validate_amount(self, value: Decimal) -> Decimal:
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive")
        return value
    
    def validate_interest_rate(self, value: Decimal) -> Decimal:
        if not (0 <= value <= 100):
            raise serializers.ValidationError("Interest rate must be between 0 and 100")
        return value
    
    def validate_pd(self, value: Decimal) -> Decimal:
        if not (0 <= value <= 1):
            raise serializers.ValidationError("PD must be between 0 and 1")
        return value
    
    def validate_lgd(self, value: Decimal) -> Decimal:
        if not (0 <= value <= 1):
            raise serializers.ValidationError("LGD must be between 0 and 1")
        return value
    
    class Meta:
        model = CreditOperation
        fields = ['customer', 'amount', 'currency', 'disbursement_date', 'maturity_date',
                 'interest_rate', 'status', 'pd', 'lgd']


class CreditRiskMetricsSerializer(serializers.Serializer):
    """Credit risk metrics"""
    
    total_portfolio = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_loans = serializers.IntegerField()
    average_exposure = serializers.DecimalField(max_digits=15, decimal_places=2)
    overdue_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    expected_loss = serializers.DecimalField(max_digits=15, decimal_places=4)
    risk_concentration = serializers.DecimalField(max_digits=5, decimal_places=2)
