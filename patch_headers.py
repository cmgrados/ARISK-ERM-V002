import re

with open('templates/financial_planning/wizard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Refactor header generation into a function
old_headers = """                            // Generate headers
                            let theadHtml = `
                                <tr>
                                    <th style="width: 120px;">Código</th>
                                    <th style="width: 350px;">Descripción</th>
                                    <th class="text-right" style="width: 100px;">Dic-${prevYearShort}</th>
                                    <th class="text-center" style="width: 100px;">Var (%)</th>
                            `;
                            months.forEach(m => {
                                theadHtml += `<th class="text-right" style="width: 100px;">${m}-${projYearShort}</th>`;
                            });
                            theadHtml += `<th class="text-right" style="width: 120px;">Total ${projYearFull}</th></tr>`;
                            $('#budget-monthly-thead').html(theadHtml);
                            
                            let summaryTheadHtml = theadHtml.replace('<th style="width: 120px;">Código</th>', '').replace('<th style="width: 350px;">Descripción</th>', '<th colspan="2">Concepto</th>');
                            $('#budget-summary-thead').html(summaryTheadHtml);"""

new_headers = """                            // Generate headers
                            window.renderStep7Headers = function() {
                                const yrFull = projectionStartYear + activeYearIndex;
                                const yrShort = String(yrFull).slice(-2);
                                const pyFull = yrFull - 1;
                                const pyShort = String(pyFull).slice(-2);
                                
                                let theadHtml = `
                                    <tr>
                                        <th style="width: 120px;">Código</th>
                                        <th style="width: 350px;">Descripción</th>
                                        <th class="text-right" style="width: 100px;">Dic-${pyShort}</th>
                                        <th class="text-center" style="width: 100px;">Var (%)</th>
                                `;
                                months.forEach(m => {
                                    theadHtml += `<th class="text-right" style="width: 100px;">${m}-${yrShort}</th>`;
                                });
                                theadHtml += `<th class="text-right" style="width: 120px;">Total ${yrFull}</th></tr>`;
                                $('#budget-monthly-thead').html(theadHtml);
                                
                                let summaryTheadHtml = theadHtml.replace('<th style="width: 120px;">Código</th>', '').replace('<th style="width: 350px;">Descripción</th>', '<th colspan="2">Concepto</th>');
                                $('#budget-summary-thead').html(summaryTheadHtml);
                            };
                            window.renderStep7Headers();"""

content = content.replace(old_headers, new_headers)

# Inject renderStep7Headers into switchYear
old_switch = """                        recalculateStep7();
                    };"""
new_switch = """                        if(window.renderStep7Headers) window.renderStep7Headers();
                        recalculateStep7();
                    };"""

content = content.replace(old_switch, new_switch)

with open('templates/financial_planning/wizard.html', 'w', encoding='utf-8') as f:
    f.write(content)
