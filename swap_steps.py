with open('templates/financial_planning/wizard.html', 'r', encoding='utf8') as f:
    text = f.read()

# Replace titles in nav
text = text.replace('title="Balance General Proyectado">', 'title="PLACEHOLDER_BG">')
text = text.replace('title="Estado de Resultados Proyectado">', 'title="PLACEHOLDER_ER">')
text = text.replace('8. BG Proyectado', '8. PLACEHOLDER_BG')
text = text.replace('9. ER Proyectado', '9. PLACEHOLDER_ER')

text = text.replace('title="PLACEHOLDER_BG">', 'title="Estado de Resultados Proyectado">')
text = text.replace('title="PLACEHOLDER_ER">', 'title="Balance General Proyectado">')
text = text.replace('8. PLACEHOLDER_BG', '8. ER Proyectado')
text = text.replace('9. PLACEHOLDER_ER', '9. BG Proyectado')

# Replace the step includes
text = text.replace("{% include 'financial_planning/projected_balance.html' %}", "{% include 'financial_planning/PLACEHOLDER_BG.html' %}")
text = text.replace("{% include 'financial_planning/projected_income.html' %}", "{% include 'financial_planning/PLACEHOLDER_ER.html' %}")

text = text.replace("{% include 'financial_planning/PLACEHOLDER_BG.html' %}", "{% include 'financial_planning/projected_income.html' %}")
text = text.replace("{% include 'financial_planning/PLACEHOLDER_ER.html' %}", "{% include 'financial_planning/projected_balance.html' %}")

with open('templates/financial_planning/wizard.html', 'w', encoding='utf8') as f:
    f.write(text)
print('Done wizard.html')
