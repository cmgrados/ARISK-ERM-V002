# -*- coding: utf-8 -*-
import os

source_dir = r"C:\Users\USER\Desktop\A.RISK ERM C1\apps\financial_planning"
dest_file = r"C:\Users\USER\.gemini\antigravity\brain\3aa937df-0aa7-49ef-8818-0de7ba5c6ce2\financial_planning_code_dump.md"

files_to_export = [
    "models.py",
    "views.py",
    "urls.py",
    "services.py",
    "apps.py",
    "admin.py",
]

with open(dest_file, "w", encoding="utf-8") as out:
    out.write("# Exportación del Módulo de Planificación Financiera\n\n")
    out.write("A continuación se encuentra el código fuente completo de los archivos clave del módulo. Puedes copiar y pegar este contenido en tu otro desarrollo con Antigravity pidiéndole: 'Antigravity, lee este documento y recrea los archivos del módulo de Planificación Financiera en mi proyecto'.\n\n")
    
    for f_name in files_to_export:
        f_path = os.path.join(source_dir, f_name)
        if os.path.exists(f_path):
            out.write(f"## Archivo: pps/financial_planning/{f_name}\n\n")
            out.write("`python\n")
            with open(f_path, "r", encoding="utf-8") as f:
                out.write(f.read())
            out.write("\n`\n\n")
            
    # Also include templates tree
    out.write("## Estructura de Templates HTML\n\n")
    out.write("`	ext\n")
    templates_dir = os.path.join(source_dir, "templates", "financial_planning")
    if os.path.exists(templates_dir):
        for root, dirs, files in os.walk(templates_dir):
            level = root.replace(templates_dir, '').count(os.sep)
            indent = ' ' * 4 * (level)
            out.write(f"{indent}{os.path.basename(root)}/\n")
            subindent = ' ' * 4 * (level + 1)
            for f in files:
                out.write(f"{subindent}{f}\n")
    out.write("`\n")

print("Exportación completa")
