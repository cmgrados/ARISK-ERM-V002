with open('apps/financial_planning/views.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if 'def institutional_budget_viewer(' in line:
        print(''.join(lines[i:i+10]))
        break
