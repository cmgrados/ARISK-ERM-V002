from django.contrib import admin
from .models import (
    StrategicPlan, ExternalEnvironment, FinancialEnvironment, InternalDiagnosis,
    StrategicMatrix, BusinessModelCanvas, Perspectiva, ObjetivoEstrategico,
    Indicador, MetaPeriodo, ProyectoIniciativa, EjecucionPresupuestaria, HitoProyecto, Survey, SurveyQuestion, SurveyResponse, SurveyAnswer
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

@admin.register(Perspectiva)
class PerspectivaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'organization', 'peso_porcentual')
    list_filter = ('organization',)

@admin.register(ObjetivoEstrategico)
class ObjetivoEstrategicoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'perspectiva', 'organization')
    list_filter = ('perspectiva', 'organization')

@admin.register(Indicador)
class IndicadorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'objetivo', 'frecuencia_medicion', 'organization')
    list_filter = ('frecuencia_medicion', 'organization')

@admin.register(MetaPeriodo)
class MetaPeriodoAdmin(admin.ModelAdmin):
    list_display = ('indicador', 'periodo', 'meta_programada', 'resultado_real', 'semaforo')
    list_filter = ('semaforo', 'periodo', 'indicador__organization')

@admin.register(ProyectoIniciativa)
class ProyectoIniciativaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'indicador', 'estado', 'porcentaje_avance_fisico', 'porcentaje_avance_financiero', 'semaforo_ejecucion')
    list_filter = ('estado', 'semaforo_ejecucion', 'organization')

@admin.register(EjecucionPresupuestaria)
class EjecucionPresupuestariaAdmin(admin.ModelAdmin):
    list_display = ('proyecto', 'periodo', 'gasto_programado', 'gasto_real')
    list_filter = ('proyecto__organization',)

@admin.register(HitoProyecto)
class HitoProyectoAdmin(admin.ModelAdmin):
    list_display = ('proyecto', 'nombre', 'fecha_entrega', 'porcentaje_avance_programado', 'porcentaje_avance_real')
    list_filter = ('proyecto__organization',)

admin.site.register(Survey)
admin.site.register(SurveyQuestion)
admin.site.register(SurveyResponse)
admin.site.register(SurveyAnswer)
