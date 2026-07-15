from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Información Corporativa', {'fields': ('position', 'department')}),
        ('ERM Roles', {'fields': ('is_risk_manager', 'is_auditor')}),
    )

