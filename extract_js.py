import re

with open('templates/strategic_risk/controls.html', 'r', encoding='utf-8') as f:
    content = f.read()

scripts = re.findall(r'<script>(.*?)</script>', content, re.DOTALL)
if scripts:
    with open('test.js', 'w', encoding='utf-8') as f:
        f.write(scripts[-1])
