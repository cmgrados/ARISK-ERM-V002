from django.contrib import admin
from .models import OrganizationalUnit, Process, Subprocess, Product, RiskType, Parameter

admin.site.register(OrganizationalUnit)
admin.site.register(Process)
admin.site.register(Subprocess)
admin.site.register(Product)
admin.site.register(RiskType)
admin.site.register(Parameter)
