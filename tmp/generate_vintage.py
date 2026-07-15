import os
import django
import sys
from datetime import date
from decimal import Decimal
import random

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from credit_risk.models import Customer, CreditOperation

def get_provision(clas, bal):
    rates = {'Normal': Decimal('0.01'), 'CPP': Decimal('0.05'), 'Deficiente': Decimal('0.25'), 'Dudoso': Decimal('0.60'), 'Pérdida': Decimal('1.00')}
    return bal * rates.get(clas, Decimal('0.01'))

def generate_data():
    date1 = date(2026, 2, 28)
    date2 = date(2026, 3, 31)

    print("Limpiando registros antiguos del script anterior...")
    CreditOperation.objects.all().delete()
    Customer.objects.filter(document_id__startswith="TEST-").delete()
    
    print("Creando 500 Clientes de Prueba...")
    customers_to_create = []
    for i in range(1, 501):
        customers_to_create.append(
            Customer(
                document_id=f"TEST-{10000+i}",
                external_id=f"SOC-1{10000+i}",
                name=f"CLIENTE MASIVO {i} S.A.",
                age=random.randint(25, 65),
                gender=random.choice(['M', 'F']),
            )
        )
    Customer.objects.bulk_create(customers_to_create)
    
    customers = list(Customer.objects.filter(document_id__startswith="TEST-").order_by('id'))

    print("Generando PERIODO 1 (Corte: 28/02/2026)... (500 operaciones en estado 'Normal')")
    ops_period_1 = []
    for i, c in enumerate(customers):
        bal = Decimal(random.randint(5000, 50000))
        prov = get_provision('Normal', bal)
        op = CreditOperation(
            customer=c,
            operation_code=f"PAGARE-MASIVO-{10000+i}",
            load_date=date1,
            disbursement_date=date(2025, random.randint(1, 12), random.randint(1, 28)),
            original_amount=bal,
            balance=bal,
            rate=Decimal('20.5'),
            term=24,
            sbs_classification='Normal',
            current_portfolio=bal,
            past_due_portfolio=Decimal('0.00'),
            days_past_due=0,
            required_provision=prov,
            product_name=random.choice(['Crédito Comercial', 'Mype', 'Consumo'])
        )
        ops_period_1.append(op)
        
    CreditOperation.objects.bulk_create(ops_period_1)

    print("Generando PERIODO 2 (Corte: 31/03/2026)... (Con variables EL)")
    
    ops_period_2 = []
    for op in ops_period_1:
        scenario = random.choices(
            ['pays', 'arrears_15', 'arrears_45', 'reprogrammed', 'default'],
            weights=[0.75, 0.10, 0.05, 0.05, 0.05]
        )[0]
        
        vig = op.current_portfolio
        ven = op.past_due_portfolio
        bal = op.balance
        clas = op.sbs_classification
        dpd = op.days_past_due
        repr_vig = op.restructured_current
        
        if scenario == 'pays':
            payment = bal * Decimal('0.05')
            bal -= payment
            vig = bal
            dpd = 0
            clas = 'Normal'
        elif scenario == 'arrears_15':
            dpd = 15
            clas = 'Normal'
        elif scenario == 'arrears_45':
            dpd = 45
            clas = 'CPP'
            ven = bal
            vig = Decimal('0.00')
        elif scenario == 'reprogrammed':
            repr_vig = bal
            vig = Decimal('0.00')
            dpd = 0
            clas = 'Normal'
        elif scenario == 'default':
            dpd = 120
            clas = 'Dudoso'
            ven = bal
            vig = Decimal('0.00')
            
        prov = get_provision(clas, bal)
            
        new_op = CreditOperation(
            customer=op.customer,
            operation_code=op.operation_code,
            load_date=date2,
            disbursement_date=op.disbursement_date,
            original_amount=op.original_amount,
            balance=bal,
            rate=op.rate,
            term=op.term,
            sbs_classification=clas,
            current_portfolio=vig,
            past_due_portfolio=ven,
            restructured_current=repr_vig,
            days_past_due=dpd,
            required_provision=prov,
            product_name=op.product_name
        )
        ops_period_2.append(new_op)
        
    CreditOperation.objects.bulk_create(ops_period_2)

    print("¡Finalizado! Se han poblado carteras con Provisiones (Pérdida Esperada).")

if __name__ == "__main__":
    generate_data()
