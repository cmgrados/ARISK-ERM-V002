
                    const budgetDataJson7 = '{{ budget_data_json|escapejs }}';
                    const histDataJson7 = '{{ historical_data_json|escapejs }}';
                    const projectionYearsCount = parseInt('{{ plan.projection_years|default:"3" }}');
                    const projectionStartYear = parseInt('{{ plan.start_date.year|default:"2026" }}'.replace(/,/g, ''));
                    let activeYearIndex = 0;
                    
                    function renderTabs() {
        let displayEl = document.getElementById('active-year-display');
        let endDisplayEl = document.getElementById('end-year-display');
        if (displayEl) displayEl.innerText = projectionStartYear;
        if (endDisplayEl) endDisplayEl.innerText = projectionStartYear + projectionYearsCount - 1;
    }

                    document.addEventListener('DOMContentLoaded', function() {
                        renderTabs();
                        let data = null;
                        let bData = {};
                        let hData = {};
                        try { bData = JSON.parse(budgetDataJson7); } catch(e) {}
                        try { hData = JSON.parse(histDataJson7); } catch(e) {}
                        
                        if (bData && bData.income_statement && bData.income_statement.length > 0) {
                            data = bData;
                        } else if (hData && hData.income_statement && hData.income_statement.length > 0) {
                            // Convert hData (list of lists) to structured data
                            let parsedIncomeStatement = [];
                            let periods = hData.selected_periods || [];
                            
                            // First pass: create node objects
                            hData.income_statement.forEach(row => {
                                let label = row[0];
                                let parts = label.split(' - ');
                                let code = parts[0].trim();
                                let name = parts.slice(1).join(' - ').trim();
                                
                                let parent_code = null;
                                let depth = 1;
                                if (code.length === 2) {
                                    parent_code = code.substring(0, 1);
                                    depth = 2;
                                } else if (code.length > 2) {
                                    parent_code = code.substring(0, code.length - 2);
                                    depth = (code.length - 2) / 2 + 2;
                                }
                                
                                let balances = {};
                                for (let i = 0; i < periods.length; i++) {
                                    balances[periods[i]] = row[i + 1] || 0;
                                }
                                
                                parsedIncomeStatement.push({
                                    code: code,
                                    name: name,
                                    parent_code: parent_code,
                                    children_codes: [],
                                    depth: depth,
                                    balances: balances
                                });
                            });
                            
                            // Second pass: link children
                            let nodeMap = {};
                            parsedIncomeStatement.forEach(node => {
                                nodeMap[node.code] = node;
                            });
                            
                            parsedIncomeStatement.forEach(node => {
                                if (node.parent_code && nodeMap[node.parent_code]) {
                                    nodeMap[node.parent_code].children_codes.push(node.code);
                                }
                            });
                            
                            // Filter out accounts with zero movement
                            let hasMovement = function(node) {
                                let hasBal = Object.values(node.balances).some(v => Math.abs(v) > 0.005);
                                if (hasBal) return true;
                                return node.children_codes.some(c => nodeMap[c] && hasMovement(nodeMap[c]));
                            };
                            parsedIncomeStatement = parsedIncomeStatement.filter(node => hasMovement(node));
                            
                            data = {
                                selected_periods: periods,
                                income_statement: parsedIncomeStatement,
                                account_assumptions: hData.account_assumptions || {}
                            };
                            
                            if (bData && bData.account_assumptions) {
                                data.account_assumptions = bData.account_assumptions;
                            }
                        }
                        
                        if (data && data.income_statement) {
                            // Filter out accounts other than 4 and 5 (like 'cuenta de orden')
                            data.income_statement = data.income_statement.filter(item => item.code.startsWith('4') || item.code.startsWith('5'));
                            
                            let decPeriods = (data.selected_periods || []).filter(p => p.endsWith('-12')).sort();
                            
                            const urlParams = new URLSearchParams(window.location.search);
                            const applyAssumptions = urlParams.get('apply') !== 'false';
                            
                            // Remove apply=false from URL so it doesn't persist on refresh
                            if (urlParams.has('apply')) {
                                urlParams.delete('apply');
                                const newUrl = window.location.pathname + (urlParams.toString() ? '?' + urlParams.toString() : '');
                                window.history.replaceState({}, '', newUrl);
                            }
                            
                            let assumptions = data.account_assumptions || {};
                            
                            let accMap = {};
                            
                            window.accMap7 = accMap; // Expose globally for switchYear
                            // Step 1: Initialize map and calculate leaf projections
                            data.income_statement.forEach(item => {
                                let baseBal = 0;
                                if (decPeriods.length > 0) {
                                    let lastP = decPeriods[decPeriods.length - 1];
                                    baseBal = (item.balances && item.balances[lastP]) ? item.balances[lastP] : 0;
                                }
                                
                                let savedAssump = assumptions[item.code];
                                
                                // Upgrade legacy format
                                if (savedAssump !== undefined && !savedAssump.years) {
                                    let oldVal = 0, oldBase = 0, oldOverrides = {};
                                    if (typeof savedAssump === 'object' && savedAssump !== null) {
                                        oldVal = savedAssump.val || 0;
                                        oldBase = savedAssump.baseTrend || 0;
                                        oldOverrides = savedAssump.monthlyOverrides || {};
                                    } else {
                                        oldVal = savedAssump; oldBase = savedAssump;
                                    }
                                    savedAssump = {
                                        years: Array(projectionYearsCount).fill(null).map((_, idx) => {
                                            if (idx === 0) return { val: oldVal, baseTrend: oldBase, monthlyOverrides: {...oldOverrides} };
                                            return { val: 0, baseTrend: 0, monthlyOverrides: {} };
                                        })
                                    };
                                    assumptions[item.code] = savedAssump;
                                }
                                
                                let calculatedTrend = 0;
                                if (decPeriods.length >= 2) {
                                    let lastP = decPeriods[decPeriods.length - 1];
                                    let prevP = decPeriods[decPeriods.length - 2];
                                    let lastBal = (item.balances && item.balances[lastP]) ? item.balances[lastP] : 0;
                                    let prevBal = (item.balances && item.balances[prevP]) ? item.balances[prevP] : 0;
                                    if (prevBal !== 0) {
                                        calculatedTrend = ((lastBal - prevBal) / Math.abs(prevBal)) * 100;
                                        if (calculatedTrend > 999) calculatedTrend = 999;
                                        if (calculatedTrend < -100) calculatedTrend = -100;
                                    }
                                }

                                let nodeYears = [];
                                let currentBaseBal = baseBal;
                                
                                for (let yr = 0; yr < projectionYearsCount; yr++) {
                                    let val = 0, baseTrend = 0, monthlyOverrides = {};
                                    let hasSaved = false;
                                    
                                    if (savedAssump && savedAssump.years && savedAssump.years[yr]) {
                                        val = savedAssump.years[yr].val !== undefined ? savedAssump.years[yr].val : 0;
                                        baseTrend = savedAssump.years[yr].baseTrend !== undefined ? savedAssump.years[yr].baseTrend : 0;
                                        monthlyOverrides = savedAssump.years[yr].monthlyOverrides || {};
                                        hasSaved = true;
                                    } else {
                                        val = calculatedTrend;
                                        baseTrend = calculatedTrend;
                                    }
                                    
                                    if (!applyAssumptions && !hasSaved) { val = 0; }
                                    
                                    let totalProjected = currentBaseBal * (1 + (val / 100));
                                    nodeYears.push({
                                        baseBal: currentBaseBal,
                                        val: val,
                                        baseTrend: baseTrend,
                                        monthlyOverrides: monthlyOverrides,
                                        totalProjected: totalProjected,
                                        monthlyProjected: new Array(12).fill(0)
                                    });
                                    currentBaseBal = totalProjected; // Cascade
                                }

                                accMap[item.code] = {
                                    code: item.code,
                                    name: item.name,
                                    depth: item.depth || 0,
                                    parent_code: item.parent_code,
                                    children_codes: item.children_codes || [],
                                    years: nodeYears,
                                    get val() { return this.years[activeYearIndex].val; },
                                    get baseBal() { return this.years[activeYearIndex].baseBal; },
                                    get baseTrend() { return this.years[activeYearIndex].baseTrend; },
                                    get totalProjected() { return this.years[activeYearIndex].totalProjected; },
                                    set totalProjected(v) { this.years[activeYearIndex].totalProjected = v; }
                                };
                            });
                            
                            // Restaurar el mes global de inicio de variación si se guardó
                            if (assumptions._meta && assumptions._meta.startMonth !== undefined) {
                                $('#apply-var-month').val(assumptions._meta.startMonth);
                            }
                            
                            // Step 1.5: Identify the latest historical year for distribution
                            let allPeriods = data.selected_periods || [];
                            let latestYear = 0;
                            allPeriods.forEach(p => {
                                let parts = p.split('-');
                                if(parts.length === 2) {
                                    let y = parseInt(parts[0]);
                                    if(y > latestYear) latestYear = y;
                                }
                            });
                            
                            data.income_statement.forEach(item => {
                                let node = accMap[item.code];
                                node.monthlyHistory = [];
                                let totalHistYear = 0;
                                
                                for (let i=1; i<=12; i++) {
                                    let mStr = i < 10 ? '0'+i : ''+i;
                                    let currentYTD = (item.balances && item.balances[`${latestYear}-${mStr}`]) ? item.balances[`${latestYear}-${mStr}`] : 0;
                                    let prevYTD = 0;
                                    if (i > 1) {
                                        let prevMStr = (i-1) < 10 ? '0'+(i-1) : ''+(i-1);
                                        prevYTD = (item.balances && item.balances[`${latestYear}-${prevMStr}`]) ? item.balances[`${latestYear}-${prevMStr}`] : 0;
                                    }
                                    let movement = currentYTD - prevYTD;
                                    node.monthlyHistory.push(movement);
                                    totalHistYear += movement;
                                }
                                node.totalHistYear = totalHistYear;
                            });
                            
                            // Step 2: Render table framework and inputs
                            function fmt(amt) {
                                const rounded = Math.round(amt || 0);
                                if (rounded === 0) return '<span style="color:#adb5bd;">-</span>';
                                const formatted = Math.abs(rounded).toLocaleString('en-US');
                                if (rounded < 0) return `<span style="color:#dc3545;">(${formatted})</span>`;
                                return `<span>${formatted}</span>`;
                            }
                            
                            const projYearRaw = '{{ plan.start_date.year|default:"2026" }}'.replace(/,/g, '');
                            const projYearFull = parseInt(projYearRaw);
                            const projYearShort = String(projYearFull).slice(-2);
                            const prevYearFull = latestYear || (projYearFull - 1);
                            const prevYearShort = String(prevYearFull).slice(-2);
                            const months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];
                            
                            // Generate headers
                            window.renderStep7Headers = function() {
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
                            };
                            window.renderStep7Headers();

                            data.income_statement.sort((a, b) => {
                                let orderA = a.code.startsWith('5') ? 'A' : (a.code.startsWith('4') ? 'B' : 'C');
                                let orderB = b.code.startsWith('5') ? 'A' : (b.code.startsWith('4') ? 'B' : 'C');
                                return (orderA + a.code).localeCompare(orderB + b.code);
                            });
                            
                            let html = '';
                            data.income_statement.forEach(item => {
                                let node = accMap[item.code];
                                node.uiChildren = node.children_codes.filter(c => accMap[c]);
                                const hasChildren = node.uiChildren.length > 0;
                                
                                // Calculate unassignedBase0 to determine if parent needs inputs
                                let unassignedBase0 = node.baseBal;
                                if (hasChildren) {
                                    let childrenBaseSum = 0;
                                    node.uiChildren.forEach(c => childrenBaseSum += (accMap[c].baseBal || 0));
                                    unassignedBase0 = node.baseBal - childrenBaseSum;
                                }
                                node.years[0].unassignedBase = unassignedBase0;
                                
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
                                    if (hasChildren && Math.abs(unassignedBase0) < 0.01) {
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
                            $('#budget-monthly-tbody').html(html);

                            // Store cell references for fast DOM updates
                            let sortedCodes = Object.keys(accMap).sort((a, b) => b.length - a.length);
                            sortedCodes.forEach(code => {
                                let node = accMap[code];
                                if (!node.uiChildren) return;
                                
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
                            });

                            // Rollup and render engine v2
                            // Rollup and render engine v2
                            function recalculateStep7() {
                                console.log("[DEBUG] recalculateStep7 v2 running...");
                                let savedActive = activeYearIndex;
                                
                                // Loop through all years sequentially to build the cascade correctly
                                for (let yr = 0; yr < projectionYearsCount; yr++) {
                                    activeYearIndex = yr;
                                    
                                    // 1. Cascade baseBal from previous year
                                    sortedCodes.forEach(code => {
                                        let node = accMap[code];
                                        if (!node.uiChildren) return;
                                        if (yr > 0) {
                                            node.years[yr].baseBal = node.years[yr-1].totalProjected || 0;
                                        } else {
                                            node.years[yr].baseBal = node.baseBal;
                                        }
                                        
                                        // Calculate unassigned base for the year
                                        if (node.uiChildren.length > 0) {
                                            let childrenBaseSum = 0;
                                            node.uiChildren.forEach(c => childrenBaseSum += (accMap[c].years[yr].baseBal || 0));
                                            node.years[yr].unassignedBase = node.years[yr].baseBal - childrenBaseSum;
                                        } else {
                                            node.years[yr].unassignedBase = node.years[yr].baseBal;
                                        }
                                    });

                                    // 2. Project this year
                                    sortedCodes.forEach(code => {
                                        let node = accMap[code];
                                        if (!node.uiChildren) return;
                                        if (node.uiChildren.length > 0) {
                                            // Parent node rollup
                                            let sumProjected = 0;
                                            let monthlySums = new Array(12).fill(0);
                                            node.uiChildren.forEach(c => {
                                                sumProjected += accMap[c].years[yr].totalProjected || 0;
                                                for(let i=0; i<12; i++) {
                                                    monthlySums[i] += accMap[c].years[yr].monthlyProjected[i] || 0;
                                                }
                                            });

                                            let unassignedBase = node.years[yr].unassignedBase || 0;
                                            // If parent has unassigned balance, project it and add to rollup
                                            if (Math.abs(unassignedBase) >= 0.01) {
                                                let varVal = parseFloat(node.years[yr].val) || 0;
                                                let startMonth = parseInt($('#apply-var-month').val()) || 0;
                                                
                                                for(let i=0; i<12; i++) {
                                                    let baseMProj = 0;
                                                    if (node.totalHistYear !== 0) {
                                                        let weight = node.monthlyHistory[i] / node.totalHistYear;
                                                        baseMProj = unassignedBase * weight;
                                                    } else {
                                                        baseMProj = unassignedBase / 12;
                                                    }
                                                    
                                                    let mProj = baseMProj;
                                                    if (i >= startMonth) {
                                                        mProj = baseMProj * (1 + (varVal / 100));
                                                    } else {
                                                        mProj = baseMProj * (1 + ((node.baseTrend || 0) / 100));
                                                    }
                                                    
                                                    if (node.years[yr].monthlyOverrides && node.years[yr].monthlyOverrides[i] !== undefined) {
                                                        mProj = node.years[yr].monthlyOverrides[i];
                                                    }
                                                    
                                                    monthlySums[i] += mProj;
                                                    sumProjected += mProj;
                                                }
                                            }

                                            node.years[yr].totalProjected = sumProjected;
                                            node.years[yr].monthlyProjected = monthlySums;
                                            
                                        } else {
                                            // Leaf node distribution
                                            let varVal = parseFloat(node.years[yr].val) || 0;
                                            let startMonth = parseInt($('#apply-var-month').val()) || 0;
                                            
                                            let mProjArr = [];
                                            let sumProjected = 0;
                                            for(let i=0; i<12; i++) {
                                                let baseMProj = 0;
                                                if (node.totalHistYear !== 0) {
                                                    let weight = node.monthlyHistory[i] / node.totalHistYear;
                                                    baseMProj = node.years[yr].baseBal * weight;
                                                } else {
                                                    baseMProj = node.years[yr].baseBal / 12;
                                                }
                                                
                                                let mProj = baseMProj;
                                                if (i >= startMonth) {
                                                    mProj = baseMProj * (1 + (varVal / 100));
                                                } else {
                                                    mProj = baseMProj * (1 + ((node.baseTrend || 0) / 100));
                                                }
                                                
                                                if (node.years[yr].monthlyOverrides && node.years[yr].monthlyOverrides[i] !== undefined) {
                                                    mProj = node.years[yr].monthlyOverrides[i];
                                                }
                                                sumProjected += mProj;
                                                mProjArr.push(mProj);
                                            }
                                            node.years[yr].totalProjected = sumProjected;
                                            node.years[yr].monthlyProjected = mProjArr;
                                        }
                                    });
                                }
                                
                                // Restore active year
                                activeYearIndex = savedActive;
                                
                                // 3. Update DOM Cells
                                sortedCodes.forEach(code => {
                                    let node = accMap[code];
                                    if (!node.uiChildren) return;
                                    
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
                                });

                                // Update Summary
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
                                }
                            }

                            recalculateStep7();

                            $('#budget-monthly-tbody').on('dblclick', 'td[id^="cell-m"]', function() {
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
                            });

                            let step4Timeout;
                            $('.step7-input').on('input', function() {
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
                            });

                            window.copyPreviousYearData = function() {
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
                            };

                            window.applyHistoricalTrend = function() {
                                let btn = $('#btn-apply-trend');
                                let originalText = '<i class="fas fa-history mr-1"></i> Aplicar Tendencia Año Anterior';
                                btn.html('<i class="fas fa-spinner fa-spin mr-1"></i> Procesando Series (Pandas)...').prop('disabled', true);
                                
                                fetch("{% url 'financial_planning:ml_trend_projection' plan.id %}", {
                                    method: 'POST',
                                    headers: {
                                        'X-CSRFToken': '{{ csrf_token }}',
                                        'Content-Type': 'application/json'
                                    }
                                })
                                .then(response => {
                                    if (!response.ok) {
                                        throw new Error('Network response was not ok');
                                    }
                                    return response.json();
                                })
                                .then(result => {
                                    if(result.status === 'success' && result.trends) {
                                        data.income_statement.forEach(item => {
                                            let node = accMap[item.code];
                                            if (node && node.inputEls) {
                                                if (result.trends[item.code] !== undefined) {
                                                    let t = parseFloat(result.trends[item.code]);
                                                    for(let yr=0; yr<projectionYearsCount; yr++) {
                                                        node.years[yr].baseTrend = t;
                                                        node.years[yr].val = t;
                                                        if (node.inputEls[yr]) node.inputEls[yr].val(t.toFixed(2));
                                                    }
                                                }
                                            }
                                        });
                                        recalculateStep7();
                                        Swal.fire({
                                            toast: true,
                                            position: 'top-end',
                                            icon: 'success',
                                            title: 'Proyección generada vía NumPy/Pandas',
                                            showConfirmButton: false,
                                            timer: 3000
                                        });
                                    } else {
                                        Swal.fire('Error', result.msg || 'Error al procesar las series', 'error');
                                    }
                                })
                                .catch(err => {
                                    console.error(err);
                                    Swal.fire('Error', 'Hubo un error de conexión con el servidor. ¿Está activo el servidor?', 'error');
                                })
                                .finally(() => {
                                    btn.html(originalText).prop('disabled', false);
                                });
                            };

                            let step4Timeout;
                            $('.step7-input').on('input', function() {
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
                            });
                            
                            window.saveAssumptionsFromStep7 = function(btnId) {
                                const btn = $(btnId);
                                const originalHtml = btn.html();
                                const originalClasses = btn.attr('class');
                                
                                let reqData = {
                                    _meta: {
                                        startMonth: parseInt($('#apply-var-month').val()) || 0
                                    }
                                };
                                $('.step7-input').each(function() {
                                    const code = String($(this).data('code'));
                                    const node = accMap[code];
                                    if (node) {
                                        reqData[code] = { years: node.years };
                                    }
                                });
                                
                                console.log("[DEBUG] Sending assumptions payload:", reqData);
                                
                                btn.html('<i class="fas fa-spinner fa-spin"></i> Guardando...').prop('disabled', true);
                                $.ajax({
                                    url: "{% url 'financial_planning:save_institutional_assumptions' plan.id %}",
                                    method: "POST",
                                    contentType: 'application/json',
                                    data: JSON.stringify(reqData),
                                    headers: { "X-CSRFToken": "{{ csrf_token }}" },
                                    success: function(res) {
                                        if(res.status === 'success') {
                                            btn.html('<i class="fas fa-check"></i> Guardado exitoso').addClass('btn-success').removeClass('btn-outline-primary btn-primary');
                                            
                                            // Toast notification
                                            let toastHtml = `
                                            <div class="position-fixed p-3" style="z-index: 1050; right: 0; bottom: 0;">
                                              <div class="toast hide shadow-lg" role="alert" aria-live="assertive" aria-atomic="true" data-delay="3000">
                                                <div class="toast-header bg-success text-white">
                                                  <i class="fas fa-check-circle mr-2"></i>
                                                  <strong class="mr-auto">Éxito</strong>
                                                  <button type="button" class="ml-2 mb-1 close text-white" data-dismiss="toast" aria-label="Close">
                                                    <span aria-hidden="true">&times;</span>
                                                  </button>
                                                </div>
                                                <div class="toast-body font-weight-bold">
                                                  Presupuesto guardado correctamente.
                                                </div>
                                              </div>
                                            </div>`;
                                            $(toastHtml).appendTo('body');
                                            $('.toast').toast('show');
                                            
                                            setTimeout(() => {
                                                btn.attr('class', originalClasses).html(originalHtml).prop('disabled', false);
                                            }, 2000);
                                        } else {
                                            alert('Error: ' + res.msg);
                                            btn.attr('class', originalClasses).html(originalHtml).prop('disabled', false);
                                        }
                                    },
                                    error: function(xhr, status, error) {
                                        console.error("[ERROR] saveAssumptions AJAX:", status, error, xhr.responseText);
                                        alert('Error de conexión al guardar.');
                                        btn.attr('class', originalClasses).html(originalHtml).prop('disabled', false);
                                    }
                                });
                            };
                            
                        } else {
                            $('#budget-monthly-tbody').html('<tr><td colspan="16" class="text-center p-5 text-muted"><i class="fas fa-exclamation-triangle fa-2x mb-3 text-warning d-block"></i>Aún no se ha calculado la base del presupuesto.<br>Por favor, regrese al <b>Paso 4: Presupuesto Institucional</b> y asigne los datos.</td></tr>');
                        }
                    });
                    
                    window.toggleRow = function(code, icon) {
                        const $icon = $(icon);
                        const isExpanded = $icon.hasClass('fa-chevron-down');
                        
                        if (isExpanded) {
                            $icon.removeClass('fa-chevron-down').addClass('fa-chevron-right');
                            hideChildren(code);
                        } else {
                            $icon.removeClass('fa-chevron-right').addClass('fa-chevron-down');
                            showChildren(code);
                        }
                    };

                    function hideChildren(parentCode) {
                        $(`.budget-row[data-parent="${parentCode}"]`).each(function() {
                            const code = $(this).data('code');
                            $(this).hide();
                            hideChildren(code);
                        });
                    }

                    function showChildren(parentCode) {
                        $(`.budget-row[data-parent="${parentCode}"]`).each(function() {
                            const code = $(this).data('code');
                            $(this).show();
                            const $childIcon = $(this).find('.expand-toggle');
                            if ($childIcon.length === 0 || $childIcon.hasClass('fa-chevron-down')) {
                                showChildren(code);
                            }
                        });
                    }
                    
                    window.toggleZeroAccounts = function() {
                        const $tbody = $('#budget-monthly-tbody');
                        const $btn = $('#toggle-zero-accounts');
                        
                        if ($tbody.hasClass('hide-zeros')) {
                            $tbody.removeClass('hide-zeros');
                            $btn.html('<i class="fas fa-eye-slash mr-1"></i> Ocultar en Cero').removeClass('btn-primary').addClass('btn-outline-primary');
                        } else {
                            $tbody.addClass('hide-zeros');
                            $btn.html('<i class="fas fa-eye mr-1"></i> Mostrar en Cero').removeClass('btn-outline-primary').addClass('btn-primary');
                        }
                    };

                    window.expandToDigits = function(maxDigits) {
                        $('.budget-row').each(function() {
                            let code = String($(this).data('code'));
                            let parentCode = String($(this).data('parent') || '');
                            let $icon = $(this).find('.expand-toggle');
                            
                            if (parentCode === '' || parentCode.length < maxDigits) {
                                $(this).show();
                                if ($icon.length > 0) {
                                    if (code.length < maxDigits) {
                                        $icon.removeClass('fa-chevron-right').addClass('fa-chevron-down');
                                    } else {
                                        $icon.removeClass('fa-chevron-down').addClass('fa-chevron-right');
                                    }
                                }
                            } else {
                                $(this).hide();
                                if ($icon.length > 0) {
                                    $icon.removeClass('fa-chevron-down').addClass('fa-chevron-right');
                                }
                            }
                        });
                    };

                    window.executeExport = async function() {
                        const whatToExport = $('input[name="exportOption"]:checked').val();
                        const format = $('#exportFormat').val();
                        const digits = parseInt($('#exportDigits').val());
                        
                        // Close modal
                        $('#exportModal').modal('hide');
                        
                        let tableId = whatToExport === 'summary' ? 'budget-summary-table' : 'budget-monthly-table';
                        
                        if (format === 'pdf') {
                            // HTML2Canvas + jsPDF
                            const element = document.getElementById(tableId);
                            const canvas = await html2canvas(element, { scale: 2, useCORS: true, backgroundColor: '#ffffff' });
                            const imgData = canvas.toDataURL('image/png');
                            const { jsPDF } = window.jspdf;
                            const pdf = new jsPDF({ orientation: canvas.width > canvas.height ? 'l' : 'p', unit: 'mm', format: 'a4' });
                            
                            const pdfWidth = pdf.internal.pageSize.getWidth();
                            const pdfHeight = (canvas.height * pdfWidth) / canvas.width;
                            pdf.addImage(imgData, 'PNG', 0, 10, pdfWidth, pdfHeight);
                            pdf.save(`ER_Proyectado_Paso7.pdf`);
                        } else {
                            // Excel or CSV (SheetJS)
                            let aoa = [];
                            let $table = $(`#${tableId}`);
                            
                            // Headers
                            let headers = [];
                            $table.find('thead tr').each(function() {
                                $(this).find('th').each(function() {
                                    headers.push($(this).text().trim());
                                });
                            });
                            aoa.push(headers);
                            
                            // Rows
                            $table.find('tbody tr').each(function() {
                                if ($(this).css('display') === 'none') return; // Skip hidden
                                
                                let parentCode = $(this).data('parent') || '';
                                if (whatToExport === 'structure' && digits !== 99 && parentCode.length >= digits) return;
                                
                                let rowData = [];
                                let code = String($(this).data('code') || '');
                                $(this).find('td').each(function() {
                                    let text = $(this).text().trim();
                                    let input = $(this).find('input');
                                    if (input.length > 0) {
                                        text = input.val();
                                    }
                                    
                                    // Try parse float
                                    if (text !== '-') {
                                        let parsed = parseFloat(text.replace(/,/g, '').replace(/%/g, ''));
                                        if (!isNaN(parsed) && text !== code) { // Dont parse code like '5' or '51'
                                            rowData.push(parsed);
                                        } else {
                                            rowData.push(text);
                                        }
                                    } else {
                                        rowData.push(0);
                                    }
                                });
                                // Code column fix
                                if (whatToExport === 'structure' && rowData.length > 0 && String(rowData[0]).includes(code)) {
                                    rowData[0] = code;
                                }
                                aoa.push(rowData);
                            });
                            
                            const wb = XLSX.utils.book_new();
                            const ws = XLSX.utils.aoa_to_sheet(aoa);
                            XLSX.utils.book_append_sheet(wb, ws, 'Datos');
                            
                            if (format === 'excel') {
                                XLSX.writeFile(wb, `ER_Proyectado_Paso7.xlsx`);
                            } else if (format === 'csv') {
                                XLSX.writeFile(wb, `ER_Proyectado_Paso7.csv`, {bookType: 'csv'});
                            }
                        }
                    };
                