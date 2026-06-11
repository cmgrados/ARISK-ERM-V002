from django.contrib import admin
from .models import RiskControl, ControlTest

class ControlTestInline(admin.TabularInline):
    model = ControlTest
    extra = 1

@admin.register(RiskControl)
class RiskControlAdmin(admin.ModelAdmin):
    inlines = [ControlTestInline]
    list_display = ('name', 'risk', 'control_type', 'owner', 'is_active')
    list_filter = ('control_type', 'is_active')
