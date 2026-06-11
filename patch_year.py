import re

with open('templates/financial_planning/wizard.html', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    "const projectionStartYear = parseInt('{{ plan.start_date.year }}');",
    "const projectionStartYear = parseInt('{{ plan.start_date.year|default:\"2026\" }}'.replace(/,/g, ''));"
)

with open('templates/financial_planning/wizard.html', 'w', encoding='utf-8') as f:
    f.write(content)
