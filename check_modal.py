with open('templates/financial_planning/institutional_budget.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if 'id="assignPlanSelector"' in line:
        print(''.join(lines[i-5:i+10]))
        break
