from django.contrib import admin
from .models import Company, Site, OrganizationalUnit, Process, Subprocess, Product, RiskType, Parameter, Position, SystemIntegration

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'tax_id', 'headquarters', 'address')
    search_fields = ('name', 'tax_id')

@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'address', 'responsible', 'company')
    search_fields = ('code', 'name', 'address')
    list_filter = ('company',)

admin.site.register(OrganizationalUnit)
admin.site.register(Position)
admin.site.register(Process)
admin.site.register(Subprocess)
admin.site.register(Product)
admin.site.register(RiskType)
admin.site.register(Parameter)
admin.site.register(SystemIntegration)
