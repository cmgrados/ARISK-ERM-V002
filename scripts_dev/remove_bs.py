import re

def modify_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the nav tab for balance-sheet
    tab_pattern = r'<li class="nav-item">\s*<a class="nav-link active" id="balance-sheet-tab".*?</li>'
    content = re.sub(tab_pattern, '', content, flags=re.DOTALL)

    # Change the income-statement tab to be active
    content = content.replace(
        '<a class="nav-link" id="income-statement-tab"',
        '<a class="nav-link active" id="income-statement-tab"'
    )
    content = content.replace(
        'href="#income-statement-panel" role="tab" aria-selected="false"',
        'href="#income-statement-panel" role="tab" aria-selected="true"'
    )

    # Remove the balance sheet panel
    panel_pattern = r'<!-- Balance Sheet Panel -->\s*<div class="tab-pane fade show active" id="balance-sheet-panel" role="tabpanel">.*?<!-- Income Statement Panel -->'
    content = re.sub(panel_pattern, '<!-- Income Statement Panel -->', content, flags=re.DOTALL)

    # Make the income statement panel active
    content = content.replace(
        '<div class="tab-pane fade" id="income-statement-panel" role="tabpanel">',
        '<div class="tab-pane fade show active" id="income-statement-panel" role="tabpanel">'
    )
    
    # We also might have tabs named differently in wizard
    # Let's check budget-balance-general
    tab_pattern_2 = r'<li class="nav-item">\s*<a class="nav-link active" id="budget-balance-general-tab".*?</li>'
    content = re.sub(tab_pattern_2, '', content, flags=re.DOTALL)
    
    content = content.replace(
        '<a class="nav-link" id="budget-er-acumulado-tab"',
        '<a class="nav-link active" id="budget-er-acumulado-tab"'
    )
    content = content.replace(
        'href="#budget-er-acumulado" role="tab" aria-selected="false"',
        'href="#budget-er-acumulado" role="tab" aria-selected="true"'
    )
    
    panel_pattern_2 = r'<!-- Balance General -->\s*<div class="tab-pane fade show active" id="budget-balance-general" role="tabpanel".*?<!-- Estado de Resultados Acumulado -->'
    content = re.sub(panel_pattern_2, '<!-- Estado de Resultados Acumulado -->', content, flags=re.DOTALL)
    
    content = content.replace(
        '<div class="tab-pane fade" id="budget-er-acumulado" role="tabpanel"',
        '<div class="tab-pane fade show active" id="budget-er-acumulado" role="tabpanel"'
    )

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print(f"Modified {filepath}")

modify_file('templates/financial_planning/institutional_budget.html')
modify_file('templates/financial_planning/institutional_budget_wizard.html')
