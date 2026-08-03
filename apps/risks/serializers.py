"""Serializers for risks app."""

from rest_framework import serializers
from .models import (
    Risk, RiskCause, RiskConsequence, ProbabilityScale,
    ImpactScale, RiskMatrixConfiguration, RiskAssessment
)


class ProbabilityScaleSerializer(serializers.ModelSerializer):
    """Serializer for ProbabilityScale model."""

    class Meta:
        model = ProbabilityScale
        fields = ['id', 'name', 'value', 'description']
        read_only_fields = ['id']


class ImpactScaleSerializer(serializers.ModelSerializer):
    """Serializer for ImpactScale model."""

    class Meta:
        model = ImpactScale
        fields = ['id', 'name', 'value', 'description']
        read_only_fields = ['id']


class RiskMatrixConfigurationSerializer(serializers.ModelSerializer):
    """Serializer for RiskMatrixConfiguration model."""

    probability_name = serializers.CharField(source='probability.name', read_only=True)
    impact_name = serializers.CharField(source='impact.name', read_only=True)
    severity_display = serializers.CharField(source='get_severity_level_display', read_only=True)

    class Meta:
        model = RiskMatrixConfiguration
        fields = [
            'id', 'probability', 'probability_name',
            'impact', 'impact_name',
            'severity_level', 'severity_display', 'score'
        ]
        read_only_fields = ['id']


class RiskCauseSerializer(serializers.ModelSerializer):
    """Serializer for RiskCause model."""

    class Meta:
        model = RiskCause
        fields = ['id', 'risk', 'description']
        read_only_fields = ['id']


class RiskConsequenceSerializer(serializers.ModelSerializer):
    """Serializer for RiskConsequence model."""

    consequence_type_display = serializers.CharField(source='get_consequence_type_display', read_only=True)

    class Meta:
        model = RiskConsequence
        fields = [
            'id', 'risk', 'consequence_type',
            'consequence_type_display', 'description'
        ]
        read_only_fields = ['id']


class RiskAssessmentDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for RiskAssessment model."""

    inherent_probability = ProbabilityScaleSerializer(read_only=True)
    inherent_impact = ImpactScaleSerializer(read_only=True)
    inherent_probability_id = serializers.IntegerField(write_only=True, required=False)
    inherent_impact_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = RiskAssessment
        fields = [
            'id', 'risk', 'assessment_date',
            'inherent_probability', 'inherent_probability_id',
            'inherent_impact', 'inherent_impact_id',
            'inherent_score', 'inherent_severity',
            'mitigation_factor', 'residual_score', 'residual_severity',
            'comments'
        ]
        read_only_fields = [
            'id', 'assessment_date',
            'inherent_score', 'inherent_severity',
            'mitigation_factor', 'residual_score', 'residual_severity'
        ]


class RiskListSerializer(serializers.ModelSerializer):
    """Simplified serializer for Risk list view."""

    category_display = serializers.CharField(source='get_category_display', read_only=True)
    criticality_display = serializers.CharField(source='get_criticallity_display', read_only=True)
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)

    class Meta:
        model = Risk
        fields = [
            'id', 'name', 'category', 'category_display',
            'criticallity', 'criticality_display',
            'owner_name', 'description'
        ]
        read_only_fields = fields


class RiskDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for Risk model."""

    category_display = serializers.CharField(source='get_category_display', read_only=True)
    criticality_display = serializers.CharField(source='get_criticallity_display', read_only=True)
    causes = RiskCauseSerializer(source='causes_list', many=True, read_only=True)
    consequences = RiskConsequenceSerializer(source='consequences_list', many=True, read_only=True)
    assessments = RiskAssessmentDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Risk
        fields = [
            'id', 'name', 'description', 'category', 'category_display',
            'criticallity', 'criticality_display',
            'owner', 'risk_type',
            'process', 'subprocess', 'activity',
            'causes', 'consequences', 'assessments'
        ]
        read_only_fields = ['id']

    def validate_name(self, value):
        """Validate risk name is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError("Risk name cannot be empty.")
        return value


class RiskCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating Risk."""

    class Meta:
        model = Risk
        fields = [
            'name', 'description', 'category',
            'criticallity', 'owner', 'risk_type',
            'process', 'subprocess', 'activity'
        ]

    def validate_name(self, value):
        """Validate risk name is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError("Risk name cannot be empty.")
        return value


class RiskSummarySerializer(serializers.Serializer):
    """Serializer for risk summary statistics."""

    total_risks = serializers.IntegerField()
    by_category = serializers.DictField(child=serializers.IntegerField())
    by_criticality = serializers.DictField(child=serializers.IntegerField())
    high_risk_count = serializers.IntegerField()
