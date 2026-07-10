import json
from financial_planning.models import PlanFinanciero, BudgetVersion
from financial_planning.services.budget_engine import BudgetEngine
from users.models import Organization, User

plan = PlanFinanciero.objects.first()
org = Organization.objects.first()
user = User.objects.first()

engine = BudgetEngine(plan, org, user)
hist_totals = engine._get_historical_er_totals()
print("Historical ER Totals:", hist_totals)

engine.sync_with_trends()

version = BudgetVersion.objects.filter(plan_financiero=plan, scenario='BASE').first()
if version:
    items = version.budgetitem_set.all()
    for item in items:
        print(f"{item.code} ({item.calc_type}): hist_annual={item.hist_annual}, m1={item.m1}")
else:
    print("No BudgetVersion found.")
