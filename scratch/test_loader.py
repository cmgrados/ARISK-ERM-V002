
import os
import django
import sys

# Setup Django
sys.path.append(r'c:\Users\VICTUS\Desktop\A.RISK ERM')
sys.path.append(r'c:\Users\VICTUS\Desktop\A.RISK ERM\apps')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from liquidity_risk.models import LiqBalanceUpload, LiqAccountPlanModel, LiqLoadStatus
from liquidity_risk.loaders import process_balance_load
from django.core.files import File
from datetime import date

def test_load():
    file_path = r'C:\Users\VICTUS\Downloads\BC - MODELO 202603..xlsx'
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    # Get a plan model
    plan = LiqAccountPlanModel.objects.first()
    if not plan:
        print("No plan model found")
        return

    # Create a dummy upload
    upload = LiqBalanceUpload.objects.create(
        period=date(2026, 3, 31),
        user_id=1, # Assume user 1 exists
        status=LiqLoadStatus.PENDING,
        plan_model=plan,
        currency='MN'
    )
    
    with open(file_path, 'rb') as f:
        upload.file_source.save('test_load.xlsx', File(f))
    
    print(f"Starting process_balance_load for ID {upload.id}...")
    success = process_balance_load(upload.id)
    
    upload.refresh_from_db()
    print(f"Success: {success}")
    print(f"Status: {upload.status}")
    print(f"Observations: {upload.observations}")

if __name__ == '__main__':
    test_load()
