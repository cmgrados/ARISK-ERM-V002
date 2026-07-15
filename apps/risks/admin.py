from django.contrib import admin
from .models import Risk, RiskAssessment

class RiskAssessmentInline(admin.TabularInline):
    model = RiskAssessment
    extra = 1

@admin.register(Risk)
class RiskAdmin(admin.ModelAdmin):
    inlines = [RiskAssessmentInline]
    list_display = ('name', 'risk_type', 'process', 'owner')
    list_filter = ('risk_type', 'process')
