from financial_planning.models import PlanFinanciero, BudgetVersion, BudgetLine
from financial_planning.services.budget_engine import BudgetEngine
from users.models import Organization, User

plan = PlanFinanciero.objects.first()
org = Organization.objects.first()
user = User.objects.first()

engine = BudgetEngine(plan, org, user)
engine.sync_with_trends()

version = BudgetVersion.objects.filter(plan_financiero=plan, scenario='BASE').first()
if version:
    lines = BudgetLine.objects.filter(version=version)
    print("Found lines:", lines.count())
    for line in lines:
        if line.hist_annual > 0:
            print(f"{line.budget_item.code} ({line.calc_type}): hist_annual={line.hist_annual}, m1={line.m1}")
else:
    print("No BudgetVersion found.")
