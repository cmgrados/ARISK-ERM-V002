import os
import re

files_to_process = [
    r'c:\Users\VICTUS\Desktop\A.RISK ERM\apps\operational_risk\views.py',
    r'c:\Users\VICTUS\Desktop\A.RISK ERM\apps\utilities\views.py',
    r'c:\Users\VICTUS\Desktop\A.RISK ERM\apps\credit_risk\views.py'
]

for file_path in files_to_process:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Fix the syntax error: `}"\'` -> `}"'`
    content = content.replace(r'}"\'', r'}"\'') # Wait, this doesn't work.
    
    # The literal string in the file is `}"\'` which means `} " \ ' `
    content = content.replace("}\"\\'", "}\"'")

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print(f"Fixed syntax error in {file_path}")
