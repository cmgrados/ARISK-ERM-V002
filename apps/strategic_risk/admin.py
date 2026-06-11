from django.contrib import admin
from .models import (
    StrategicPlan, ExternalEnvironment, FinancialEnvironment, InternalDiagnosis,
    StrategicMatrix, BusinessModelCanvas, StrategicPerspective, StrategicObjective,
    KPI, KPIMeasurement, StrategicProject, Survey, SurveyQuestion, SurveyResponse, SurveyAnswer
)

@admin.register(StrategicPlan)
class StrategicPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'institution', 'start_year', 'horizon_years', 'status', 'version', 'created_by')
    list_filter = ('status', 'start_year', 'horizon_years')
    search_fields = ('name', 'institution')

@admin.register(ExternalEnvironment)
class ExternalEnvironmentAdmin(admin.ModelAdmin):
    list_display = ('plan',)

@admin.register(FinancialEnvironment)
class FinancialEnvironmentAdmin(admin.ModelAdmin):
    list_display = ('plan',)

@admin.register(InternalDiagnosis)
class InternalDiagnosisAdmin(admin.ModelAdmin):
    list_display = ('plan',)

@admin.register(StrategicMatrix)
class StrategicMatrixAdmin(admin.ModelAdmin):
    list_display = ('plan', 'matrix_type')
    list_filter = ('matrix_type',)

@admin.register(BusinessModelCanvas)
class BusinessModelCanvasAdmin(admin.ModelAdmin):
    list_display = ('plan', 'version', 'created_at')

@admin.register(StrategicPerspective)
class StrategicPerspectiveAdmin(admin.ModelAdmin):
    list_display = ('name', 'plan', 'order')
    list_filter = ('plan',)

@admin.register(StrategicObjective)
class StrategicObjectiveAdmin(admin.ModelAdmin):
    list_display = ('name', 'perspective')
    list_filter = ('perspective__plan', 'perspective')

@admin.register(KPI)
class KPIAdmin(admin.ModelAdmin):
    list_display = ('name', 'objective', 'baseline', 'target', 'frequency')
    list_filter = ('frequency', 'objective__perspective__plan')

@admin.register(KPIMeasurement)
class KPIMeasurementAdmin(admin.ModelAdmin):
    list_display = ('kpi', 'period_date', 'value')
    list_filter = ('period_date', 'kpi')

@admin.register(StrategicProject)
class StrategicProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'objective', 'manager', 'status', 'physical_progress', 'financial_progress')
    list_filter = ('status',)

admin.site.register(Survey)
admin.site.register(SurveyQuestion)
admin.site.register(SurveyResponse)
admin.site.register(SurveyAnswer)
