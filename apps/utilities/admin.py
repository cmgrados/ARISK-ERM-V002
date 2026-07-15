from django.contrib import admin
from .models import BulkLoadLog

@admin.register(BulkLoadLog)
class BulkLoadLogAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'load_date', 'records_processed', 'status')
    list_filter = ('status', 'load_date')
    search_fields = ('file_name',)
