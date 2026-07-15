with open('apps/financial_planning/views.py', 'r', encoding='utf-8') as f:
    text = f.read()

target1 = '''        variables_def = [
            {"id": "cartera", "name": "Cartera de Créditos"},
            {"id": "mora", "name": "Mora (S/)"},
            {"id": "ahorros", "name": "Ahorros y Depósitos"},
            {"id": "aportes", "name": "Aportes"},
            {"id": "socios", "name": "Número de Socios"}
        ]'''

rep1 = '''        variables_def = [
            {"id": "cartera", "name": "Cartera de Créditos"},
            {"id": "mora", "name": "Mora (S/)"},
            {"id": "ahorros_cte", "name": "Ahorro Corriente"},
            {"id": "dpf", "name": "Depósitos a Plazo Fijo (DPF)"},
            {"id": "aportes", "name": "Aportes"},
            {"id": "socios", "name": "Número de Socios"}
        ]'''

target2 = '''                periods_map[p]['ahorros'] = item.get('ahorros', 0.0) + item.get('dpf', 0.0)
                periods_map[p]['aportes'] = item.get('aportes', 0.0)'''

rep2 = '''                periods_map[p]['ahorros_cte'] = item.get('ahorros', 0.0)
                periods_map[p]['dpf'] = item.get('dpf', 0.0)
                periods_map[p]['aportes'] = item.get('aportes', 0.0)'''

target3 = '''                    item['ahorros'] = item.get('ahorros', 0.0)
                    item['aportes'] = item.get('aportes', 0.0)'''

rep3 = '''                    item['ahorros_cte'] = item.get('ahorros_cte', 0.0)
                    item['dpf'] = item.get('dpf', 0.0)
                    item['aportes'] = item.get('aportes', 0.0)'''

target4 = '''padding = [{'period': f"PAD-{i}", 'cartera': 0, 'mora': 0, 'ahorros': 0, 'aportes': 0, 'socios': 0} for i in range(pads)]'''
rep4 = '''padding = [{'period': f"PAD-{i}", 'cartera': 0, 'mora': 0, 'ahorros_cte': 0, 'dpf': 0, 'aportes': 0, 'socios': 0} for i in range(pads)]'''

# For target1, encoding issues might be present if the file had cp1252 but we opened as utf-8. We will just use regex to be safe.
import re
text = re.sub(r'\{\"id\": \"ahorros\", \"name\": \"[^\"]+\"\},', '{"id": "ahorros_cte", "name": "Ahorro Corriente"},\n            {"id": "dpf", "name": "Depósitos a Plazo Fijo (DPF)"},', text)

text = text.replace(target2, rep2)
text = text.replace(target3, rep3)
text = text.replace(target4, rep4)

with open('apps/financial_planning/views.py', 'w', encoding='utf-8') as f:
    f.write(text)
print("Views patched")
