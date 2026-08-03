"""Serializers for users app with type hints."""

from typing import Any, Dict, Optional
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Organization, Role

User = get_user_model()


class OrganizationSerializer(serializers.ModelSerializer):
    """Serializer for Organization model."""

    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'ruc', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def validate_name(self, value):
        """Validate organization name is unique."""
        qs = Organization.objects.filter(name=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Organization with this name already exists.")
        return value

    def validate_ruc(self, value):
        """Validate RUC format and uniqueness."""
        if value:
            qs = Organization.objects.filter(ruc=value)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError("Organization with this RUC already exists.")
        return value


class RoleSerializer(serializers.ModelSerializer):
    """Serializer for Role model."""

    class Meta:
        model = Role
        fields = [
            'id', 'name', 'description', 'permissions'
        ]
        read_only_fields = ['id']

    def validate_name(self, value):
        """Validate role name is unique."""
        qs = Role.objects.filter(name=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Role with this name already exists.")
        return value


class UserDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for User model with nested organization and role."""

    organization = OrganizationSerializer(read_only=True)
    role = RoleSerializer(read_only=True)
    organization_id = serializers.IntegerField(write_only=True, required=False)
    role_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_active', 'is_staff', 'is_superuser',
            'is_risk_manager', 'is_auditor',
            'organization', 'organization_id',
            'role', 'role_id',
            'date_joined', 'last_login',
            'can_access_integral_risk',
            'can_access_financial_planning',
            'can_access_strategic_planning'
        ]
        read_only_fields = [
            'id', 'date_joined', 'last_login',
            'can_access_integral_risk',
            'can_access_financial_planning',
            'can_access_strategic_planning'
        ]

    def validate_email(self, value):
        """Validate email uniqueness."""
        qs = User.objects.filter(email=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("User with this email already exists.")
        return value

    def validate_username(self, value):
        """Validate username uniqueness."""
        qs = User.objects.filter(username=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("User with this username already exists.")
        return value

    def create(self, validated_data):
        """Create user with proper password hashing."""
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        """Update user with proper password hashing."""
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class UserListSerializer(serializers.ModelSerializer):
    """Simplified serializer for User list view."""

    organization_name = serializers.CharField(source='organization.name', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_active', 'is_staff', 'is_superuser',
            'is_risk_manager', 'is_auditor',
            'organization_name', 'role_name',
            'date_joined'
        ]
        read_only_fields = fields


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating users with password."""

    password = serializers.CharField(write_only=True, required=True)
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'password', 'password_confirm',
            'organization', 'role',
            'is_risk_manager', 'is_auditor',
            'is_staff', 'is_superuser'
        ]

    def validate(self, data):
        """Validate that passwords match."""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        """Create user with hashed password."""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class PermissionsSerializer(serializers.Serializer):
    """Serializer for checking user permissions."""

    integral_risk = serializers.SerializerMethodField()
    financial_planning = serializers.SerializerMethodField()
    strategic_planning = serializers.SerializerMethodField()
    is_superuser = serializers.BooleanField()
    is_staff = serializers.BooleanField()

    def get_integral_risk(self, obj):
        """Check if user has access to integral risk."""
        return obj.can_access_integral_risk

    def get_financial_planning(self, obj):
        """Check if user has access to financial planning."""
        return obj.can_access_financial_planning

    def get_strategic_planning(self, obj):
        """Check if user has access to strategic planning."""
        return obj.can_access_strategic_planning
