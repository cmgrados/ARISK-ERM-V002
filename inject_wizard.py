import sys
wizard = open(r'templates\financial_planning\wizard.html', encoding='utf-8').read()
budget_block = open('processed_budget2.html', encoding='utf-8').read()

import re
# We need to replace everything from {% if step == 7 %} to the {% endif %} before {% if step == 8 %}
pattern = re.compile(r'{% if step == 7 %}.*?(?={% if step == 8 %})', re.DOTALL)

# Let's wrap the budget_block with {% if step == 7 %} and {% endif %}
replacement = "{% if step == 7 %}\n" + budget_block + "\n                {% endif %}\n\n                <!-- STEP 8"

wizard_new = pattern.sub(replacement.replace('<!-- STEP 8', ''), wizard)
open(r'templates\financial_planning\wizard.html', 'w', encoding='utf-8').write(wizard_new)
print('Done injecting')
