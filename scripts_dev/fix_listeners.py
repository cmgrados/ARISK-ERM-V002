with open('templates/financial_planning/wizard.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

to_delete_start = -1
to_delete_end = -1

for i, l in enumerate(lines):
    if "$('#btn-apply-trend').off('click').on('click', function() {" in l:
        to_delete_start = i
    if to_delete_start != -1 and "btnGroup.append(btn);" in l:
        to_delete_end = i - 3
        break

extracted = lines[to_delete_start:to_delete_end+1]
print('Extracting lines', to_delete_start, 'to', to_delete_end)
print('Length of extracted:', len(extracted))

# Remove extracted lines
new_lines = lines[:to_delete_start] + lines[to_delete_end+1:]

insert_idx = -1
for i, l in enumerate(new_lines):
    if "$('#trend-agency-select').on('change'" in l:
        insert_idx = i
        break

if insert_idx == -1:
    print('Could not find insert index')
else:
    # re-indent
    reindented = []
    for l in extracted:
        if l.startswith('                        '):
            reindented.append(l[8:])
        else:
            reindented.append(l)

    final_lines = new_lines[:insert_idx] + reindented + new_lines[insert_idx:]
    with open('templates/financial_planning/wizard.html', 'w', encoding='utf-8') as f:
        f.writelines(final_lines)
    print('Successfully moved the event listeners')
