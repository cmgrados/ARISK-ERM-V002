with open('templates/financial_planning/institutional_budget.html', 'r', encoding='utf-8') as f:
    for line in f:
        if 'value="{{ p.id }}"' in line:
            print(line.strip())
