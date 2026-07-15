import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from credit_risk.models import CreditOperation, CreditRiskMetrics, CreditRiskPeriodParameter, Customer
from liquidity_risk.models import LiabilityOperation, LiquidityFlow, LiquidityMetric, LiquidityAlert, LiquidityParameter
from utilities.models import BulkLoadLog

def wipe_data():
    print("--- Iniciando limpieza total de datos de riesgo ---")
    
    # 1. Credit Risk
    print("Limpiando Riesgo de Crédito...")
    CreditRiskMetrics.objects.all().delete()
    CreditOperation.objects.all().delete()
    CreditRiskPeriodParameter.objects.all().delete()
    Customer.objects.all().delete()
    
    # 2. Liquidity Risk
    print("Limpiando Riesgo de Liquidez...")
    LiabilityOperation.objects.all().delete()
    LiquidityFlow.objects.all().delete()
    LiquidityMetric.objects.all().delete()
    LiquidityAlert.objects.all().delete()
    LiquidityParameter.objects.all().delete()
    
    # 3. Utilities / Logs
    print("Limpiando Historial de Cargas...")
    BulkLoadLog.objects.all().delete()
    
    print("--- Limpieza completada. El sistema está en CERO. ---")

if __name__ == "__main__":
    wipe_data()
