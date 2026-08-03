import pytest
from apps.users.serializers import UserCreateSerializer, UserPasswordSerializer
from apps.risks.serializers import RiskDetailSerializer
from apps.credit_risk.serializers import CustomerSerializer
from decimal import Decimal


@pytest.mark.django_db
class TestUserSerializers:
    """Tests for User serializers"""
    
    def test_user_create_serializer_valid(self):
        """Test valid user creation"""
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'ValidPass123',
            'password_confirm': 'ValidPass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        serializer = UserCreateSerializer(data=data)
        assert serializer.is_valid()
    
    def test_user_create_serializer_weak_password(self):
        """Test weak password validation"""
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'weakpass',  # No uppercase, no digit
            'password_confirm': 'weakpass'
        }
        serializer = UserCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'password' in serializer.errors
    
    def test_user_create_serializer_password_mismatch(self):
        """Test password mismatch"""
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'ValidPass123',
            'password_confirm': 'DifferentPass123'
        }
        serializer = UserCreateSerializer(data=data)
        assert not serializer.is_valid()


@pytest.mark.django_db
class TestRiskSerializers:
    """Tests for Risk serializers"""
    
    def test_risk_detail_serializer(self, risk):
        """Test risk detail serializer"""
        serializer = RiskDetailSerializer(risk)
        data = serializer.data
        assert data['name'] == risk.name
        assert data['probability_display'] == risk.get_probability_display()
    
    def test_risk_probability_validation(self):
        """Test probability validation in serializer"""
        data = {
            'name': 'Invalid Risk',
            'probability': 10,  # Invalid
            'impact': 3,
            'category': 'operational'
        }
        from apps.risks.serializers import RiskCreateUpdateSerializer
        serializer = RiskCreateUpdateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'probability' in serializer.errors


@pytest.mark.django_db
class TestCreditRiskSerializers:
    """Tests for Credit Risk serializers"""
    
    def test_customer_serializer_valid_dni(self):
        """Test valid DNI format"""
        data = {
            'name': 'Test Customer',
            'dni': '12345678',  # Valid: 8 digits
            'email': 'test@example.com'
        }
        serializer = CustomerSerializer(data=data)
        assert serializer.is_valid()
    
    def test_customer_serializer_invalid_dni(self):
        """Test invalid DNI format"""
        data = {
            'name': 'Test Customer',
            'dni': 'invalid',  # Invalid
            'email': 'test@example.com'
        }
        serializer = CustomerSerializer(data=data)
        assert not serializer.is_valid()
        assert 'dni' in serializer.errors
    
    def test_customer_serializer_invalid_ruc(self):
        """Test invalid RUC format"""
        data = {
            'name': 'Test Customer',
            'dni': '12345678',
            'ruc': 'invalid',  # Must be 11 digits
            'email': 'test@example.com'
        }
        serializer = CustomerSerializer(data=data)
        assert not serializer.is_valid()
        assert 'ruc' in serializer.errors
