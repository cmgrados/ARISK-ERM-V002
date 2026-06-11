from django.contrib import admin
from .models import ComplianceRequirement, ComplianceRisk, ComplianceFinding

@admin.register(ComplianceRequirement)
class ComplianceRequirementAdmin(admin.ModelAdmin):
    list_display = ('id', 'source', 'description_short', 'responsible_area')
    list_filter = ('source', 'responsible_area')
    
    def description_short(self, obj):
        return obj.description[:75] + "..."
    description_short.short_description = "Descripción"

@admin.register(ComplianceRisk)
class ComplianceRiskAdmin(admin.ModelAdmin):
    list_display = ('id', 'requirement', 'inherent_risk_display', 'residual_risk_display', 'monitoring_frequency')
    list_filter = ('monitoring_frequency', 'evaluation_period')

    def inherent_risk_display(self, obj):
        return f"{obj.inherent_risk_value} ({obj.inherent_risk_category})"
    inherent_risk_display.short_description = "Riesgo Inherente"

    def residual_risk_display(self, obj):
        return f"{obj.residual_risk_value} ({obj.residual_risk_category})"
    residual_risk_display.short_description = "Riesgo Residual"

@admin.register(ComplianceFinding)
class ComplianceFindingAdmin(admin.ModelAdmin):
    list_display = ('id', 'risk', 'state', 'due_date', 'responsible')
    list_filter = ('state',)
    search_fields = ('description',)
