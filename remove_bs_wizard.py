with open('templates/financial_planning/institutional_budget_wizard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the nav-item for budget-bs-tab
import re
content = re.sub(
    r'<li class="nav-item">\s*<a class="nav-link(?: active)?" id="budget-bs-tab"[^>]+>.*?Situacin Financiera.*?</a>\s*</li>',
    '',
    content,
    flags=re.IGNORECASE | re.DOTALL
)
content = re.sub(
    r'<li class="nav-item">\s*<a class="nav-link(?: active)?" id="budget-bs-tab"[^>]+>.*?Situación Financiera.*?</a>\s*</li>',
    '',
    content,
    flags=re.IGNORECASE | re.DOTALL
)

# Make the is-tab active
content = content.replace('id="budget-is-tab"', 'id="budget-is-tab" class="nav-link active"')
content = content.replace('class="nav-link active" id="budget-is-tab" class="nav-link active"', 'class="nav-link active" id="budget-is-tab"')
content = content.replace('class="nav-link" id="budget-is-tab" class="nav-link active"', 'class="nav-link active" id="budget-is-tab"')

# Remove the budget-bs-panel
content = re.sub(
    r'<div class="tab-pane fade show active" id="budget-bs-panel" role="tabpanel" aria-labelledby="budget-bs-tab">.*?</div>\s*(?=<!-- Estado de Resultados Accum -->)',
    '',
    content,
    flags=re.IGNORECASE | re.DOTALL
)
content = re.sub(
    r'<div class="tab-pane fade show active" id="budget-bs-panel" role="tabpanel" aria-labelledby="budget-bs-tab">.*?(<div class="tab-pane fade" id="budget-is-panel")',
    r'\1',
    content,
    flags=re.IGNORECASE | re.DOTALL
)

# Make budget-is-panel active
content = content.replace('<div class="tab-pane fade" id="budget-is-panel"', '<div class="tab-pane fade show active" id="budget-is-panel"')

with open('templates/financial_planning/institutional_budget_wizard.html', 'w', encoding='utf-8') as f:
    f.write(content)
