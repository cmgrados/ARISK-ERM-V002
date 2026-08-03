from rest_framework import serializers
from django.contrib.auth import get_user_model
from typing import Any, Dict, Optional

User = get_user_model()


class UserDetailSerializer(serializers.ModelSerializer):
    """Detailed user information with nested organization and role"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class UserListSerializer(serializers.ModelSerializer):
    """Lightweight user list view"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active']
        read_only_fields = ['id']


class UserCreateSerializer(serializers.ModelSerializer):
    """User creation with password validation"""
    
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'password_confirm']
    
    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password": "Passwords must match"})
        
        # Validate password strength
        password = data['password']
        if not any(c.isupper() for c in password):
            raise serializers.ValidationError({"password": "Password must contain uppercase letter"})
        if not any(c.isdigit() for c in password):
            raise serializers.ValidationError({"password": "Password must contain digit"})
        
        data.pop('password_confirm')
        return data
    
    def create(self, validated_data: Dict[str, Any]) -> User:
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """User update without password"""
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']


class UserPasswordSerializer(serializers.Serializer):
    """Change password serializer"""
    
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True, required=True, min_length=8)
    
    def validate_new_password(self, value: str) -> str:
        if not any(c.isupper() for c in value):
            raise serializers.ValidationError("Password must contain uppercase letter")
        if not any(c.isdigit() for c in value):
            raise serializers.ValidationError("Password must contain digit")
        return value
    
    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError({"new_password": "Passwords must match"})
        return data
