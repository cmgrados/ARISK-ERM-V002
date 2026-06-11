from django.contrib import admin
from .models import OpRiskIncident, OpRiskEventCategory, COSOComponent, COSOPrinciple, COSOAssessment, RiskManagementStep

admin.site.register(OpRiskEventCategory)

@admin.register(OpRiskIncident)
class OpRiskIncidentAdmin(admin.ModelAdmin):
    list_display = ('title', 'incident_date', 'severity', 'gross_loss', 'net_loss')
    list_filter = ('severity', 'category')
    search_fields = ('title', 'description')

@admin.register(COSOComponent)
class COSOComponentAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
    ordering = ('order',)

@admin.register(COSOPrinciple)
class COSOPrincipleAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'component')
    list_filter = ('component',)
    ordering = ('code',)

@admin.register(COSOAssessment)
class COSOAssessmentAdmin(admin.ModelAdmin):
    list_display = ('principle', 'evaluation_date', 'score', 'assessed_by')
    list_filter = ('evaluation_date', 'score', 'principle__component')
    date_hierarchy = 'evaluation_date'

@admin.register(RiskManagementStep)
class RiskManagementStepAdmin(admin.ModelAdmin):
    list_display = ('order', 'name', 'url_name')
    list_display_links = ('name',)
    list_editable = ('order', 'url_name')
    ordering = ('order',)
