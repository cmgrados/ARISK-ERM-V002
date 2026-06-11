import re

with open(r'c:\Users\VICTUS\Desktop\A.RISK ERM\templates\financial_planning\wizard.html', 'r', encoding='utf-8') as f:
    text = f.read()

# find step-8 content
match8 = re.search(r'id="step-8"', text)
if match8:
    start = max(0, match8.start() - 300)
    print(text[start:match8.start() + 100])
else:
    print('step-8 not found')
