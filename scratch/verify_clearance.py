import os
import sys
import django

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from credit_risk.models import CreditOperation, Customer
from compliance_risk.models import ComplianceRisk, ComplianceRequirement

print(f"Clientes: {Customer.objects.count()}")
print(f"Operaciones: {CreditOperation.objects.count()}")
print(f"Requisitos Compliance: {ComplianceRequirement.objects.count()}")
print(f"Riesgos Compliance: {ComplianceRisk.objects.count()}")
