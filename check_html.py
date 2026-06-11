with open(r'c:\Users\VICTUS\Desktop\A.RISK ERM\templates\financial_planning\wizard.html', 'r', encoding='utf-8') as f:
    text = f.read()
target = text.find('div class="d-flex align-items-center">')
if target != -1:
    print(text[target-200:target+200])
