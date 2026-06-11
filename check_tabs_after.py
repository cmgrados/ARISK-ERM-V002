with open('templates/financial_planning/institutional_budget_wizard.html', 'r', encoding='utf-8') as f:
    for line in f:
        if 'nav-link' in line and 'tab' in line:
            print(line.strip())
