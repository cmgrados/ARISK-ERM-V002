import sys

# Read credit_risk views
with open('apps/credit_risk/views.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

vintage_lines = []
in_vintage = False
for line in lines:
    if line.startswith('def vintage_analysis(request):'):
        in_vintage = True
        vintage_lines.append('@login_required\ndef vintage_view(request):\n')
        continue
    if in_vintage:
        # Stop at the next function definition, except for inner functions like normalize_sbs
        if line.startswith('def ') and not line.startswith('def normalize_sbs') and not line.startswith('def normalize_cat') and not line.startswith('def beta_cdf'):
            break
        
        # Replace template
        line = line.replace("'credit_risk/vintage_analysis.html'", "'riesgo/vintage.html'")
        vintage_lines.append(line)

# Now read modulo_riesgo_credito views
with open('apps/modulo_riesgo_credito/views.py', 'r', encoding='utf-8') as f:
    mod_lines = f.readlines()

new_mod_lines = []
skip = False
i = 0
while i < len(mod_lines):
    line = mod_lines[i]
    if line.startswith('@login_required') and i+1 < len(mod_lines) and mod_lines[i+1].startswith('def vintage_view'):
        skip = True
    elif line.startswith('def vintage_view(request):'):
        skip = True
    elif skip and line.startswith('@login_required'): # next function
        skip = False
        new_mod_lines.append(line)
    elif not skip:
        new_mod_lines.append(line)
    i += 1

with open('apps/modulo_riesgo_credito/views.py', 'w', encoding='utf-8') as f:
    f.writelines(new_mod_lines)
    f.write('\n')
    f.writelines(vintage_lines)

print("Done")
