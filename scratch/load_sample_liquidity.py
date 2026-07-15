import os
import django
import sys
from datetime import date, timedelta
import random

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from liquidity_risk.models import LiabilityOperation, LiquidityMetric
from credit_risk.models import CreditOperation
from liquidity_risk.engine import process_monthly_liquidity

def load_sample_data():
    target_date = date(2026, 4, 30)
    
    # 1. Ensure some credits exist for this date
    agencies = ["LIMA", "AREQUIPA", "TRUJILLO", "CUZCO"]
    if not CreditOperation.objects.filter(load_date=target_date).exists():
        print(f"Creando créditos de muestra para {target_date}...")
        from credit_risk.models import Customer
        customer, _ = Customer.objects.get_or_create(
            document_id="00000000",
            defaults={'name': 'CLIENTE DE MUESTRA'}
        )
        for i in range(20):
            CreditOperation.objects.create(
                customer=customer,
                load_date=target_date,
                operation_code=f"CRED-{i:04d}",
                agency=random.choice(agencies),
                original_amount=random.uniform(5000, 50000),
                balance=random.uniform(1000, 45000),
                current_portfolio=random.uniform(1000, 40000),
                past_due_portfolio=random.choice([0, 0, 0, 500]),
                maturity_date=target_date + timedelta(days=random.randint(10, 720))
            )

    # 2. Clear existing liabilities for this date
    LiabilityOperation.objects.filter(load_date=target_date).delete()
    print(f"Limpiando y creando pasivos de muestra para {target_date}...")

    # 3. Create diverse liabilities
    agencies = ["LIMA", "AREQUIPA", "TRUJILLO", "CUZCO"]
    products = ["AHORRO VISTA", "PLAZO FIJO", "CTS", "DPF EMPRENDEDOR"]
    
    # Create 30 operations for multiple customers
    for i in range(30):
        customer_name = f"DEPOSITANTE {random.randint(1, 20):03d}" # Some overlap to test aggregation
        agency = random.choice(agencies)
        product = random.choice(products)
        amt = random.uniform(5000, 250000)
        
        is_savings = product == "AHORRO VISTA"
        due_date = None if is_savings else target_date + timedelta(days=random.randint(1, 500))
        
        LiabilityOperation.objects.create(
            load_date=target_date,
            agency=agency,
            opening_agency=agency,
            customer_code=f"CUST-{i:03d}",
            customer_name=customer_name,
            opening_code=f"OP-{i:03d}",
            product=product,
            currency="S/",
            amount=amt,
            balance=amt,
            due_date=due_date,
            tea=random.uniform(1, 9),
            tem=0.5,
            term=random.randint(30, 360) if not is_savings else 0
        )

    print("Datos de muestra creados. Iniciando recálculo del motor de liquidez...")
    
    # 4. Trigger the engine
    process_monthly_liquidity(target_date)
    
    print(f"¡Éxito! Proceso completado para {target_date}.")
    print("Por favor, revisa el dashboard y el análisis de brechas en el módulo de liquidez.")

if __name__ == '__main__':
    load_sample_data()
