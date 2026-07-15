from django.contrib import admin
from .models import (
    Macroprocess, Process, RiskCategory, ProbabilityLevel, ImpactLevel,
    Subprocess, Activity, Risk, Control, RiskEvent, KeyRiskIndicator,
    KRIReading, ActionPlan, ActionPlanEvidence, OpRiskDocument,
    OperationalCapitalCalculation
)

@admin.register(Macroprocess)
class MacroprocessAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner_position', 'owner_area', 'created_at')
    search_fields = ('name',)

@admin.register(Process)
class ProcessAdmin(admin.ModelAdmin):
    list_display = ('name', 'macroprocess', 'criticality', 'owner_position', 'owner_area')
    search_fields = ('name', 'macroprocess__name')
    list_filter = ('criticality',)

@admin.register(RiskCategory)
class RiskCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(ProbabilityLevel)
class ProbabilityLevelAdmin(admin.ModelAdmin):
    list_display = ('level', 'name', 'weight')
    ordering = ('level',)

@admin.register(ImpactLevel)
class ImpactLevelAdmin(admin.ModelAdmin):
    list_display = ('level', 'name', 'financial_threshold')
    ordering = ('level',)

@admin.register(Subprocess)
class SubprocessAdmin(admin.ModelAdmin):
    list_display = ('name', 'process', 'owner_position', 'owner_area')
    search_fields = ('name', 'process__name')

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('name', 'subprocess', 'owner_position', 'owner_area')
    search_fields = ('name', 'subprocess__name')

@admin.register(Risk)
class RiskAdmin(admin.ModelAdmin):
    list_display = ('name', 'process', 'status', 'owner')
    search_fields = ('name', 'process__name')
    list_filter = ('status', 'category')

@admin.register(Control)
class ControlAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'periodicity', 'owner')
    search_fields = ('name',)
    list_filter = ('type',)

@admin.register(OpRiskDocument)
class OpRiskDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_by', 'created_at', 'content_object')
    search_fields = ('title',)

@admin.register(OperationalCapitalCalculation)
class OperationalCapitalCalculationAdmin(admin.ModelAdmin):
    list_display = ('year', 'calculated_capital', 'alfa_factor')
    readonly_fields = ('calculated_capital',)
    search_fields = ('year',)

@admin.register(RiskEvent)
class RiskEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_type', 'date_occurred', 'amount')
    search_fields = ('title',)
    list_filter = ('event_type',)

@admin.register(KeyRiskIndicator)
class KRIAdmin(admin.ModelAdmin):
    list_display = ('name', 'process', 'risk')
    search_fields = ('name',)

@admin.register(KRIReading)
class KRIReadingAdmin(admin.ModelAdmin):
    list_display = ('kri', 'date', 'value')
    list_filter = ('kri',)

@admin.register(ActionPlan)
class ActionPlanAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'commitment_date', 'owner')
    search_fields = ('title',)
    list_filter = ('status',)

admin.site.register(ActionPlanEvidence)
