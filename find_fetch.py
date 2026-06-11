with open(r'c:\Users\VICTUS\Desktop\A.RISK ERM\templates\financial_planning\wizard.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = re.finditer(r'step7-data', text)
for m in matches:
    start = max(0, text.rfind('fetch(', 0, m.start()))
    print(text[start:start+100])
