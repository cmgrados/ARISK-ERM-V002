import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from risks.models import ProbabilityScale, ImpactScale, RiskMatrixConfiguration

def populate():
    # 1. Probability Scales
    probs = [
        (1, 'Muy Raro', 'Evento que puede ocurrir solo en circunstancias excepcionales.'),
        (2, 'Improbable', 'Evento que puede ocurrir en algún momento.'),
        (3, 'Posible', 'Evento que debería ocurrir en algún momento.'),
        (4, 'Probable', 'Evento que probablemente ocurrirá en la mayoría de las circunstancias.'),
        (5, 'Casi Seguro', 'Evento que se espera que ocurra en la mayoría de las circunstancias.'),
    ]
    
    p_objs = {}
    for val, name, desc in probs:
        obj, _ = ProbabilityScale.objects.get_or_create(value=val, defaults={'name': name, 'description': desc})
        p_objs[val] = obj

    # 2. Impact Scales
    impacts = [
        (1, 'Insignificante', 'Sin impacto financiero o reputacional detectable.'),
        (2, 'Menor', 'Impacto financiero bajo, afectación mínima a procesos.'),
        (3, 'Moderado', 'Impacto financiero medio, afectación a procesos clave.'),
        (4, 'Mayor', 'Impacto financiero alto, daño reputacional significativo.'),
        (5, 'Catastrófico', 'Pérdida financiera masiva, inviabilidad del negocio.'),
    ]
    
    i_objs = {}
    for val, name, desc in impacts:
        obj, _ = ImpactScale.objects.get_or_create(value=val, defaults={'name': name, 'description': desc})
        i_objs[val] = obj

    # 3. Matrix Configuration (5x5)
    # Simple logic for colors
    for p_val in range(1, 6):
        for i_val in range(1, 6):
            score = p_val * i_val
            
            if score >= 15:
                level = 'RED'
            elif score >= 9:
                level = 'ORANGE'
            elif score >= 4:
                level = 'YELLOW'
            else:
                level = 'GREEN'
                
            RiskMatrixConfiguration.objects.get_or_create(
                probability=p_objs[p_val],
                impact=i_objs[i_val],
                defaults={'severity_level': level, 'score': score}
            )

    print("Scales and Matrix Configuration populated successfully.")

if __name__ == '__main__':
    populate()
