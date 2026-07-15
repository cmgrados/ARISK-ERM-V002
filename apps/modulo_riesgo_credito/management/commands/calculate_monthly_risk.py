from django.core.management.base import BaseCommand
from credit_risk.models import CreditOperation
from modulo_riesgo_credito.models import RiskClassification
from modulo_riesgo_credito.services.provisioning import determine_sbs_classification, calculate_required_provision
from modulo_riesgo_credito.analytics.credit_metrics import calculate_ead, calculate_lgd, get_base_pd, calculate_expected_loss
from django.utils import timezone
from decimal import Decimal

class Command(BaseCommand):
    help = 'Calcula PD, LGD, EAD, Pérdida Esperada y Provisiones para la foto del mes actual.'

    def add_arguments(self, parser):
        parser.add_argument('--date', type=str, help='Fecha de corte (YYYY-MM-DD)')

    def handle(self, *args, **options):
        # En una versión real, esto buscaría la última load_date de CreditOperation
        date_str = options.get('date')
        if date_str:
            target_date = date_str
            operations = CreditOperation.objects.filter(load_date=target_date)
        else:
            operations = CreditOperation.objects.all() # Esto en prod debería filtrar por la fecha más reciente
            target_date = timezone.now().date()
            if operations.exists():
                target_date = operations.order_by('-load_date').first().load_date
                operations = CreditOperation.objects.filter(load_date=target_date)

        total_ops = operations.count()
        self.stdout.write(f"Iniciando cálculo para {total_ops} operaciones en el corte {target_date}...")

        classifications_to_create = []

        for op in operations:
            # Lógica
            days_pd = op.days_past_due
            classification = determine_sbs_classification(days_pd, op.is_refinanced)
            
            # Métricas
            ead = calculate_ead(op.balance, op.interest_receivable)
            lgd = calculate_lgd(op.guarantee_value, ead)
            pd = get_base_pd(classification, days_pd)
            expected_loss = calculate_expected_loss(pd, lgd, ead)
            
            req_prov = calculate_required_provision(ead, classification)
            
            # Buckets
            if days_pd == 0:
                bucket = 'Bucket 0'
            elif days_pd <= 30:
                bucket = 'Bucket 1'
            elif days_pd <= 60:
                bucket = 'Bucket 2'
            elif days_pd <= 90:
                bucket = 'Bucket 3'
            else:
                bucket = 'Bucket 4'
                
            # Preservación
            snapshot = {
                'balance': float(op.balance),
                'interest': float(op.interest_receivable),
                'guarantee': float(op.guarantee_value),
                'is_refinanced': op.is_refinanced
            }
            
            # Instanciar histórico
            classifications_to_create.append(
                RiskClassification(
                    operation=op,
                    cut_off_date=target_date,
                    bucket=bucket,
                    days_past_due=days_pd,
                    sbs_classification=classification,
                    pd=pd,
                    lgd=lgd,
                    ead=ead,
                    expected_loss=expected_loss,
                    required_provision=req_prov,
                    snapshot_data=snapshot
                )
            )

        # Bulk create / Update
        RiskClassification.objects.filter(cut_off_date=target_date).delete() # Limpieza previa
        RiskClassification.objects.bulk_create(classifications_to_create, batch_size=2000)

        self.stdout.write(self.style.SUCCESS(f"Éxito: {len(classifications_to_create)} clasificaciones guardadas."))
