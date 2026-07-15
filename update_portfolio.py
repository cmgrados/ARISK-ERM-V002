import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from credit_risk.models import CreditOperation, CarteraCreditoCarga
from django.db import transaction

def run():
    print("Fetching CarteraCreditoCarga...")
    cargas = {c.ccr: c for c in CarteraCreditoCarga.objects.all()}
    print(f"Loaded {len(cargas)} rows from CarteraCreditoCarga.")

    ops_to_update = []
    print("Updating CreditOperations...")
    for op in CreditOperation.objects.all():
        carga = cargas.get(op.operation_code)
        if carga:
            op.required_provision = carga.pvr
            op.established_provision = carga.pci
            op.refinanced_current = carga.krf
            op.restructured_current = carga.kre
            op.current_portfolio = carga.kvi
            op.past_due_portfolio = carga.kve
            op.judicial_portfolio = carga.kju
            op.is_refinanced = (carga.krf > 0)
            ops_to_update.append(op)
    
    with transaction.atomic():
        CreditOperation.objects.bulk_update(ops_to_update, [
            'required_provision', 'established_provision', 'refinanced_current',
            'restructured_current', 'current_portfolio', 'past_due_portfolio',
            'judicial_portfolio', 'is_refinanced'
        ], batch_size=2000)
    print(f"Updated {len(ops_to_update)} rows.")

if __name__ == '__main__':
    run()
