import re

with open(r'c:\Users\VICTUS\Desktop\A.RISK ERM\templates\financial_planning\wizard.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Remove the incorrectly placed section
start_idx = text.find('<!-- Montecarlo Comparative Section -->')
if start_idx != -1:
    end_idx = text.find('</div>\n                            </div>\n                        </div>', start_idx)
    if end_idx != -1:
        end_idx += 75
        html_section = text[start_idx:end_idx]
        text = text[:start_idx] + text[end_idx:]
        
        # Now find where to insert it correctly
        target_idx = text.rfind('Guardar Supuestos')
        if target_idx != -1:
            insert_idx = text.rfind('<div class="text-center mt-4">', 0, target_idx)
            if insert_idx != -1:
                text = text[:insert_idx] + html_section + '\n\n                        ' + text[insert_idx:]
                with open(r'c:\Users\VICTUS\Desktop\A.RISK ERM\templates\financial_planning\wizard.html', 'w', encoding='utf-8') as f:
                    f.write(text)
                print('Successfully moved the montecarlo-section to the end of the table!')
            else:
                print('Could not find insert_idx')
        else:
            print('Could not find Guardar Supuestos')
    else:
        print('End of section not found')
else:
    print('Could not find Montecarlo section')
