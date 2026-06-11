import re
import os

filepath = r"c:\Users\VICTUS\Desktop\A.RISK ERM\templates\financial_planning\wizard.html"

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update Title and remove Tabs
content = re.sub(
    r'<h4 class="font-weight-bold text-primary text-uppercase" style="letter-spacing: 0.5px;">ESTADO DE RESULTADOS PROYECTADO \([^)]+\)</h4>',
    r'<h4 class="font-weight-bold text-primary text-uppercase" style="letter-spacing: 0.5px;">ESTADO DE RESULTADOS PROYECTADO (<span id="active-year-display">{{ plan.start_date.year }}</span> - <span id="end-year-display"></span>)</h4>',
    content
)

content = re.sub(
    r'<ul class="nav nav-tabs mb-3" id="projectionYearsTabs" role="tablist">[\s\S]*?</ul>',
    r'<!-- Tabs removed: showing all years sequentially -->',
    content
)

# 2. Update renderTabs function logic and switchYear
def repl_tabs(m):
    return '''function renderTabs() {
        let displayEl = document.getElementById('active-year-display');
        let endDisplayEl = document.getElementById('end-year-display');
        if (displayEl) displayEl.innerText = projectionStartYear;
        if (endDisplayEl) endDisplayEl.innerText = projectionStartYear + projectionYearsCount - 1;
    }'''
content = re.sub(
    r'function renderTabs\(\) \{[\s\S]*?window\.switchYear = function\(index\) \{[\s\S]*?recalculateStep7\(\);\s*\};',
    repl_tabs,
    content
)

# 3. Update renderStep7Headers
def repl_headers(m):
    return '''window.renderStep7Headers = function() {
                                const pyFull = projectionStartYear - 1;
                                const pyShort = String(pyFull).slice(-2);
                                
                                let theadHtml = `
                                    <tr>
                                        <th style="width: 120px; position: sticky; left: 0; z-index: 3; background-color: #6610f2; color:white;">Código</th>
                                        <th style="width: 350px; position: sticky; left: 120px; z-index: 3; background-color: #6610f2; color:white;">Descripción</th>
                                        <th class="text-right" style="width: 100px;">Dic-${pyShort}</th>
                                `;
                                
                                for(let yr = 0; yr < projectionYearsCount; yr++) {
                                    let yrFull = projectionStartYear + yr;
                                    let yrShort = String(yrFull).slice(-2);
                                    theadHtml += `<th class="text-center" style="width: 100px;">Var (%) ${yrFull}</th>`;
                                    months.forEach(m => {
                                        theadHtml += `<th class="text-right" style="width: 100px;">${m}-${yrShort}</th>`;
                                    });
                                    theadHtml += `<th class="text-right" style="width: 120px;">Total ${yrFull}</th>`;
                                }
                                "</tr>";
                                $('#budget-monthly-thead').html(theadHtml);
                                
                                let summaryTheadHtml = theadHtml.replace('<th style="width: 120px; position: sticky; left: 0; z-index: 3; background-color: #6610f2; color:white;">Código</th>', '').replace('<th style="width: 350px; position: sticky; left: 120px; z-index: 3; background-color: #6610f2; color:white;">Descripción</th>', '<th colspan="2" style="position: sticky; left: 0; z-index: 3; background-color: #6610f2; color: white;">Concepto</th>');
                                $('#budget-summary-thead').html(summaryTheadHtml);
                            };'''
content = re.sub(
    r'window\.renderStep7Headers = function\(\) \{[\s\S]*?\$\(\'#budget-summary-thead\'\)\.html\(summaryTheadHtml\);\s*\};',
    repl_headers,
    content
)

