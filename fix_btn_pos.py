import re

with open(r'c:\Users\VICTUS\Desktop\A.RISK ERM\templates\financial_planning\wizard.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Remove the wrong button (at the first occurrence)
wrong_btn_str = '''
                                <button type="button" id="btn-apply-montecarlo" class="btn btn-sm btn-outline-warning font-weight-bold shadow-sm mr-3" onclick="applyMontecarloTrend()">
                                    <i class="fas fa-chart-line mr-1"></i> Simulación Montecarlo
                                </button>'''
text = text.replace(wrong_btn_str, '')

# Now find the correct "Aplicar Tendencia" which has onclick="applyHistoricalTrend()"
match = re.search(r'onclick="applyHistoricalTrend\(\)".*?>\s*<i class="fas fa-history mr-1"></i> Aplicar Tendencia.*?A[ñ]o Anterior\s*</button>', text, flags=re.DOTALL)

if match:
    end_tag = match.end()
    
    new_btns = '''
                                <button type="button" id="btn-apply-montecarlo" class="btn btn-sm btn-outline-warning font-weight-bold shadow-sm mr-3" onclick="applyMontecarloTrend()">
                                    <i class="fas fa-chart-line mr-1"></i> Simulación Montecarlo
                                </button>'''
    
    text = text[:end_tag] + new_btns + text[end_tag:]
    with open(r'c:\Users\VICTUS\Desktop\A.RISK ERM\templates\financial_planning\wizard.html', 'w', encoding='utf-8') as f:
        f.write(text)
    print('Successfully added button to the right place.')
else:
    print('Could not find the correct button to append to.')
