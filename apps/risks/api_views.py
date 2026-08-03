"""ViewSets for risks app - DRF API."""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    Risk, RiskCause, RiskConsequence, ProbabilityScale,
    ImpactScale, RiskMatrixConfiguration, RiskAssessment
)
from .serializers import (
    RiskDetailSerializer, RiskListSerializer, RiskCreateUpdateSerializer,
    RiskCauseSerializer, RiskConsequenceSerializer,
    ProbabilityScaleSerializer, ImpactScaleSerializer,
    RiskMatrixConfigurationSerializer, RiskAssessmentDetailSerializer,
    RiskSummarySerializer
)


class ProbabilityScaleViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only ViewSet for ProbabilityScale."""

    queryset = ProbabilityScale.objects.all()
    serializer_class = ProbabilityScaleSerializer
    permission_classes = [IsAuthenticated]
    ordering_fields = ['value']
    ordering = ['value']


class ImpactScaleViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only ViewSet for ImpactScale."""

    queryset = ImpactScale.objects.all()
    serializer_class = ImpactScaleSerializer
    permission_classes = [IsAuthenticated]
    ordering_fields = ['value']
    ordering = ['value']


class RiskMatrixConfigurationViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only ViewSet for RiskMatrixConfiguration."""

    queryset = RiskMatrixConfiguration.objects.all()
    serializer_class = RiskMatrixConfigurationSerializer
    permission_classes = [IsAuthenticated]


class RiskCauseViewSet(viewsets.ModelViewSet):
    """ViewSet for RiskCause."""

    queryset = RiskCause.objects.all()
    serializer_class = RiskCauseSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['risk']

    def get_permissions(self):
        """Only admin can create/update/delete."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission_class() for permission_class in permission_classes]


class RiskConsequenceViewSet(viewsets.ModelViewSet):
    """ViewSet for RiskConsequence."""

    queryset = RiskConsequence.objects.all()
    serializer_class = RiskConsequenceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['risk', 'consequence_type']

    def get_permissions(self):
        """Only admin can create/update/delete."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission_class() for permission_class in permission_classes]


class RiskAssessmentViewSet(viewsets.ModelViewSet):
    """ViewSet for RiskAssessment."""

    queryset = RiskAssessment.objects.all()
    serializer_class = RiskAssessmentDetailSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['risk', 'inherent_severity', 'residual_severity']
    ordering_fields = ['assessment_date', 'residual_score']
    ordering = ['-assessment_date']

    def get_permissions(self):
        """Only admin can create/update/delete."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission_class() for permission_class in permission_classes]


class RiskViewSet(viewsets.ModelViewSet):
    """ViewSet for Risk model."""

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'criticallity', 'owner']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'criticallity']
    ordering = ['-criticallity', 'name']

    def get_serializer_class(self):
        """Return different serializers based on action."""
        if self.action == 'list':
            return RiskListSerializer
        elif self.action == 'create' or self.action == 'update' or self.action == 'partial_update':
            return RiskCreateUpdateSerializer
        else:
            return RiskDetailSerializer

    def get_queryset(self):
        """Filter queryset."""
        return Risk.objects.all()

    def get_permissions(self):
        """Only admin can create/update/delete."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission_class() for permission_class in permission_classes]

    @action(detail=True, methods=['get'])
    def causes(self, request, pk=None):
        """Get all causes for this risk."""
        risk = self.get_object()
        causes = risk.causes_list.all()
        serializer = RiskCauseSerializer(causes, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def consequences(self, request, pk=None):
        """Get all consequences for this risk."""
        risk = self.get_object()
        consequences = risk.consequences_list.all()
        serializer = RiskConsequenceSerializer(consequences, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def assessments(self, request, pk=None):
        """Get all assessments for this risk."""
        risk = self.get_object()
        assessments = risk.assessments.all()
        serializer = RiskAssessmentDetailSerializer(assessments, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get risk summary statistics."""
        risks = self.get_queryset()
        categories = dict(Risk.RISK_CATEGORY_CHOICES)
        criticalities = dict(Risk.CRITICALITY_CHOICES)

        summary = {
            'total_risks': risks.count(),
            'by_category': {
                cat: risks.filter(category=code).count()
                for code, cat in categories.items()
            },
            'by_criticality': {
                crit: risks.filter(criticallity=code).count()
                for code, crit in criticalities.items()
            },
            'high_risk_count': risks.filter(criticallity__in=['HIGH', 'CRITICAL']).count(),
        }
        serializer = RiskSummarySerializer(summary)
        return Response(serializer.data)
