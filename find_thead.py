with open(r'c:\Users\VICTUS\Desktop\A.RISK ERM\templates\financial_planning\wizard.html', 'r', encoding='utf-8') as f:
    text = f.read()

target = text.find('id="budget-monthly-thead"')
if target != -1:
    start = max(0, text.rfind('<table', 0, target))
    end = text.find('</thead>', target) + 8
    print(text[start:end])
else:
    print('Not found')
