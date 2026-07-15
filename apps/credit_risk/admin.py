from django.contrib import admin
from .models import Customer, CreditOperation, CreditRiskMetrics, CarteraCreditoCarga

admin.site.register(Customer)
admin.site.register(CreditRiskMetrics)

@admin.register(CreditOperation)
class CreditOperationAdmin(admin.ModelAdmin):
    list_display = ('operation_code', 'customer', 'balance', 'days_past_due', 'sbs_classification', 'is_refinanced')
    list_filter = ('sbs_classification', 'is_refinanced', 'bucket')
    search_fields = ('operation_code', 'customer__name', 'customer__document_id')

@admin.register(CarteraCreditoCarga)
class CarteraCreditoCargaAdmin(admin.ModelAdmin):
    list_display = ('csoc', 'ncl', 'ccr', 'morg', 'skcr', 'fecha_carga')
    search_fields = ('csoc', 'ncl', 'ccr', 'nid')
    list_filter = ('stcr', 'fecha_corte')
