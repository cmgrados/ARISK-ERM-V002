import re
import subprocess

with open(r'c:\Users\VICTUS\Desktop\A.RISK ERM\templates\financial_planning\wizard.html', 'r', encoding='utf-8') as f:
    html = f.read()

scripts = re.findall(r'<script>(.*?)</script>', html, re.DOTALL)

for i, s in enumerate(scripts):
    # Avoid generating double quotes when already quoted
    s = re.sub(r'\"\{%.*?%\}\"', '\"URL\"', s)
    s = re.sub(r'\'\{%.*?%\}\'', '\'URL\'', s)
    s = re.sub(r'\{%.*?%\}', 'URL', s) # bare url
    
    s = re.sub(r'\"\{\{.*?\}\}\"', '\"VAR\"', s)
    s = re.sub(r'\'\{\{.*?\}\}\'', '\'VAR\'', s)
    s = re.sub(r'\{\{.*?\}\}', 'VAR', s) # bare var
    
    filename = f'script_{i}_clean.js'
    with open(filename, 'w', encoding='utf-8') as out:
        out.write(s)
    
    print(f'Checking script {i}...')
    result = subprocess.run(['node', '-c', filename], capture_output=True, text=True)
    if result.returncode != 0:
        print(f'Error in script {i}:')
        print(result.stderr)
        
print('Done!')
