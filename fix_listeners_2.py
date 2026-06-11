with open('templates/financial_planning/wizard.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_idx = -1
end_idx = -1

for i, l in enumerate(lines):
    if "$('#btn-apply-trend').off('click').on('click', function() {" in l:
        start_idx = i
    if start_idx != -1 and "btn.html(originalHtml);" in l:
        # the end of complete function
        end_idx = i + 5 # up to line 1753 `});`
        break

if start_idx == -1 or end_idx == -1:
    print("Could not find block!")
else:
    extracted = lines[start_idx:end_idx+1]
    lines_new = lines[:start_idx] + lines[end_idx+1:]
    
    insert_idx = -1
    for i, l in enumerate(lines_new):
        if "selectAgency.on('change', function() {" in l:
            insert_idx = i
            break
            
    if insert_idx == -1:
        print("Could not find insert index!")
    else:
        # Dedent the extracted lines
        reindented = []
        for l in extracted:
            if l.startswith('                        '):
                reindented.append(l[8:])
            else:
                reindented.append(l)
                
        final = lines_new[:insert_idx] + reindented + lines_new[insert_idx:]
        with open('templates/financial_planning/wizard.html', 'w', encoding='utf-8') as f:
            f.writelines(final)
        print("Successfully moved handlers!")
