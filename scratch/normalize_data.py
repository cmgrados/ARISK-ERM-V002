import os
import django
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from credit_risk.models import CreditOperation

def normalize_classifications():
    print("Normalizando clasificaciones en la base de datos...")
    
    mapping = {
        'NORMAL': 'Normal',
        'CON PROBLEMAS POTENCIALES': 'Con Problemas Potenciales',
        'CPP': 'Con Problemas Potenciales',
        'DEFICIENTE': 'Deficiente',
        'DUDOSO': 'Dudoso',
        'PRDIDA': 'Pérdida',
        'PERDIDA': 'Pérdida',
        'PÉRDIDA': 'Pérdida',
    }
    
    for old, new in mapping.items():
        count = CreditOperation.objects.filter(sbs_classification__iexact=old).update(sbs_classification=new)
        if count > 0:
            print(f"Actualizados {count} registros: '{old}' -> '{new}'")
            
    # Catch any remaining encoding issues with 'Pérdida'
    # The output from my previous check showed 'PRDIDA'
    # Let's try to match it by searching for a partial string if possible or using regex
    
    ops = CreditOperation.objects.all()
    updated_any = 0
    for op in ops:
        normalized = op.sbs_classification.upper().strip()
        if 'RDIDA' in normalized: # Catch PRDIDA, PERDIDA, etc.
            if op.sbs_classification != 'Pérdida':
                op.sbs_classification = 'Pérdida'
                op.save()
                updated_any += 1
        elif normalized == 'NORMAL':
            if op.sbs_classification != 'Normal':
                op.sbs_classification = 'Normal'
                op.save()
                updated_any += 1
        elif normalized == 'DEFICIENTE':
            if op.sbs_classification != 'Deficiente':
                op.sbs_classification = 'Deficiente'
                op.save()
                updated_any += 1
        elif normalized == 'DUDOSO':
            if op.sbs_classification != 'Dudoso':
                op.sbs_classification = 'Dudoso'
                op.save()
                updated_any += 1
        elif 'POTENCIALES' in normalized or normalized == 'CPP':
            if op.sbs_classification != 'Con Problemas Potenciales':
                op.sbs_classification = 'Con Problemas Potenciales'
                op.save()
                updated_any += 1
                
    print(f"Finalizado. Registros actualizados adicionalmente: {updated_any}")

if __name__ == "__main__":
    normalize_classifications()
