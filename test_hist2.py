from financial_planning.models import PlanFinanciero
from financial_planning.services.budget_engine import BudgetEngine
from users.models import Organization, User

plan = PlanFinanciero.objects.first()
org = Organization.objects.first()
user = User.objects.first()

engine = BudgetEngine(plan, org, user)
hist_totals = engine._get_historical_er_totals()
print("Historical ER Totals:", hist_totals)
