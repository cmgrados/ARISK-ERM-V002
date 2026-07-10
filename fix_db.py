from financial_planning.models import PlanFinanciero, BudgetCalculationRule
from financial_planning.services.budget_engine import BudgetEngine
from users.models import Organization, User

plan = PlanFinanciero.objects.first()
org = Organization.objects.first()
user = User.objects.first()

print("Fixing calculation_type...")
updated = BudgetCalculationRule.objects.filter(calculation_type='GROWTH_VARIABLE').update(calculation_type='TREND')
print(f"Updated {updated} rules.")

engine = BudgetEngine(plan, org, user)
engine._ensure_default_items()
engine.sync_with_trends()
print("Sync with trends complete.")
