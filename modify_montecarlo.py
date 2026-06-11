import re

with open(r'c:\Users\VICTUS\Desktop\A.RISK ERM\templates\financial_planning\wizard.html', 'r', encoding='utf-8') as f:
    text = f.read()

js_block = """
                    window.montecarloData = null;
                    window.currentMcScenario = 'base';
                    
                    window.runMontecarloSimulation = function() {
                        let btn = $('#montecarlo-body-container .btn-primary');
                        let status = $('#montecarlo-status');
                        btn.prop('disabled', true);
                        status.html('<i class="fas fa-spinner fa-spin text-primary"></i> Calculando 1000 iteraciones...');
                        
                        fetch("{% url 'financial_planning:ml_montecarlo_projection' plan.id %}", {
                            method: 'POST',
                            headers: {
                                'X-CSRFToken': '{{ csrf_token }}',
                                'Content-Type': 'application/json'
                            }
                        })
                        .then(response => {
                            if (!response.ok) throw new Error('Error en el servidor');
                            return response.json();
                        })
                        .then(result => {
                            if(result.status === 'success' && result.data) {
                                window.montecarloData = result.data;
                                status.html('<i class="fas fa-check-circle text-success"></i> Simulaci&oacute;n completada');
                                buildMontecarloTable();
                            } else {
                                status.html('<i class="fas fa-exclamation-triangle text-danger"></i> Error: ' + result.msg);
                            }
                        })
                        .catch(err => {
                            status.html('<i class="fas fa-exclamation-triangle text-danger"></i> Error de conexi&oacute;n');
                        })
                        .finally(() => {
                            btn.prop('disabled', false);
                        });
                    };

                    window.switchMontecarloScenario = function(scenario, btnEl) {
                        window.currentMcScenario = scenario;
                        $(btnEl).siblings().removeClass('active');
                        $(btnEl).addClass('active');
                        if (window.montecarloData) {
                            buildMontecarloTable();
                        }
                    };

                    function buildMontecarloTable() {
                        if (!window.montecarloData || !window.accMap7) return;
                        
                        // Deep clone accMap7 to avoid mutating main table
                        let mcMap = JSON.parse(JSON.stringify(window.accMap7));
                        let flatTree = [];
                        $('#budget-monthly-tbody tr.budget-row').each(function() {
                            let code = $(this).data('code');
                            if(mcMap[code]) flatTree.push(mcMap[code]);
                        });
                        
                        // Apply Montecarlo trends to mcMap
                        Object.keys(window.montecarloData).forEach(code => {
                            if (mcMap[code]) {
                                let mcValues = window.montecarloData[code]; // { pesimista, base, optimista }
                                let t = mcValues[window.currentMcScenario];
                                for(let yr=0; yr<projectionYearsCount; yr++) {
                                    mcMap[code].years[yr].val = t;
                                }
                            }
                        });
                        
                        // Recalculate bottom-up
                        for(let i = flatTree.length - 1; i >= 0; i--) {
                            let node = flatTree[i];
                            let isIncome = node.code.startsWith('4');
                            let isExpense = node.code.startsWith('5');
                            
                            if (!node.children_codes || node.children_codes.length === 0) {
                                // Leaf node: Calculate months
                                for(let yr=0; yr<projectionYearsCount; yr++) {
                                    let annualTotal = 0;
                                    let rate = parseFloat(node.years[yr].val || 0) / 100.0;
                                    let factor = 1.0 + rate;
                                    
                                    for(let m=0; m<12; m++) {
                                        let histVal = node.history && node.history[m] ? parseFloat(node.history[m]) : 0;
                                        
                                        let proj = 0;
                                        if (isIncome) proj = histVal * factor;
                                        else if (isExpense) proj = histVal * factor;
                                        
                                        node.years[yr].months[m] = proj;
                                        annualTotal += proj;
                                    }
                                    node.years[yr].total = annualTotal;
                                }
                            } else {
                                // Parent node: sum children
                                for(let yr=0; yr<projectionYearsCount; yr++) {
                                    let annualTotal = 0;
                                    for(let m=0; m<12; m++) {
                                        let mSum = 0;
                                        node.children_codes.forEach(ccode => {
                                            if (mcMap[ccode]) mSum += (mcMap[ccode].years[yr].months[m] || 0);
                                        });
                                        node.years[yr].months[m] = mSum;
                                        annualTotal += mSum;
                                    }
                                    node.years[yr].total = annualTotal;
                                }
                            }
                        }
                        
                        ['3', '3.1', '3.1.1'].forEach(utilCode => {
                            if (mcMap[utilCode]) {
                                for(let yr=0; yr<projectionYearsCount; yr++) {
                                    let annualTotal = 0;
                                    for(let m=0; m<12; m++) {
                                        let inc = mcMap['4'] ? mcMap['4'].years[yr].months[m] : 0;
                                        let exp = mcMap['5'] ? mcMap['5'].years[yr].months[m] : 0;
                                        let val = inc - exp;
                                        mcMap[utilCode].years[yr].months[m] = val;
                                        annualTotal += val;
                                    }
                                    mcMap[utilCode].years[yr].total = annualTotal;
                                }
                            }
                        });

                        // Render table
                        let html = '';
                        flatTree.forEach(node => {
                            let hasChildren = node.children_codes && node.children_codes.length > 0;
                            const trClass = hasChildren ? 'font-weight-bold bg-light border-bottom' : '';
                            const iconHtml = hasChildren ? `<i class="fas fa-chevron-down mr-2 text-warning" style="width: 12px;"></i>` : `<span style="display:inline-block; width:20px;"></span>`;
                            
                            html += `<tr class="budget-row ${trClass}">
                                <td style="padding-left:${(node.depth || 0) * 14}px; position: sticky; left: 0; z-index: 1; background-color: ${hasChildren ? '#f8f9fa' : '#fff'};">
                                    <div class="d-flex align-items-center text-truncate">
                                        ${iconHtml}
                                        <span class="text-monospace">${node.code}</span>
                                    </div>
                                </td>
                                <td style="position: sticky; left: 120px; z-index: 1; background-color: ${hasChildren ? '#f8f9fa' : '#fff'};">
                                    <div class="text-truncate" title="${node.name}">${node.name}</div>
                                </td>
                                <td class="text-right text-monospace text-secondary">${fmt(node.baseBal)}</td>
                            `;
                            
                            for(let yr = 0; yr < projectionYearsCount; yr++) {
                                let varHtml = '';
                                if (hasChildren) {
                                    varHtml = `<td class="text-center text-monospace font-weight-bold text-muted">-</td>`;
                                } else {
                                    varHtml = `<td class="text-center text-monospace"><span class="badge badge-warning">${parseFloat(node.years[yr].val || 0).toFixed(2)}%</span></td>`;
                                }
                                html += varHtml;
                                
                                for(let i=0; i<12; i++) {
                                    html += `<td class="text-right text-monospace">${fmt(node.years[yr].months[i])}</td>`;
                                }
                                html += `<td class="text-right text-monospace font-weight-bold bg-light" style="border-left: 2px solid #e9ecef;">${fmt(node.years[yr].total)}</td>`;
                            }
                            html += `</tr>`;
                        });
                        
                        $('#montecarlo-monthly-tbody').html(html);
                        
                        // Sync headers
                        let theadHtml = `<tr>
                            <th style="width: 120px; position: sticky; left: 0; z-index: 2;" class="bg-dark text-white">C&oacute;digo</th>
                            <th style="width: 350px; position: sticky; left: 120px; z-index: 2;" class="bg-dark text-white">Descripci&oacute;n</th>
                            <th style="width: 120px;" class="text-right bg-dark text-white">Base</th>`;
                            
                        let startYear = parseInt("{{ plan.year|default:2026 }}");
                        for(let yr = 0; yr < projectionYearsCount; yr++) {
                            let currYear = startYear + yr;
                            theadHtml += `<th style="width: 80px;" class="text-center bg-secondary text-white">Var %</th>`;
                            const months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];
                            for(let i=0; i<12; i++) {
                                theadHtml += `<th style="width: 100px;" class="text-right bg-secondary text-white">${months[i]} ${currYear}</th>`;
                            }
                            theadHtml += `<th style="width: 120px; border-left: 2px solid #e9ecef;" class="text-right bg-warning text-dark">TOTAL ${currYear}</th>`;
                        }
                        theadHtml += `</tr>`;
                        $('#montecarlo-monthly-thead').html(theadHtml);
                    }
"""

if 'window.montecarloData' not in text:
    text = text.replace('function recalculateStep7', js_block + '\nfunction recalculateStep7')

with open(r'c:\Users\VICTUS\Desktop\A.RISK ERM\templates\financial_planning\wizard.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("Modification complete.")
