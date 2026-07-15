import re

# Fix views.py
with open('apps/financial_planning/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Make sure we replace plans = FinancialPlan.objects.all().order_by('-start_date') 
# to plans = FinancialPlan.objects.filter(plan_type='INSTITUTIONAL').order_by('-start_date')
content = content.replace(
    'def institutional_budget_viewer(request, plan_id=None):\n    plans = FinancialPlan.objects.all().order_by(\'-start_date\')',
    'def institutional_budget_viewer(request, plan_id=None):\n    plans = FinancialPlan.objects.filter(plan_type=\'INSTITUTIONAL\').order_by(\'-start_date\')'
)

with open('apps/financial_planning/views.py', 'w', encoding='utf-8') as f:
    f.write(content)

# Fix institutional_budget.html
with open('templates/financial_planning/institutional_budget.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = html.replace(
    '<option value="{{ p.id }}">{{ p.name }} ({{ p.start_date|date:"Y" }})</option>',
    '<option value="{{ p.id }}" {% if selected_plan and p.id == selected_plan.id %}selected{% endif %}>{{ p.name }} ({{ p.start_date|date:"Y" }})</option>'
)

with open('templates/financial_planning/institutional_budget.html', 'w', encoding='utf-8') as f:
    f.write(html)
