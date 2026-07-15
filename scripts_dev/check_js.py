with open('templates/financial_planning/institutional_budget.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if 'url:' in line and 'assign_institutional_budget_to_plan' in line:
        print(''.join(lines[i:i+30]))
        break
