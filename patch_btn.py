import re

with open(r'c:\Users\VICTUS\Desktop\A.RISK ERM\templates\financial_planning\wizard.html', 'r', encoding='utf-8') as f:
    text = f.read()

match = re.search(r'id="btn-apply-trend"', text)
if match:
    start_tag = match.start()
    btn_start = text.rfind('<button', 0, start_tag)
    btn_end = text.find('</button>', start_tag) + 9
    
    existing_btn = text[btn_start:btn_end]
    print('Existing button:', repr(existing_btn))
    
    new_btns = existing_btn + '''
                                <button type="button" id="btn-apply-montecarlo" class="btn btn-sm btn-outline-warning font-weight-bold shadow-sm mr-3" onclick="applyMontecarloTrend()">
                                    <i class="fas fa-chart-line mr-1"></i> Simulación Montecarlo
                                </button>'''
    
    if 'id="btn-apply-montecarlo"' not in text:
        text = text[:btn_start] + new_btns + text[btn_end:]
        with open(r'c:\Users\VICTUS\Desktop\A.RISK ERM\templates\financial_planning\wizard.html', 'w', encoding='utf-8') as f:
            f.write(text)
        print('Successfully added button.')
    else:
        print('Button already exists.')