# 4. Update data.income_statement.forEach(item => { ... }) generating table rows
html_gen_regex = r"let html = '';\s*data\.income_statement\.forEach\(item => \{[\s\S]*?\$\('#budget-monthly-tbody'\)\.html\(html\);"
def repl_html_gen(m):
    return '''let html = '';
                            data.income_statement.forEach(item => {
                                let node = accMap[item.code];
                                node.uiChildren = node.children_codes.filter(c => accMap[c]);
                                const hasChildren = node.uiChildren.length > 0;
                                
                                const trClass = hasChildren ? 'font-weight-bold bg-light border-bottom' : '';
                                const iconHtml = hasChildren ? `<i class="fas fa-chevron-down mr-2 expand-toggle text-primary" style="cursor:pointer; width: 12px;" onclick="toggleRow('${node.code}', this)"></i>` : `<span style="display:inline-block; width:20px;"></span>`;
                                
                                html += `<tr class="budget-row ${trClass}" data-code="${node.code}" data-parent="${node.parent_code || ''}" id="row-${node.code}">
                                    <td style="padding-left:${(node.depth || 0) * 14}px; position: sticky; left: 0; z-index: 1; background-color: ${hasChildren ? '#f8f9fa' : '#fff'};">
                                        ${iconHtml}
                                        <span class="badge badge-light border text-monospace text-dark">${node.code || ''}</span>
                                    </td>
                                    <td style="position: sticky; left: 120px; z-index: 1; background-color: ${hasChildren ? '#f8f9fa' : '#fff'};">${node.name || ''}</td>
                                    <td class="text-right text-monospace text-secondary" id="cell-baseBal-${node.code}">${fmt(node.baseBal)}</td>
                                `;

                                for(let yr = 0; yr < projectionYearsCount; yr++) {
                                    let varHtml = '';
                                    if (hasChildren && node.years[yr] && Math.abs(node.years[yr].unassignedBase || 0) < 0.01) {
                                        varHtml = `<td class="text-center text-monospace font-weight-bold cell-var-${yr}" id="cell-var-${yr}-${node.code}">-</td>`;
                                    } else {
                                        varHtml = `<td><input type="number" class="form-control form-control-sm text-center step7-input" data-code="${node.code}" data-year="${yr}" value="${parseFloat(node.years[yr].val || 0).toFixed(2)}" step="0.01" style="width: 70px;"></td>`;
                                    }
                                    html += varHtml;
                                    
                                    for(let i=0; i<12; i++) {
                                        html += `<td class="text-right text-monospace cell-m${i}-${yr}" id="cell-m${i}-${yr}-${node.code}">-</td>`;
                                    }
                                    html += `<td class="text-right text-monospace font-weight-bold bg-light cell-total-${yr}" id="cell-total-${yr}-${node.code}">-</td>`;
                                }
                                html += `</tr>`;
                            });
                            $('#budget-monthly-tbody').html(html);'''
content = re.sub(html_gen_regex, repl_html_gen, content)

# 5. Update cell references
cell_ref_regex = r"let sortedCodes = Object\.keys\(accMap\)\.sort\(\(a, b\) => b\.length - a\.length\);\s*sortedCodes\.forEach\(code => \{[\s\S]*?node\.rowEl = \$\(`#row-\$\{code\}`\);\s*\}\);"
def repl_cell_ref(m):
    return '''let sortedCodes = Object.keys(accMap).sort((a, b) => b.length - a.length);
                            sortedCodes.forEach(code => {
                                let node = accMap[code];
                                if (node.uiChildren.length === 0 || Math.abs(node.years[0].unassignedBase) >= 0.01) {
                                    node.inputEls = [];
                                    for(let yr=0; yr<projectionYearsCount; yr++) {
                                        node.inputEls.push($(`.step7-input[data-code="${code}"][data-year="${yr}"]`));
                                    }
                                }
                                node.varCells = [];
                                node.totalCells = [];
                                node.mCellsYr = [];
                                for(let yr=0; yr<projectionYearsCount; yr++) {
                                    if (node.uiChildren.length > 0) {
                                        node.varCells.push($(`#cell-var-${yr}-${code}`));
                                    } else {
                                        node.varCells.push(null);
                                    }
                                    node.totalCells.push($(`#cell-total-${yr}-${code}`));
                                    let mArr = [];
                                    for(let i=0; i<12; i++) {
                                        mArr.push($(`#cell-m${i}-${yr}-${code}`));
                                    }
                                    node.mCellsYr.push(mArr);
                                }
                                node.rowEl = $(`#row-${code}`);
                            });'''
content = re.sub(cell_ref_regex, repl_cell_ref, content)

# 6. Update recalculateStep7 section for DOM updates
dom_update_regex = r"// Restore active year to update the UI correctly[\s\S]*?node\.rowEl\.attr\('data-has-budget', hasBudget \? 'true' : 'false'\);\s*}\);"
def repl_dom_update(m):
    return '''// Restore active year
                                activeYearIndex = savedActive;
                                
                                // 3. Update DOM Cells
                                sortedCodes.forEach(code => {
                                    let node = accMap[code];
                                    
                                    if (node.rowEl && node.rowEl.length) {
                                        $(`#cell-baseBal-${code}`).html(fmt(node.years[0].baseBal));
                                    }
                                    
                                    let hasBudget = false;
                                    for(let yr = 0; yr < projectionYearsCount; yr++) {
                                        let actYr = node.years[yr];
                                        if (Math.abs(actYr.totalProjected) > 0.001) hasBudget = true;
                                        
                                        if (node.uiChildren.length > 0) {
                                            let newVar = 0;
                                            if (actYr.baseBal !== 0) {
                                                newVar = ((actYr.totalProjected / actYr.baseBal) - 1) * 100;
                                            }
                                            if (node.varCells && node.varCells[yr] && node.varCells[yr].length) {
                                                node.varCells[yr].html(newVar.toFixed(2) + '%');
                                            }
                                        }
                                        
                                        node.totalCells[yr].html(fmt(actYr.totalProjected));
                                        for(let i=0; i<12; i++) {
                                            let cell = node.mCellsYr[yr][i];
                                            cell.html(fmt(actYr.monthlyProjected[i]));
                                            
                                            if (actYr.monthlyOverrides && actYr.monthlyOverrides[i] !== undefined) {
                                                cell.addClass('bg-warning-light text-dark font-weight-bold').css('background-color', '#fff3cd');
                                            } else {
                                                cell.removeClass('bg-warning-light text-dark font-weight-bold').css('background-color', '');
                                            }
                                        }
                                    }
                                    
                                    node.rowEl.attr('data-has-budget', hasBudget ? 'true' : 'false');
                                });'''
