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

    # Remove the backslashes
    content = content.replace("response[\\'Content-Disposition\\'] = \\'attachment; filename=", "response['Content-Disposition'] = 'attachment; filename=")
    content = content.replace("xlsx\"\\'", "xlsx\"'")
    
    # Let's just do a clean replace using standard string manipulation
    content = content.replace(r"response[\'Content-Disposition\'] = \'attachment; filename=", "response['Content-Disposition'] = 'attachment; filename=")
    content = content.replace(r".xlsx\"\'", ".xlsx\"'")
    
    # For the f-string ones
    content = content.replace(r"response[\'Content-Disposition\'] = f\'attachment; filename=", "response['Content-Disposition'] = f'attachment; filename=")
    content = content.replace(r"}\"\'", "}\"'")

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print(f"Cleaned {file_path}")
