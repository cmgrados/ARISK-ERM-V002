with open('templates/financial_planning/wizard.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re

# 1. Add state variables before renderMonthlyTable
state_vars = '''
                        let showTrendCols = false;
                        let showMCCols = false;
                        let mcDataObj = null;

                        function renderMonthlyTable(agencyId, variableId, period) {
'''
text = re.sub(r'function renderMonthlyTable\(agencyId, variableId, period\) \{', state_vars, text, count=1)

# 2. Rewrite renderMonthlyTable
new_table = '''
                            const container = $('#proj-table-container');
                            if (!trendDatasetsByAgency[agencyId]) return;
                            const vars = trendDatasetsByAgency[agencyId].variables;
                            const v = vars.find(d => d.id === variableId);
                            if (!v) return;

                            const isSocio = variableId === 'socios';
                            $('#proj-variable-label').text(v.name);
                            $('#proj-months-label').text(period);

                            let theadHtml = `
                                <tr>
                                    <th class="font-weight-bold align-middle" style="min-width: 120px;">Mes</th>
                                    <th class="text-left font-weight-bold text-danger" style="min-width: 140px;">Pesimista</th>
                                    <th class="text-left font-weight-bold text-primary" style="min-width: 140px;">Base</th>
                                    <th class="text-left font-weight-bold text-success" style="min-width: 140px;">Optimista</th>`;
                            
                            if (showTrendCols) {
                                theadHtml += `
                                    <th class="text-left font-weight-bold text-secondary" style="min-width: 140px;">Tend. Año Ant.</th>`;
                            }
                            
                            if (showMCCols && mcDataObj) {
                                theadHtml += `
                                    <th class="text-left font-weight-bold text-danger" style="min-width: 140px; border-left: 2px solid #dee2e6;">MC Pesimista</th>
                                    <th class="text-left font-weight-bold text-primary" style="min-width: 140px;">MC Base</th>
                                    <th class="text-left font-weight-bold text-success" style="min-width: 140px;">MC Optimista</th>`;
                            }
                            
                            theadHtml += `</tr>`;

                            let html = `<table class="table table-bordered table-sm m-0 w-auto" style="font-size: 0.8rem; min-width: 60%;">
                                <thead class="bg-light text-muted">
                                    ${theadHtml}
                                </thead>
                                <tbody>`;

                            const startIdx = 1;
                            const numRows = Math.min(period, v.base.length - 1);

                            for (let i = 0; i < numRows; i++) {
                                const idx = startIdx + i;
                                const lbl = trendLabels[histMonthsCount + i] || `Mes ${i+1}`;

                                const formatVal = (val) => {
                                    if (val === null || val === undefined) return '-';
                                    if (isSocio) return Math.round(val).toLocaleString('en-US');
                                    return 'S/ ' + val.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
                                };

                                html += `<tr>
                                    <td class="font-weight-bold text-dark bg-light">${lbl}</td>
                                    <td class="text-left text-danger">${formatVal(v.pesimista[idx])}</td>
                                    <td class="text-left font-weight-bold text-primary">${formatVal(v.base[idx])}</td>
                                    <td class="text-left text-success">${formatVal(v.optimista[idx])}</td>`;
                                
                                if (showTrendCols) {
                                    html += `<td class="text-left text-secondary font-weight-bold">${formatVal(v.trend[idx])}</td>`;
                                }
                                
                                if (showMCCols && mcDataObj) {
                                    html += `
                                        <td class="text-left text-danger" style="border-left: 2px solid #dee2e6;">${formatVal(mcDataObj.pesimista[i])}</td>
                                        <td class="text-left font-weight-bold text-primary">${formatVal(mcDataObj.base[i])}</td>
                                        <td class="text-left text-success">${formatVal(mcDataObj.optimista[i])}</td>`;
                                }
                                
                                html += `</tr>`;
                            }
                            html += `</tbody></table>`;
                            container.html(html);
                        }
'''

# Replace the body of renderMonthlyTable
text = re.sub(
    r'const container = \$\(\'#proj-table-container\'\);.*?container\.html\(html\);\s*\}', 
    new_table.strip(), 
    text, 
    flags=re.DOTALL
)


# 3. Add event handlers for buttons at the end of loadTrendData success handler
events_html = '''
                        $('#btn-apply-trend').off('click').on('click', function() {
                            showTrendCols = !showTrendCols;
                            renderMonthlyTable(currentAgency, currentVariable, currentPeriod);
                        });

                        $('#btn-run-mc').off('click').on('click', function() {
                            const btn = $(this);
                            const originalHtml = btn.html();
                            btn.html('<i class="fas fa-spinner fa-spin mr-1"></i> Calculando...');
                            btn.prop('disabled', true);
                            
                            const agencyId = currentAgency;
                            const variableId = currentVariable;
                            const period = currentPeriod;
                            const iterations = $('#mc-iterations').val() || 1000;
                            
                            const vars = trendDatasetsByAgency[agencyId].variables;
                            const v = vars.find(d => d.id === variableId);
                            
                            $.ajax({
                                url: "{% url 'financial_planning:api_run_montecarlo' plan.id %}",
                                type: 'POST',
                                contentType: 'application/json',
                                data: JSON.stringify({
                                    history: v.hist,
                                    proj_months: period,
                                    iterations: parseInt(iterations)
                                }),
                                headers: {
                                    'X-CSRFToken': '{{ csrf_token }}'
                                },
                                success: function(res) {
                                    if(res.status === 'success') {
                                        mcDataObj = res.data;
                                        showMCCols = true;
                                        renderMonthlyTable(agencyId, variableId, period);
                                    } else {
                                        alert("Error en Montecarlo: " + res.msg);
                                    }
                                },
                                error: function() {
                                    alert("Error de conexión al generar Montecarlo");
                                },
                                complete: function() {
                                    btn.html(originalHtml);
                                    btn.prop('disabled', false);
                                }
                            });
                        });
                        
                        updateDashboard();
'''

text = text.replace('updateDashboard();', events_html, 1)

with open('templates/financial_planning/wizard.html', 'w', encoding='utf-8') as f:
    f.write(text)
print("Patch applied")