content = re.sub(dom_update_regex, repl_dom_update, content)

# 7. Update Summary HTML
summary_regex = r"// Update Summary[\s\S]*?\$\('#budget-summary-tbody'\)\.html\(sumHtml\);\s*\}"
def repl_summary(m):
    return '''// Update Summary
                                let incNode = accMap['5'];
                                let expNode = accMap['4'];
                                if (incNode && expNode) {
                                    let sumHtml = '';
                                    let incHtml = `<td class="text-right text-monospace text-success">${fmt(incNode.years[0].baseBal)}</td>`;
                                    let expHtml = `<td class="text-right text-monospace text-danger">${fmt(expNode.years[0].baseBal)}</td>`;
                                    
                                    let utilBaseFirst = incNode.years[0].baseBal - expNode.years[0].baseBal;
                                    let utilHtml = `<td class="text-right text-monospace font-weight-bold ${utilBaseFirst < 0 ? 'text-danger' : ''}">${fmt(utilBaseFirst)}</td>`;
                                    
                                    for(let yr = 0; yr < projectionYearsCount; yr++) {
                                        let actInc = incNode.years[yr];
                                        let actExp = expNode.years[yr];
                                        
                                        incHtml += `<td class="text-center font-weight-bold text-success">${actInc.baseBal !== 0 ? ((actInc.totalProjected/actInc.baseBal - 1)*100).toFixed(2) : '0.00'}%</td>`;
                                        for(let i=0; i<12; i++) incHtml += `<td class="text-right text-monospace text-success">${fmt(actInc.monthlyProjected[i])}</td>`;
                                        incHtml += `<td class="text-right text-monospace font-weight-bold text-success">${fmt(actInc.totalProjected)}</td>`;
                                        
                                        expHtml += `<td class="text-center font-weight-bold text-danger">${actExp.baseBal !== 0 ? ((actExp.totalProjected/actExp.baseBal - 1)*100).toFixed(2) : '0.00'}%</td>`;
                                        for(let i=0; i<12; i++) expHtml += `<td class="text-right text-monospace text-danger">${fmt(actExp.monthlyProjected[i])}</td>`;
                                        expHtml += `<td class="text-right text-monospace font-weight-bold text-danger">${fmt(actExp.totalProjected)}</td>`;
                                        
                                        let utilBase = actInc.baseBal - actExp.baseBal;
                                        let utilTotal = actInc.totalProjected - actExp.totalProjected;
                                        let utilVar = utilBase !== 0 ? ((utilTotal / utilBase) - 1) * 100 : 0;
                                        
                                        utilHtml += `<td class="text-center font-weight-bold ${utilVar < 0 ? 'text-danger' : ''}">${utilVar.toFixed(2)}%</td>`;
                                        for(let i=0; i<12; i++) {
                                            let mUtil = (actInc.monthlyProjected[i] || 0) - (actExp.monthlyProjected[i] || 0);
                                            utilHtml += `<td class="text-right text-monospace font-weight-bold ${mUtil < 0 ? 'text-danger' : ''}">${fmt(mUtil)}</td>`;
                                        }
                                        utilHtml += `<td class="text-right text-monospace font-weight-bold ${utilTotal < 0 ? 'text-danger' : ''}">${fmt(utilTotal)}</td>`;
                                    }
                                    
                                    sumHtml = `
                                        <tr><td colspan="2" class="font-weight-bold" style="position: sticky; left: 0; z-index: 1; background-color: #fff;">Total Ingresos (5)</td>${incHtml}</tr>
                                        <tr><td colspan="2" class="font-weight-bold" style="position: sticky; left: 0; z-index: 1; background-color: #fff;">Total Gastos (4)</td>${expHtml}</tr>
                                        <tr style="background-color: #fff3cd;"><td colspan="2" class="font-weight-bold" style="position: sticky; left: 0; z-index: 1; background-color: #fff3cd;">Utilidad / Pérdida Neta</td>${utilHtml}</tr>
                                    `;
                                    $('#budget-summary-tbody').html(sumHtml);
                                }'''
