from django.contrib import admin
from .models import ActionPlan, ActionFollowUp

@admin.register(ActionPlan)
class ActionPlanAdmin(admin.ModelAdmin):
    list_display = ('title', 'responsible', 'due_date', 'status', 'progress')
    list_filter = ('status', 'responsible')
    search_fields = ('title', 'description')
    date_hierarchy = 'due_date'

@admin.register(ActionFollowUp)
class ActionFollowUpAdmin(admin.ModelAdmin):
    list_display = ('action_plan', 'follow_up_date', 'performed_by')
    list_filter = ('follow_up_date',)
