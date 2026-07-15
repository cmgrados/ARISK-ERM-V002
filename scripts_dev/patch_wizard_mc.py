with open('templates/financial_planning/wizard.html', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

import re

# Update width for iteration input
text = re.sub(
    r'id="mc-iterations" class="form-control form-control-sm border-secondary text-center mr-1" value="1000" style="width: 70px;',
    'id="mc-iterations" class="form-control form-control-sm border-secondary text-center mr-1" value="100000" style="width: 100px;',
    text
)

# Update the JS logic
js_target = '''                        $('#btn-apply-trend').off('click').on('click', function() {
                            showTrendCols = !showTrendCols;
                            renderMonthlyTable(currentAgency, currentVariable, currentPeriod);
                        });'''

js_rep = '''                        $('#btn-apply-trend').off('click').on('click', function() {
                            showTrendCols = !showTrendCols;
                            if (showTrendCols) {
                                showMCCols = false; // Hide Montecarlo when showing trend
                                mcDataObj = {};     // Clear simulated data
                            }
                            renderMonthlyTable(currentAgency, currentVariable, currentPeriod);
                        });'''

text = text.replace(js_target, js_rep)

with open('templates/financial_planning/wizard.html', 'w', encoding='utf-8') as f:
    f.write(text)
print('Done!')
