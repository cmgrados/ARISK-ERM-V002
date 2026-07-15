import os
import django
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from credit_risk.models import CreditOperation

def normalize_classifications():
    print("Normalizando clasificaciones en la base de datos (Intento 2)...")
    
    # We will search for ANY string containing 'RDIDA' and replace it with 'Pérdida'
    # using a very explicit string.
    perdida_correct = "Pérdida"
    
    ops_to_update = CreditOperation.objects.filter(sbs_classification__icontains='RDIDA')
    count = ops_to_update.count()
    ops_to_update.update(sbs_classification=perdida_correct)
    print(f"Actualizados {count} registros que contenían 'RDIDA' -> '{perdida_correct}'")
    
    # Also handle the others just in case
    mapping = {
        'NORMAL': 'Normal',
        'DEFICIENTE': 'Deficiente',
        'DUDOSO': 'Dudoso',
        'CON PROBLEMAS POTENCIALES': 'Con Problemas Potenciales',
        'CPP': 'Con Problemas Potenciales'
    }
    
    for old, new in mapping.items():
        c = CreditOperation.objects.filter(sbs_classification__iexact=old).update(sbs_classification=new)
        if c > 0:
            print(f"Actualizados {c} registros: '{old}' -> '{new}'")

if __name__ == "__main__":
    normalize_classifications()
