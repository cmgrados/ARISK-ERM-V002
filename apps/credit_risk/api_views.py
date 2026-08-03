"""ViewSets for credit_risk app - DRF API."""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Avg, Q
from decimal import Decimal
from .models import Customer, CreditOperation, CreditRiskMetrics, CreditRiskPeriodParameter
from .serializers import (
    CustomerSerializer, CreditOperationDetailSerializer,
    CreditOperationListSerializer, CreditOperationCreateSerializer,
    CreditRiskMetricsSerializer, CreditRiskPeriodParameterSerializer,
    CreditPortfolioSummarySerializer
)


class CustomerViewSet(viewsets.ModelViewSet):
    """ViewSet for Customer model."""

    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['document_id', 'name', 'segment', 'economic_activity']
    ordering_fields = ['name', 'document_id']
    ordering = ['name']

    def get_permissions(self):
        """Only admin can create/update/delete."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission_class() for permission_class in permission_classes]

    @action(detail=True, methods=['get'])
    def operations(self, request, pk=None):
        """Get all credit operations for this customer."""
        customer = self.get_object()
        operations = customer.operations.all()
        serializer = CreditOperationListSerializer(operations, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def portfolio_summary(self, request, pk=None):
        """Get portfolio summary for this customer."""
        customer = self.get_object()
        operations = customer.operations.all()

        summary = {
            'customer_id': customer.id,
            'customer_name': customer.name,
            'total_operations': operations.count(),
            'total_current_portfolio': operations.aggregate(Sum('current_portfolio'))['current_portfolio__sum'] or Decimal('0'),
            'total_past_due_portfolio': operations.aggregate(Sum('past_due_portfolio'))['past_due_portfolio__sum'] or Decimal('0'),
            'total_provisions': (
                operations.aggregate(Sum('generic_provision'))['generic_provision__sum'] or Decimal('0') +
                operations.aggregate(Sum('specific_provision'))['specific_provision__sum'] or Decimal('0')
            ),
            'high_risk_operations': operations.filter(days_past_due__gt=90).count(),
            'critical_operations': operations.filter(days_past_due__gt=180).count(),
        }
        return Response(summary)


class CreditOperationViewSet(viewsets.ModelViewSet):
    """ViewSet for CreditOperation model."""

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['customer', 'currency', 'credit_type', 'agency', 'sbs_classification', 'load_date']
    search_fields = ['operation_code', 'product_name', 'customer__name']
    ordering_fields = ['operation_code', 'original_amount', 'days_past_due', 'load_date']
    ordering = ['-load_date', '-days_past_due']

    def get_serializer_class(self):
        """Return different serializers based on action."""
        if self.action == 'list':
            return CreditOperationListSerializer
        elif self.action == 'create':
            return CreditOperationCreateSerializer
        else:
            return CreditOperationDetailSerializer

    def get_queryset(self):
        """Filter queryset."""
        return CreditOperation.objects.all()

    def get_permissions(self):
        """Only admin can create/update/delete."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission_class() for permission_class in permission_classes]

    @action(detail=True, methods=['get'])
    def metrics(self, request, pk=None):
        """Get risk metrics for this credit operation."""
        operation = self.get_object()
        try:
            metrics = operation.metrics
            serializer = CreditRiskMetricsSerializer(metrics)
            return Response(serializer.data)
        except CreditRiskMetrics.DoesNotExist:
            return Response(
                {'error': 'No metrics found for this operation.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get portfolio summary statistics."""
        operations = self.get_queryset()

        current_total = operations.aggregate(Sum('current_portfolio'))['current_portfolio__sum'] or Decimal('0')
        past_due_total = operations.aggregate(Sum('past_due_portfolio'))['past_due_portfolio__sum'] or Decimal('0')
        total_provisions = (
            (operations.aggregate(Sum('generic_provision'))['generic_provision__sum'] or Decimal('0')) +
            (operations.aggregate(Sum('specific_provision'))['specific_provision__sum'] or Decimal('0'))
        )
        avg_rate = operations.aggregate(Avg('rate'))['rate__avg'] or Decimal('0')

        summary = {
            'total_customers': Customer.objects.filter(operations__in=operations).distinct().count(),
            'total_operations': operations.count(),
            'total_current_portfolio': str(current_total),
            'total_past_due_portfolio': str(past_due_total),
            'total_provisions': str(total_provisions),
            'average_rate': str(avg_rate),
            'high_risk_operations': operations.filter(days_past_due__gt=90).count(),
            'critical_operations': operations.filter(days_past_due__gt=180).count(),
        }
        serializer = CreditPortfolioSummarySerializer(summary)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def high_risk(self, request):
        """Get high-risk credit operations (past due > 90 days)."""
        operations = self.get_queryset().filter(days_past_due__gt=90)
        serializer = CreditOperationListSerializer(operations, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def critical(self, request):
        """Get critical credit operations (past due > 180 days)."""
        operations = self.get_queryset().filter(days_past_due__gt=180)
        serializer = CreditOperationListSerializer(operations, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_currency(self, request):
        """Get operations grouped by currency."""
        currency = request.query_params.get('currency', None)
        if currency:
            operations = self.get_queryset().filter(currency=currency)
        else:
            operations = self.get_queryset()

        total_pen = operations.filter(currency='PEN').aggregate(Sum('balance'))['balance__sum'] or Decimal('0')
        total_usd = operations.filter(currency='USD').aggregate(Sum('balance'))['balance__sum'] or Decimal('0')

        return Response({
            'currency_summary': {
                'PEN': str(total_pen),
                'USD': str(total_usd),
            }
        })


class CreditRiskMetricsViewSet(viewsets.ModelViewSet):
    """ViewSet for CreditRiskMetrics model."""

    queryset = CreditRiskMetrics.objects.all()
    serializer_class = CreditRiskMetricsSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['operation']
    ordering_fields = ['pd', 'ead', 'expected_loss']
    ordering = ['-expected_loss']

    def get_permissions(self):
        """Only admin can create/update/delete."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission_class() for permission_class in permission_classes]


class CreditRiskPeriodParameterViewSet(viewsets.ModelViewSet):
    """ViewSet for CreditRiskPeriodParameter model."""

    queryset = CreditRiskPeriodParameter.objects.all()
    serializer_class = CreditRiskPeriodParameterSerializer
    permission_classes = [IsAuthenticated]
    ordering_fields = ['load_date', 'patrimonio_efectivo']
    ordering = ['-load_date']

    def get_permissions(self):
        """Only admin can create/update/delete."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission_class() for permission_class in permission_classes]
