from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('ERM Roles', {'fields': ('is_risk_manager', 'is_auditor', 'role')}),
        ('Acceso a Módulos (Legacy / Manual)', {'fields': (
            'can_access_integral_risk_flag', 
            'can_access_financial_planning_flag', 
            'can_access_strategic_planning_flag'
        )}),
    )
