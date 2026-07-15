import os
import django
from datetime import date, timedelta
import random

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from credit_risk.models import Customer, CreditOperation, CreditRiskMetrics
from catalogs.models import Product

def load_test_data():
    print("Loading test data...")
    
    # Ensure some products exist
    products = list(Product.objects.all())
    if not products:
        print("Creating basic products...")
        Product.objects.get_or_create(name='Consumo Directo')
        Product.objects.get_or_create(name='Crédito MYPE')
        Product.objects.get_or_create(name='Hipotecario Vivienda')
        products = list(Product.objects.all())

    # Create some test customers
    customers_data = [
        ('10203040', 'JUAN ALBERTO PEREZ', 'MYPE', 'COMERCIO', 'NORTE'),
        ('40506070', 'MARIA LUISA GOMEZ', 'CONSUMO', 'SERVICIOS', 'SUR'),
        ('80901020', 'CARLOS ANDRES RIVERA', 'HIPOTECARIO', 'DEPENDIENTE', 'LIMA'),
        ('20304050', 'ANA LUCIA SANTOS', 'MYPE', 'PRODUCCION', 'CENTRO'),
        ('60708090', 'PEDRO PABLO CASTRO', 'CONSUMO', 'SERVICIOS', 'ORIENTE'),
    ]
    
    customers = []
    for doc, name, seg, act, zone in customers_data:
        c, _ = Customer.objects.update_or_create(
            document_id=doc,
            defaults={
                'name': name,
                'segment': seg,
                'economic_activity': act,
                'zone': zone
            }
        )
        customers.append(c)

    # Cutoff dates
    dates = [date.today() - timedelta(days=x*30) for x in range(3)]
    
    for load_date in dates:
        print(f"  Generating data for date: {load_date}")
        for i, customer in enumerate(customers):
            op_code = f"OP-{load_date.strftime('%Y%m')}-{customer.document_id[:4]}"
            
            # Use random or semi-random values
            balance = random.uniform(5000, 50000)
            rate = random.uniform(12, 35)
            term = random.choice([12, 24, 36, 48])
            
            # Determine classification based on index
            classification = 'Normal'
            if i == 3: classification = 'Deficiente'
            if i == 4: classification = 'Pérdida'
            
            op, _ = CreditOperation.objects.update_or_create(
                operation_code=op_code,
                defaults={
                    'customer': customer,
                    'product': random.choice(products),
                    'balance': balance,
                    'rate': rate,
                    'term': term,
                    'load_date': load_date,
                    'sbs_classification': classification,
                    'bucket': '0 días' if classification == 'Normal' else '30-60 días',
                    'days_past_due': 0 if classification == 'Normal' else random.randint(31, 60)
                }
            )
            
            # Create metrics
            CreditRiskMetrics.objects.update_or_create(
                operation=op,
                defaults={
                    'pd': random.uniform(0.01, 0.20),  # 1% to 20%
                    'ead': balance,
                    'lgd': random.uniform(0.10, 0.60)   # 10% to 60%
                }
            )

    print("Success: Test data loaded.")

if __name__ == "__main__":
    load_test_data()
