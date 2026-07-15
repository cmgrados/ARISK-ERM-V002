import os
import sys
import django
import pandas as pd
from decimal import Decimal

# Setup Django
BASE_DIR = 'c:/Users/VICTUS/Desktop/A.RISK ERM'
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from liquidity_risk.models import LiqBalanceUpload, LiqAccountPlanModel, LiqLoadStatus
from liquidity_risk.loaders import process_balance_load
from django.contrib.auth.models import User

def run_test():
    file_path = r"C:\Users\VICTUS\Downloads\BC - MODELO 202603..xlsx"
    if not os.path.exists(file_path):
        print(f"Error: El archivo no existe en {file_path}")
        return

    print(f"Archivo encontrado: {file_path}")
    
    # Get a plan model
    plan = LiqAccountPlanModel.objects.filter(is_active=True).first()
    user = User.objects.first()
    
    # Create upload record
    # Note: We use a placeholder period, the loader should detect the real one if it exists in the file
    upload = LiqBalanceUpload.objects.create(
        period="2026-03-01",
        plan_model=plan,
        currency="MN",
        user=user,
        status=LiqLoadStatus.PENDING
    )
    
    # Manually copy file path to file_source (this is a bit hacky for testing)
    upload.file_source.name = "testing_bulk_load.xlsx"
    # We'll need to actually copy the file to the media folder if we want process_balance_load to work
    # because it uses upload.file_source.path
    import shutil
    media_path = os.path.join("c:/Users/VICTUS/Desktop/A.RISK ERM/media/liquidity/balances", "testing_bulk_load.xlsx")
    os.makedirs(os.path.dirname(media_path), exist_ok=True)
    shutil.copy(file_path, media_path)
    upload.file_source.name = "liquidity/balances/testing_bulk_load.xlsx"
    upload.save()

    print(f"Iniciando procesamiento de Upload ID: {upload.id}")
    success = process_balance_load(upload.id)
    
    # Refresh from DB
    upload.refresh_from_db()
    print(f"Resultado: {'EXITOSO' if success else 'FALLIDO'}")
    print(f"Observaciones: {upload.observations}")

if __name__ == "__main__":
    run_test()
