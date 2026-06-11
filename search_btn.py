import re

with open(r'c:\Users\VICTUS\Desktop\A.RISK ERM\templates\financial_planning\wizard.html', 'r', encoding='utf-8') as f:
    text = f.read()

match = re.search(r'id="btn-apply-montecarlo"', text)
if match:
    start = max(0, match.start() - 200)
    end = min(len(text), match.start() + 200)
    print(text[start:end])
else:
    print('Not found')
