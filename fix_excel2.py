import os
import re

files_to_process = [
    r'c:\Users\VICTUS\Desktop\A.RISK ERM\apps\operational_risk\views.py',
    r'c:\Users\VICTUS\Desktop\A.RISK ERM\apps\utilities\views.py',
    r'c:\Users\VICTUS\Desktop\A.RISK ERM\apps\credit_risk\views.py'
]

# We need to find the blocks that were incorrectly replaced.
# They look like:
#     from django.http import HttpResponse
#     _content = ...
#     response = HttpResponse(_content, ...)
#     response['Content-Disposition'] = f'attachment; filename={"Eventos_Riesgo_Operacional.xlsx"}'
#     return response

for file_path in files_to_process:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern 1: Literal string filename
    # response['Content-Disposition'] = f'attachment; filename={"Reporte.xlsx"}'
    pattern1 = re.compile(r'response\[\'Content-Disposition\'\] = f\'attachment; filename=\{"([^"]+)"\}\'')
    content = pattern1.sub(r'response[\'Content-Disposition\'] = \'attachment; filename="\1"\'', content)
    
    # Pattern 2: f-string filename with ' + f"Anexo_{var}.xlsx" + '
    # Wait, my script generated: response['Content-Disposition'] = 'attachment; filename="' + f"Anexo_{var}.xlsx" + '"'
    # Actually, let's see what it generated. In credit_risk/views.py it generated:
    # response['Content-Disposition'] = f'attachment; filename="{{filename}}"'
    # Let's fix that one.
    pattern2 = re.compile(r'response\[\'Content-Disposition\'\] = f\'attachment; filename="\{\{([^}]+)\}\}"\'')
    content = pattern2.sub(r'response[\'Content-Disposition\'] = f\'attachment; filename="{ \1 }"\'', content)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print(f"Fixed {file_path}")
