from credit_risk.models import CreditOperation
from credit_risk.models import CarteraCreditoCarga

print("Starting patch...")
ops = CreditOperation.objects.all()
updated = 0
for op in ops:
    # Get corresponding carga record
    carga = CarteraCreditoCarga.objects.filter(ccr=op.operation_code, fecha_corte=op.load_date).first()
    if carga:
        op.product_name = carga.tpr
        op.credit_type = carga.tcr
        op.sbs_classification = carga.calint
        op.save(update_fields=['product_name', 'credit_type', 'sbs_classification'])
        updated += 1

print(f"Patch completed. Updated {updated} records.")
