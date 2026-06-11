import re

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the nav tabs
    nav_tabs_pattern = r'(<ul class="nav nav-tabs custom-tabs border-0".*?>\s*)(<li class="nav-item">.*?<a class="nav-link active".*?href="#budget-balance-general".*?>.*?</a>\s*</li>)(.*?</ul>)'
    match = re.search(nav_tabs_pattern, content, re.DOTALL)
    
    if match:
        print(f"Found tabs in {filepath}")
        new_nav = match.group(1) + match.group(3)
        # We also need to make the next tab (ER Acumulado) active since we removed the first one
        new_nav = new_nav.replace('href="#budget-er-acumulado"', 'href="#budget-er-acumulado" class="nav-link active"')
        new_nav = new_nav.replace('class="nav-link"', '', 1) # Might be messy, let's just do a direct replace
        
        # Simpler approach:
        content = re.sub(
            r'<li class="nav-item">\s*<a class="nav-link active" id="budget-balance-general-tab" data-toggle="pill" href="#budget-balance-general".*?</a>\s*</li>',
            '', content, flags=re.DOTALL
        )
        content = content.replace('class="nav-link"', 'class="nav-link active"', 1)
        
        # Remove the tab content pane for balance general
        content = re.sub(
            r'<div class="tab-pane fade show active" id="budget-balance-general" role="tabpanel" aria-labelledby="budget-balance-general-tab">\s*<div class="card shadow-sm border-0 rounded-lg">.*?</div>\s*</div>\s*<!-- Estado de Resultados Acumulado -->',
            '<!-- Estado de Resultados Acumulado -->', content, flags=re.DOTALL
        )
        
        # Make ER Acumulado active
        content = content.replace(
            '<div class="tab-pane fade" id="budget-er-acumulado"',
            '<div class="tab-pane fade show active" id="budget-er-acumulado"'
        )
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {filepath}")
    else:
        print(f"Tabs not found in {filepath}")
        
    return content

c1 = process_file('templates/financial_planning/institutional_budget_wizard.html')
c2 = process_file('templates/financial_planning/institutional_budget_viewer.html')

