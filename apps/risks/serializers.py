from rest_framework import serializers
from risks.models import Risk, RiskAssessment, RiskCause, RiskConsequence
from typing import Any, Dict


class RiskListSerializer(serializers.ModelSerializer):
    """Lightweight risk list view"""
    
    probability_display = serializers.CharField(source='get_probability_display', read_only=True)
    impact_display = serializers.CharField(source='get_impact_display', read_only=True)
    
    class Meta:
        model = Risk
        fields = ['id', 'name', 'description', 'probability', 'probability_display', 
                 'impact', 'impact_display', 'status', 'created_at']
        read_only_fields = ['id', 'created_at']


class RiskDetailSerializer(serializers.ModelSerializer):
    """Detailed risk information"""
    
    probability_display = serializers.CharField(source='get_probability_display', read_only=True)
    impact_display = serializers.CharField(source='get_impact_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Risk
        fields = ['id', 'name', 'description', 'category', 'probability', 'probability_display',
                 'impact', 'impact_display', 'risk_score', 'status', 'status_display',
                 'owner', 'mitigation_strategy', 'created_at', 'updated_at']
        read_only_fields = ['id', 'risk_score', 'created_at', 'updated_at']


class RiskCreateUpdateSerializer(serializers.ModelSerializer):
    """Create and update risks"""
    
    def validate_probability(self, value: int) -> int:
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Probability must be between 1 and 5")
        return value
    
    def validate_impact(self, value: int) -> int:
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Impact must be between 1 and 5")
        return value
    
    class Meta:
        model = Risk
        fields = ['name', 'description', 'category', 'probability', 'impact', 
                 'status', 'owner', 'mitigation_strategy']


class RiskCauseSerializer(serializers.ModelSerializer):
    """Risk cause information"""
    
    class Meta:
        model = RiskCause
        fields = ['id', 'risk', 'description', 'likelihood', 'created_at']
        read_only_fields = ['id', 'created_at']


class RiskConsequenceSerializer(serializers.ModelSerializer):
    """Risk consequence information"""
    
    class Meta:
        model = RiskConsequence
        fields = ['id', 'risk', 'description', 'severity', 'created_at']
        read_only_fields = ['id', 'created_at']


class RiskAssessmentSerializer(serializers.ModelSerializer):
    """Risk assessment details"""
    
    class Meta:
        model = RiskAssessment
        fields = ['id', 'risk', 'assessment_date', 'probability', 'impact',
                 'residual_risk', 'assessor', 'notes']
        read_only_fields = ['id']
