from django.contrib import admin
from .models import Customer, CreditOperation, CreditRiskMetrics

admin.site.register(Customer)
admin.site.register(CreditRiskMetrics)

@admin.register(CreditOperation)
class CreditOperationAdmin(admin.ModelAdmin):
    list_display = ('operation_code', 'customer', 'balance', 'days_past_due', 'sbs_classification', 'is_refinanced')
    list_filter = ('sbs_classification', 'is_refinanced', 'bucket')
    search_fields = ('operation_code', 'customer__name', 'customer__document_id')
