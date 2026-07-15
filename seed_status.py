import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.op_risk.models import RiskStatus

RiskStatus.objects.get_or_create(code='DRAFT', defaults={'name': 'Borrador'})
RiskStatus.objects.get_or_create(code='REVIEW', defaults={'name': 'En Revisión'})
RiskStatus.objects.get_or_create(code='APPROVED', defaults={'name': 'Aprobado'})
RiskStatus.objects.get_or_create(code='CLOSED', defaults={'name': 'Cerrado'})
print("Seed complete.")
