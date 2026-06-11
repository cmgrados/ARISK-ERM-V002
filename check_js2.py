with open('templates/financial_planning/institutional_budget_wizard.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if 'document.addEventListener(' in line and 'DOMContentLoaded' in line:
        print(''.join(lines[i:i+40]))
        break
