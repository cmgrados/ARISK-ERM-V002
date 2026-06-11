from apps.financial_planning.models import FinancialPlan
plans = FinancialPlan.objects.filter(plan_type='INSTITUTIONAL')
for p in plans:
    print(p.id, p.name, bool(p.budget_data))
    if p.budget_data:
        print("keys:", p.budget_data.keys())
        print("selected_periods:", p.budget_data.get('selected_periods'))
