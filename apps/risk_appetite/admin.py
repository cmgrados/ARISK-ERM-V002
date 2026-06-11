from django.contrib import admin
from .models import (
    RAFFramework, RAFStatement, KRICatalog, RAFThreshold, 
    KRIMeasurement, RAFBreach, RAFActionPlan, RAFApproval, RAFChangeLog
)

@admin.register(RAFFramework)
class RAFFrameworkAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'version', 'state', 'start_date', 'end_date')
    list_filter = ('state',)
    search_fields = ('name', 'code')

@admin.register(RAFStatement)
class RAFStatementAdmin(admin.ModelAdmin):
    list_display = ('framework', 'risk_type', 'risk_posture', 'application_level')
    list_filter = ('risk_posture', 'framework')

@admin.register(KRICatalog)
class KRICatalogAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'risk_type', 'kri_level', 'frequency')
    list_filter = ('risk_type', 'kri_level')
    search_fields = ('name', 'code')

@admin.register(RAFThreshold)
class RAFThresholdAdmin(admin.ModelAdmin):
    list_display = ('framework', 'kri', 'target_value', 'green_threshold', 'red_threshold')
    list_filter = ('framework',)

@admin.register(KRIMeasurement)
class KRIMeasurementAdmin(admin.ModelAdmin):
    list_display = ('kri', 'cut_off_date', 'value', 'semaphore')
    list_filter = ('semaphore', 'kri')

@admin.register(RAFBreach)
class RAFBreachAdmin(admin.ModelAdmin):
    list_display = ('measurement', 'breach_type', 'severity', 'state', 'due_date')
    list_filter = ('state', 'severity', 'breach_type')

admin.site.register(RAFActionPlan)
admin.site.register(RAFApproval)
admin.site.register(RAFChangeLog)
