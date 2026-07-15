$ErrorActionPreference = "Stop"

Write-Host "Creating Virtual Environment..."
python -m venv venv

Write-Host "Upgrading PIP..."
.\venv\Scripts\python.exe -m pip install --upgrade pip

Write-Host "Installing Dependencies..."
.\venv\Scripts\python.exe -m pip install django djangorestframework psycopg2-binary supabase python-dotenv celery redis pandas

Write-Host "Initializing Django Project..."
.\venv\Scripts\django-admin.exe startproject config .

Write-Host "Creating 'apps' directory..."
New-Item -ItemType Directory -Force -Path "apps"

Write-Host "Creating Core Apps..."
cd apps
..\venv\Scripts\python.exe ..\manage.py startapp core
..\venv\Scripts\python.exe ..\manage.py startapp users
..\venv\Scripts\python.exe ..\manage.py startapp catalogs
..\venv\Scripts\python.exe ..\manage.py startapp audit
..\venv\Scripts\python.exe ..\manage.py startapp utilities
..\venv\Scripts\python.exe ..\manage.py startapp attachments
..\venv\Scripts\python.exe ..\manage.py startapp dashboards
..\venv\Scripts\python.exe ..\manage.py startapp reports
..\venv\Scripts\python.exe ..\manage.py startapp risks
..\venv\Scripts\python.exe ..\manage.py startapp controls
..\venv\Scripts\python.exe ..\manage.py startapp action_plans
..\venv\Scripts\python.exe ..\manage.py startapp indicators
..\venv\Scripts\python.exe ..\manage.py startapp incidents
..\venv\Scripts\python.exe ..\manage.py startapp credit_risk
..\venv\Scripts\python.exe ..\manage.py startapp liquidity_risk
..\venv\Scripts\python.exe ..\manage.py startapp market_risk
..\venv\Scripts\python.exe ..\manage.py startapp operational_risk
..\venv\Scripts\python.exe ..\manage.py startapp compliance_risk
..\venv\Scripts\python.exe ..\manage.py startapp plaft_risk
..\venv\Scripts\python.exe ..\manage.py startapp strategic_risk
..\venv\Scripts\python.exe ..\manage.py startapp reputational_risk
..\venv\Scripts\python.exe ..\manage.py startapp ai_assistant
cd ..

Write-Host "Initialization Complete."
