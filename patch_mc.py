import re
with open(r'c:\Users\VICTUS\Desktop\A.RISK ERM\apps\financial_planning\views.py', 'r', encoding='utf-8') as f:
    text = f.read()

pattern = re.compile(r"        for item in source_data\['income_statement'\]:\n.*?arr = np\.array\(vals, dtype=float\)", re.DOTALL)

new_mc = """        for item in source_data['income_statement']:
            if isinstance(item, dict):
                code = item.get('code')
                balances = item.get('balances', {})
                sorted_periods = sorted(selected_periods)
                vals = [balances.get(p, 0.0) for p in sorted_periods]
            else:
                code_str = str(item[0])
                code = code_str.split(' - ')[0].strip()
                sorted_periods = sorted(selected_periods)
                vals = item[1:]
                
            if len(vals) < 2:
                trends[code] = {'base': [], 'pesimista': [], 'optimista': []}
                continue
                
            arr = np.array(vals, dtype=float)"""

text, count = pattern.subn(new_mc, text)

with open(r'c:\Users\VICTUS\Desktop\A.RISK ERM\apps\financial_planning\views.py', 'w', encoding='utf-8') as f:
    f.write(text)

print(f"views patched {count} times")
