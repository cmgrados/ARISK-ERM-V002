with open('templates/financial_planning/institutional_budget_wizard.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if 'function budgetFetchData(' in line:
        print(''.join(lines[i:i+50]))
        break