content = re.sub(summary_regex, repl_summary, content)

# 8. Dbl click manual override
dblclick_regex = r"\$\('#budget-monthly-tbody'\)\.on\('dblclick', 'td\[id\^=\"cell-m\"\]', function\(\) \{[\s\S]*?\}\);"
def repl_dblclick(m):
    return '''$('#budget-monthly-tbody').on('dblclick', 'td[id^="cell-m"]', function() {
                                let cellId = $(this).attr('id');
                                let match = cellId.match(/^cell-m(\d+)-(\d+)-(.+)$/);
                                if (!match) return;
                                
                                let monthIdx = parseInt(match[1]);
                                let yrIdx = parseInt(match[2]);
                                let code = match[3];
                                
                                let node = accMap[code];
                                if (!node || node.uiChildren.length > 0) return; 
                                
                                if ($(this).find('input').length > 0) return; 
                                
                                let currentVal = node.years[yrIdx].monthlyProjected[monthIdx] || 0;
                                let inputHtml = `<input type="number" class="form-control form-control-sm text-right manual-month-override" value="${Math.round(currentVal)}" style="width:100%; min-width:60px; font-size:0.8rem; padding:2px;">`;
                                $(this).html(inputHtml);
                                
                                let inputEl = $(this).find('input');
                                inputEl.focus().select();
                                
                                inputEl.on('blur keypress', function(e) {
                                    if (e.type === 'keypress' && e.which !== 13) return;
                                    let newValStr = $(this).val();
                                    if (newValStr === "") {
                                        if (node.years[yrIdx].monthlyOverrides) delete node.years[yrIdx].monthlyOverrides[monthIdx];
                                    } else {
                                        let newVal = parseFloat(newValStr) || 0;
                                        if (!node.years[yrIdx].monthlyOverrides) node.years[yrIdx].monthlyOverrides = {};
                                        node.years[yrIdx].monthlyOverrides[monthIdx] = newVal;
                                    }
                                    recalculateStep7();
                                });
                            });'''
content = re.sub(dblclick_regex, repl_dblclick, content)

# 9. copyPreviousYearData
cpy_regex = r"window\.copyPreviousYearData = function\(\) \{[\s\S]*?recalculateStep7\(\);\s*\};"
def repl_cpy(m):
    return '''window.copyPreviousYearData = function() {
                                data.income_statement.forEach(item => {
                                    let node = accMap[item.code];
                                    if (node && node.inputEls) {
                                        node.inputEls.forEach(el => {
                                            if (el && el.length) el.val(0);
                                        });
                                        for(let yr=0; yr<projectionYearsCount; yr++){
                                            node.years[yr].baseTrend = 0;
                                            node.years[yr].val = 0;
                                            node.years[yr].monthlyOverrides = {};
                                        }
                                    }
                                });
                                $('#apply-var-month').val(0);
                                recalculateStep7();
                            };'''
content = re.sub(cpy_regex, repl_cpy, content)

# 10. applyHistoricalTrend
apply_regex = r"if \(node && node\.inputEl\) \{[\s\S]*?node\.inputEl\.val\(t\.toFixed\(2\)\);\s*\}\s*\}"
def repl_apply(m):
    return '''if (node && node.inputEls) {
                                                if (result.trends[item.code] !== undefined) {
                                                    let t = parseFloat(result.trends[item.code]);
                                                    for(let yr=0; yr<projectionYearsCount; yr++) {
                                                        node.years[yr].baseTrend = t;
                                                        node.years[yr].val = t;
                                                        if (node.inputEls[yr]) node.inputEls[yr].val(t.toFixed(2));
                                                    }
                                                }
                                            }'''
content = re.sub(apply_regex, repl_apply, content)

# 11. input change event
input_regex = r"\$\('\.step7-input'\)\.on\('input', function\(\) \{[\s\S]*?recalculateStep7\(\);\s*\}\);"
def repl_input(m):
    return '''$('.step7-input').on('input', function() {
                                let code = String($(this).data('code'));
                                let yr = parseInt($(this).data('year'));
                                let node = accMap[code];
                                if (node && !isNaN(yr)) {
                                    node.years[yr].val = parseFloat($(this).val()) || 0;
                                }
                                clearTimeout(step4Timeout);
                                step4Timeout = setTimeout(recalculateStep7, 150);
                            }).on('blur', function() {
                                let v = parseFloat($(this).val()) || 0;
                                $(this).val(v.toFixed(2));
                                
                                let code = String($(this).data('code'));
                                let yr = parseInt($(this).data('year'));
                                let node = accMap[code];
                                if (node && !isNaN(yr)) {
                                    node.years[yr].val = v;
                                }
                                recalculateStep7();
                            });'''
content = re.sub(input_regex, repl_input, content)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Done")
