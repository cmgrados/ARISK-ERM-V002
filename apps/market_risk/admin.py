from django.contrib import admin
from .models import MarketTimeBand, MarketPositionUpload, MarketPosition, MarketScenario, MarketLimit

@admin.register(MarketTimeBand)
class MarketTimeBandAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'days_start', 'days_end')
    ordering = ('order',)

@admin.register(MarketScenario)
class MarketScenarioAdmin(admin.ModelAdmin):
    list_display = ('name', 'scenario_type', 'rate_shock_bps', 'fx_shock_percent', 'is_active')
    list_filter = ('scenario_type', 'is_active')
    search_fields = ('name',)

@admin.register(MarketLimit)
class MarketLimitAdmin(admin.ModelAdmin):
    list_display = ('name', 'threshold_value', 'is_percentage')

@admin.register(MarketPositionUpload)
class MarketPositionUploadAdmin(admin.ModelAdmin):
    list_display = ('period_date', 'status', 'created_at')
    date_hierarchy = 'period_date'

@admin.register(MarketPosition)
class MarketPositionAdmin(admin.ModelAdmin):
    list_display = ('account_code', 'position_type', 'currency', 'balance', 'interest_rate', 'time_band')
    list_filter = ('position_type', 'currency', 'time_band', 'upload__period_date')
    search_fields = ('account_code', 'description')
