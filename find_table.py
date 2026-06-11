import re

with open(r'c:\Users\VICTUS\Desktop\A.RISK ERM\templates\financial_planning\wizard.html', 'r', encoding='utf-8') as f:
    text = f.read()

match = re.search(r'id="budget-table"', text)
if match:
    # Find the closing tag of the card body or something near the end
    end_tag = text.find('</table>', match.start())
    if end_tag != -1:
        start = max(0, end_tag - 100)
        end = min(len(text), end_tag + 300)
        print(text[start:end])
else:
    print('Not found')
