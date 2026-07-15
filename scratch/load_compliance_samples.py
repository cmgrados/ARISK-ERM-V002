import os
import django
import random
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from compliance_risk.models import ComplianceRequirement, ComplianceRisk
from catalogs.models import OrganizationalUnit

def load_compliance_data():
    print("Loading detailed Peru COOPAC Compliance Risk data...")
    
    # Areas
    creditos, _ = OrganizationalUnit.objects.get_or_create(name='Gerencia de Créditos')
    contabilidad, _ = OrganizationalUnit.objects.get_or_create(name='Contabilidad y Finanzas')
    rrhh, _ = OrganizationalUnit.objects.get_or_create(name='Recursos Humanos')
    sistemas, _ = OrganizationalUnit.objects.get_or_create(name='Sistemas y TI')
    legal, _ = OrganizationalUnit.objects.get_or_create(name='Legal / Oficial de Cumplimiento')

    # Detailed Requirements from User Request
    requirements_data = [
        # SUNAT
        {
            'desc': 'No presentar declaraciones juradas anuales o presentarlas fuera de plazo.',
            'source': 'SUNAT',
            'area': contabilidad,
            'sanction': 'Multa de 1 UIT (S/ 5,150) por no presentar DJ Anual.',
            'p': 4, 'i': 3, 'cp': 2, 'ci': 3
        },
        {
            'desc': 'Errores en facturación electrónica o registros contables (Omisión de ingresos).',
            'source': 'SUNAT',
            'area': contabilidad,
            'sanction': 'Multa de hasta 50% del tributo omitido; bloqueo de cuentas en BN.',
            'p': 3, 'i': 4, 'cp': 2, 'ci': 4
        },
        # SBS
        {
            'desc': 'Incumplimiento de capital mínimo, saneamiento o límites de cartera.',
            'source': 'SBS',
            'area': creditos,
            'sanction': 'Multas de 3–5 UIT; Intervención o disolución de la COOPAC.',
            'p': 2, 'i': 5, 'cp': 1, 'ci': 5
        },
        {
            'desc': 'No presentar o presentar información inexacta del Padrón de Socios.',
            'source': 'SBS',
            'area': sistemas,
            'sanction': 'Multas y causal de disolución si se detecta pérdida de capital.',
            'p': 3, 'i': 4, 'cp': 1, 'ci': 4
        },
        # UIF
        {
            'desc': 'No presentar o presentar con errores el Informe Anual del Oficial de Cumplimiento (IAOC).',
            'source': 'UIF',
            'area': legal,
            'sanction': 'Sanción por incumplimiento grave del sistema de prevención.',
            'p': 3, 'i': 4, 'cp': 1, 'ci': 4
        },
        {
            'desc': 'No reportar operaciones sospechosas (ROS) u omisión de reportes.',
            'source': 'UIF',
            'area': legal,
            'sanction': 'Multa de hasta 3 veces el valor de las operaciones no reportadas.',
            'p': 2, 'i': 5, 'cp': 1, 'ci': 5
        },
        # INDECOPI
        {
            'desc': 'No pagar depósitos a plazo fijo o intereses en la fecha pactada.',
            'source': 'INDECOPI',
            'area': creditos,
            'sanction': 'Multas (ej. 6.16 UIT) y obligación de reparación patrimonial.',
            'p': 2, 'i': 4, 'cp': 1, 'ci': 4
        },
        {
            'desc': 'Negarse injustificadamente a entregar copias de certificados o documentos a socios.',
            'source': 'INDECOPI',
            'area': sistemas,
            'sanction': 'Multa de 1 UIT por denegación de información al consumidor.',
            'p': 3, 'i': 3, 'cp': 1, 'ci': 3
        },
        # SUNAFIL
        {
            'desc': 'Incumplimiento de aportes a pensiones (AFP/ONP) o retenciones no depositadas.',
            'source': 'SUNAFIL',
            'area': rrhh,
            'sanction': 'Multas en UIT; reparación de beneficios; posible clausura temporal.',
            'p': 3, 'i': 4, 'cp': 2, 'ci': 4
        }
    ]

    # Clear old data if needed or just update
    # ComplianceRisk.objects.all().delete()
    # ComplianceRequirement.objects.all().delete()

    for item in requirements_data:
        req, _ = ComplianceRequirement.objects.get_or_create(
            description=item['desc'],
            defaults={
                'source': item['source'], 
                'responsible_area': item['area'],
                'potential_sanction': item['sanction']
            }
        )
        
        # Create Risk entry
        ComplianceRisk.objects.get_or_create(
            requirement=req,
            defaults={
                'inherent_probability': item['p'],
                'inherent_impact': item['i'],
                'existing_controls': 'Revisiones mensuales, auditorías internas y sistemas de alerta.',
                'residual_probability': item['cp'],
                'residual_impact': item['ci'],
                'indicator': f'Tasa de cumplimiento {item["source"]}',
                'monitoring_frequency': 'MONTHLY',
                'evaluation_period': '2026'
            }
        )

    print("Success: Detailed Peru COOPAC Compliance data loaded.")

if __name__ == "__main__":
    load_compliance_data()
