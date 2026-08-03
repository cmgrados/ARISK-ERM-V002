from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from risks.models import Risk, RiskAssessment, RiskCause, RiskConsequence
from .serializers import (
    RiskListSerializer,
    RiskDetailSerializer,
    RiskCreateUpdateSerializer,
    RiskCauseSerializer,
    RiskConsequenceSerializer,
    RiskAssessmentSerializer,
)


class RiskViewSet(viewsets.ModelViewSet):
    """
    Risk management viewset.
    
    Endpoints:
    - GET /risks/ - List all risks
    - POST /risks/ - Create new risk
    - GET /risks/{id}/ - Retrieve risk
    - PUT /risks/{id}/ - Update risk
    - DELETE /risks/{id}/ - Delete risk
    - GET /risks/summary/ - Risk summary statistics
    - GET /risks/{id}/causes/ - Get risk causes
    - GET /risks/{id}/consequences/ - Get risk consequences
    - GET /risks/{id}/assessments/ - Get risk assessments
    """
    
    queryset = Risk.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'category']
    search_fields = ['name', 'description', 'owner']
    ordering_fields = ['created_at', 'risk_score', 'probability', 'impact']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RiskCreateUpdateSerializer
        elif self.action == 'list':
            return RiskListSerializer
        return RiskDetailSerializer
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get risk summary statistics"""
        total_risks = self.queryset.count()
        high_risks = self.queryset.filter(risk_score__gte=20).count()
        by_status = {}
        for status_choice in Risk.STATUS_CHOICES:
            by_status[status_choice[0]] = self.queryset.filter(status=status_choice[0]).count()
        
        return Response({
            'total_risks': total_risks,
            'high_risks': high_risks,
            'by_status': by_status,
        })
    
    @action(detail=True, methods=['get'])
    def causes(self, request, pk=None):
        """Get all causes for a risk"""
        risk = self.get_object()
        causes = RiskCause.objects.filter(risk=risk)
        serializer = RiskCauseSerializer(causes, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def consequences(self, request, pk=None):
        """Get all consequences for a risk"""
        risk = self.get_object()
        consequences = RiskConsequence.objects.filter(risk=risk)
        serializer = RiskConsequenceSerializer(consequences, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def assessments(self, request, pk=None):
        """Get all assessments for a risk"""
        risk = self.get_object()
        assessments = RiskAssessment.objects.filter(risk=risk)
        serializer = RiskAssessmentSerializer(assessments, many=True)
        return Response(serializer.data)


class RiskCauseViewSet(viewsets.ModelViewSet):
    """Risk cause management"""
    
    queryset = RiskCause.objects.all()
    serializer_class = RiskCauseSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['risk']
    ordering_fields = ['created_at']


class RiskConsequenceViewSet(viewsets.ModelViewSet):
    """Risk consequence management"""
    
    queryset = RiskConsequence.objects.all()
    serializer_class = RiskConsequenceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['risk']
    ordering_fields = ['created_at']


class RiskAssessmentViewSet(viewsets.ModelViewSet):
    """Risk assessment management"""
    
    queryset = RiskAssessment.objects.all()
    serializer_class = RiskAssessmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['risk', 'assessor']
    ordering_fields = ['assessment_date']
