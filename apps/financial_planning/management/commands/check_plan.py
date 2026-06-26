from django.core.management.base import BaseCommand
from apps.financial_planning.models import PlanFinanciero

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        p = PlanFinanciero.objects.filter(nombre='PLAN FINANCIERO 2026-2028 PRUEBA').last()
        if p:
            self.stdout.write(f'ID: {p.id}, Anio: {repr(p.anio_base)}, Horizonte: {repr(p.horizonte_anios)}')
        else:
            self.stdout.write('Plan not found')
