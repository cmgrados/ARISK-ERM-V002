"""ViewSets for users app - DRF API."""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from .models import Organization, Role
from .serializers import (
    OrganizationSerializer, RoleSerializer, UserDetailSerializer,
    UserListSerializer, UserCreateSerializer, PermissionsSerializer
)

User = get_user_model()


class OrganizationViewSet(viewsets.ModelViewSet):
    """ViewSet for Organization model."""

    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'ruc']
    ordering_fields = ['name', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filter by is_active if query param is provided."""
        queryset = super().get_queryset()
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            is_active = is_active.lower() == 'true'
            queryset = queryset.filter(is_active=is_active)
        return queryset

    def get_permissions(self):
        """Allow admin only for create/update/delete."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission_class() for permission_class in permission_classes]

    @action(detail=True, methods=['get'])
    def users(self, request, pk=None):
        """Get all users in this organization."""
        org = self.get_object()
        users = org.users.all()
        serializer = UserListSerializer(users, many=True)
        return Response(serializer.data)


class RoleViewSet(viewsets.ModelViewSet):
    """ViewSet for Role model."""

    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name']
    ordering = ['name']

    def get_permissions(self):
        """Allow admin only for create/update/delete."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission_class() for permission_class in permission_classes]


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for User model."""

    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'is_staff', 'is_superuser', 'is_risk_manager', 'is_auditor', 'organization']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['username', 'date_joined', 'last_login']
    ordering = ['-date_joined']

    def get_serializer_class(self):
        """Return different serializers based on action."""
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action == 'list':
            return UserListSerializer
        else:
            return UserDetailSerializer

    def get_queryset(self):
        """Filter queryset based on user role."""
        user = self.request.user
        if user.is_superuser or user.is_staff:
            return User.objects.all()
        if user.organization:
            return User.objects.filter(organization=user.organization)
        return User.objects.none()

    def get_permissions(self):
        """Set permissions based on action."""
        if self.action == 'create':
            permission_classes = [IsAdminUser]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission_class() for permission_class in permission_classes]

    @action(detail=True, methods=['get'])
    def permissions(self, request, pk=None):
        """Get permissions for this user."""
        user = self.get_object()
        serializer = PermissionsSerializer(user)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user information."""
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def set_password(self, request, pk=None):
        """Change password for a user."""
        user = self.get_object()
        if request.user != user and not request.user.is_staff:
            return Response(
                {'error': 'You can only change your own password.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = UserDetailSerializer(
            user, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response({'status': 'password set'})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a user."""
        if not request.user.is_staff:
            return Response(
                {'error': 'Only staff can activate users.'},
                status=status.HTTP_403_FORBIDDEN
            )
        user = self.get_object()
        user.is_active = True
        user.save()
        return Response({'status': 'user activated'})

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a user."""
        if not request.user.is_staff:
            return Response(
                {'error': 'Only staff can deactivate users.'},
                status=status.HTTP_403_FORBIDDEN
            )
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response({'status': 'user deactivated'})
