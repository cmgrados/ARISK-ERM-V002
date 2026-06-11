with open('templates/financial_planning/wizard.html', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

import re

text = re.sub(
    r'id="mc-iterations" class="form-control form-control-sm border-secondary text-center mr-1" value="100000" style="width: 100px;',
    'id="mc-iterations" class="form-control form-control-sm border-secondary text-center mr-1" value="100000" style="width: 140px; min-width: 140px;',
    text
)

with open('templates/financial_planning/wizard.html', 'w', encoding='utf-8') as f:
    f.write(text)
print('Done!')
