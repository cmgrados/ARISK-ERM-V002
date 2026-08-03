from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Sum, Count, Avg, Q
from decimal import Decimal

from credit_risk.models import Customer, CreditOperation
from .serializers import (
    CustomerSerializer,
    CreditOperationListSerializer,
    CreditOperationDetailSerializer,
    CreditOperationCreateSerializer,
    CreditRiskMetricsSerializer,
)


class CustomerViewSet(viewsets.ModelViewSet):
    """
    Customer management viewset.
    
    Endpoints:
    - GET /customers/ - List all customers
    - POST /customers/ - Create new customer
    - GET /customers/{id}/ - Retrieve customer
    - PUT /customers/{id}/ - Update customer
    - DELETE /customers/{id}/ - Delete customer
    - GET /customers/{id}/operations/ - Get customer operations
    - GET /customers/{id}/portfolio_summary/ - Get customer portfolio summary
    """
    
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'dni', 'ruc', 'email']
    ordering_fields = ['created_at', 'name']
    ordering = ['-created_at']
    
    @action(detail=True, methods=['get'])
    def operations(self, request, pk=None):
        """Get all credit operations for a customer"""
        customer = self.get_object()
        operations = CreditOperation.objects.filter(customer=customer)
        serializer = CreditOperationDetailSerializer(operations, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def portfolio_summary(self, request, pk=None):
        """Get portfolio summary for a customer"""
        customer = self.get_object()
        operations = CreditOperation.objects.filter(customer=customer)
        
        total_amount = operations.aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
        active_loans = operations.filter(status='active').count()
        overdue_amount = operations.filter(days_past_due__gt=0).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
        
        return Response({
            'customer_id': customer.id,
            'customer_name': customer.name,
            'total_amount': total_amount,
            'active_loans': active_loans,
            'overdue_amount': overdue_amount,
            'delinquency_rate': float(overdue_amount / total_amount * 100) if total_amount > 0 else 0,
        })


class CreditOperationViewSet(viewsets.ModelViewSet):
    """
    Credit operation management viewset.
    
    Endpoints:
    - GET /credit-operations/ - List all operations
    - POST /credit-operations/ - Create new operation
    - GET /credit-operations/{id}/ - Retrieve operation
    - PUT /credit-operations/{id}/ - Update operation
    - DELETE /credit-operations/{id}/ - Delete operation
    - GET /credit-operations/summary/ - Summary statistics
    - GET /credit-operations/high_risk/ - High risk operations
    - GET /credit-operations/critical/ - Critical operations
    - GET /credit-operations/by_currency/ - Operations by currency
    """
    
    queryset = CreditOperation.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['customer', 'currency', 'status']
    search_fields = ['customer__name', 'customer__dni']
    ordering_fields = ['created_at', 'amount', 'days_past_due']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CreditOperationCreateSerializer
        elif self.action == 'list':
            return CreditOperationListSerializer
        return CreditOperationDetailSerializer
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get credit risk summary statistics"""
        total_portfolio = self.queryset.aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
        total_loans = self.queryset.count()
        average_exposure = self.queryset.aggregate(Avg('amount'))['amount__avg'] or Decimal('0')
        overdue_amount = self.queryset.filter(days_past_due__gt=0).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
        
        expected_loss = Decimal('0')
        for op in self.queryset:
            if op.pd and op.lgd:
                expected_loss += op.amount * op.pd * op.lgd
        
        return Response({
            'total_portfolio': total_portfolio,
            'total_loans': total_loans,
            'average_exposure': average_exposure,
            'overdue_amount': overdue_amount,
            'expected_loss': expected_loss,
            'risk_concentration': (max([op.amount for op in self.queryset], default=Decimal('0')) / total_portfolio * 100) if total_portfolio > 0 else 0,
        })
    
    @action(detail=False, methods=['get'])
    def high_risk(self, request):
        """Get high risk credit operations (days past due > 30)"""
        high_risk_ops = self.queryset.filter(days_past_due__gt=30)
        serializer = CreditOperationDetailSerializer(high_risk_ops, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def critical(self, request):
        """Get critical operations (days past due > 90)"""
        critical_ops = self.queryset.filter(days_past_due__gt=90)
        serializer = CreditOperationDetailSerializer(critical_ops, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_currency(self, request):
        """Get operations by currency"""
        currencies = self.queryset.values('currency').annotate(
            total=Sum('amount'),
            count=Count('id'),
            average=Avg('amount')
        )
        return Response(list(currencies))
