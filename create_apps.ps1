$ErrorActionPreference = "Stop"

Write-Host "Creating Django Project..."
.\venv\Scripts\django-admin.exe startproject config .

Write-Host "Creating apps directory..."
if (!(Test-Path -Path "apps")) {
    New-Item -ItemType Directory -Force -Path "apps"
}

cd apps

$apps = @(
    "core", "users", "catalogs", "audit", "utilities", "attachments", 
    "dashboards", "reports", "risks", "controls", "action_plans", 
    "indicators", "incidents", "credit_risk", "liquidity_risk", 
    "market_risk", "operational_risk", "compliance_risk", "plaft_risk", 
    "strategic_risk", "reputational_risk", "ai_assistant"
)

foreach ($app in $apps) {
    Write-Host "Creating app: $app"
    ..\venv\Scripts\python.exe ..\manage.py startapp $app
}

cd ..
Write-Host "All apps created successfully."
