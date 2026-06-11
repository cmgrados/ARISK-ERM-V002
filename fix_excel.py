import os
import re

files_to_process = [
    r'c:\Users\VICTUS\Desktop\A.RISK ERM\apps\operational_risk\views.py',
    r'c:\Users\VICTUS\Desktop\A.RISK ERM\apps\utilities\views.py',
    r'c:\Users\VICTUS\Desktop\A.RISK ERM\apps\credit_risk\views.py'
]

pattern = re.compile(r'    return FileResponse\(([^,]+),\s*as_attachment=True,\s*filename=([^)]+)\)', re.MULTILINE)

for file_path in files_to_process:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    matches = pattern.findall(content)
    if not matches:
        continue
    
    def replacer(match):
        out_var = match.group(1)
        fname_var = match.group(2)
        if fname_var.startswith('"') or fname_var.startswith("'"):
            # It's a string literal like "Reporte.xlsx"
            return (
                f'    from django.http import HttpResponse\n'
                f'    _content = {out_var}.getvalue() if hasattr({out_var}, "getvalue") else {out_var}.read()\n'
                f'    response = HttpResponse(_content, content_type=\'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet\')\n'
                f'    response[\'Content-Disposition\'] = f\'attachment; filename={{{fname_var}}}\'\n'
                f'    return response'
            )
        elif fname_var.startswith('f"'):
            # It's an f-string like f"Anexo_{var}.xlsx"
            # Since fname_var already has f"...", if we put it inside f"attachment; filename={...}" it gets tricky.
            # It's easier to just do: f'attachment; filename="' + {fname_var} + '"'
            return (
                f'    from django.http import HttpResponse\n'
                f'    _content = {out_var}.getvalue() if hasattr({out_var}, "getvalue") else {out_var}.read()\n'
                f'    response = HttpResponse(_content, content_type=\'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet\')\n'
                f'    response[\'Content-Disposition\'] = \'attachment; filename="\' + {fname_var} + \'"\'\n'
                f'    return response'
            )
        else:
            # It's a variable like filename
            return (
                f'    from django.http import HttpResponse\n'
                f'    _content = {out_var}.getvalue() if hasattr({out_var}, "getvalue") else {out_var}.read()\n'
                f'    response = HttpResponse(_content, content_type=\'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet\')\n'
                f'    response[\'Content-Disposition\'] = f\'attachment; filename="{{{{{fname_var}}}}}"\'\n'
                f'    return response'
            )

    new_content = pattern.sub(replacer, content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Updated {file_path} with {len(matches)} replacements.")
