import re

filepath = r"c:\Users\USER\Desktop\ARISK V002\apps\utilities\views.py"
with open(filepath, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if "financial_planning" in line:
        new_lines.append("# " + line)
    else:
        new_lines.append(line)

with open(filepath, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("Fixed utilities/views.py")
