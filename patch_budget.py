import re

filepath = r'c:\Users\VICTUS\Desktop\A.RISK ERM - V2\templates\financial_planning\institutional_budget_builder.html'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# I will replace the inside of renderBudgetTable() with a new version
# I need to find the start of `function renderBudgetTable() {` and the end of it.

start_str = "    function renderBudgetTable() {"
end_str = "        updateUIForStatus();\n    }"
start_idx = content.find(start_str)
end_idx = content.find(end_str, start_idx) + len(end_str)

if start_idx == -1 or end_idx == -1:
    print("Could not find renderBudgetTable")
else:
    new_render = """    function renderBudgetTable() {
        const tbody = document.getElementById('budget-table-body');
        if (currentBudgetData.length === 0) {
            tbody.innerHTML = `<tr><td colspan="17" class="text-center py-5 text-muted">
                <i class="fas fa-folder-open fa-3x mb-3 text-secondary d-block"></i>
                No hay rubros presupuestales. Haz clic en <strong>"Inicializar Rubros"</strong> y luego <strong>"Sincronizar con Tendencias"</strong>.
            </td></tr>`;
            return;
        }

        const digit1Names = { '4': 'EGRESOS', '5': 'INGRESOS' };
        const digit2Names = {
            '51': 'INGRESOS FINANCIEROS', '52': 'INGRESOS POR SERVICIOS',
            '53': 'INGRESOS POR SERVICIOS FINANCIEROS', '54': 'OTROS INGRESOS',
            '56': 'UTILIDADES EN VENTA DE BIENES', '57': 'INGRESOS DIVERSOS',
            '59': 'CARGAS IMPUTABLES', '41': 'GASTOS FINANCIEROS',
            '42': 'GASTOS POR SERVICIOS FINANCIEROS', '43': 'PROVISIONES',
            '44': 'DEPRECIACIÓN Y AMORTIZACIÓN', '45': 'GASTOS ADMINISTRATIVOS',
            '46': 'GASTOS DE VENTAS', '49': 'OTRAS CARGAS IMPUTABLES',
        };

        // Group by 1 digit, then 2 digit
        let hierarchy = { '5': {}, '4': {} };
        currentBudgetData.forEach(item => {
            const pfx = item.account_prefix || '';
            const d1 = pfx.substring(0, 1) || (CATEGORY_CONFIG[item.category].sign === 1 ? '5' : '4');
            const d2 = pfx.substring(0, 2) || (CATEGORY_CONFIG[item.category].sign === 1 ? '50' : '40');
            
            if (!hierarchy[d1]) hierarchy[d1] = {};
            if (!hierarchy[d1][d2]) hierarchy[d1][d2] = [];
            hierarchy[d1][d2].push(item);
        });

        let html = '';
        let rY1 = 0, rY2 = 0, rY3 = 0;
        let ingY1 = 0, ingY2 = 0, ingY3 = 0;
        let egY1 = 0, egY2 = 0, egY3 = 0;
        let resMonths = new Array(12).fill(0);
        let ingMonths = new Array(12).fill(0);
        let egMonths = new Array(12).fill(0);
        const isApproved = currentVersionStatus === 'APPROVED';

        for (const d1 of ['5', '4']) {
            if (Object.keys(hierarchy[d1]).length === 0) continue;
            const sign = d1 === '5' ? 1 : -1;
            const color = d1 === '5' ? 'text-success' : 'text-danger';
            const icon = d1 === '5' ? 'fa-plus-circle' : 'fa-minus-circle';
            const d1Name = digit1Names[d1] || 'OTRAS CUENTAS';

            let d1Months = new Array(12).fill(0);
            let d1Y1 = 0, d1Y2 = 0, d1Y3 = 0;

            let d1Html = '';

            // Render children first to sum up
            let d2HtmlAcc = '';
            for (const d2 of Object.keys(hierarchy[d1]).sort()) {
                const items = hierarchy[d1][d2];
                let d2Months = new Array(12).fill(0);
                let d2Y1 = 0, d2Y2 = 0, d2Y3 = 0;
                let itemsHtml = '';

                items.forEach(item => {
                    let itemMonths = new Array(12).fill(0);
                    for (let i = 0; i < 12; i++) {
                        const mVal = parseFloat(item.monthly_values[i]) || 0;
                        itemMonths[i] = mVal;
                        d2Months[i] += mVal;
                        d1Months[i] += mVal;
                        resMonths[i] += mVal * sign;
                        if (sign === 1) ingMonths[i] += mVal;
                        else egMonths[i] += mVal;
                    }
                    
                    const iY1 = parseFloat(item.y1_total) || 0;
                    const iY2 = parseFloat(item.y2_total) || 0;
                    const iY3 = parseFloat(item.y3_total) || 0;
                    d2Y1 += iY1; d2Y2 += iY2; d2Y3 += iY3;
                    d1Y1 += iY1; d1Y2 += iY2; d1Y3 += iY3;
                    
                    rY1 += iY1 * sign; rY2 += iY2 * sign; rY3 += iY3 * sign;
                    if (sign === 1) { ingY1 += iY1; ingY2 += iY2; ingY3 += iY3; } 
                    else { egY1 += iY1; egY2 += iY2; egY3 += iY3; }

                    const isManual = item.calc_type === 'MANUAL';
                    let calcSelect = '';
                    let sourceSelect = '';
                    if (isApproved) {
                        calcSelect = `<span class="badge badge-secondary">${item.calc_type}</span>`;
                        sourceSelect = `<span class="badge badge-light border">${item.source_trend_variable || '-'}</span>`;
                    } else {
                        const calcOpts = [
                            {val: 'MANUAL', label: 'Manual'},
                            {val: 'TREND', label: 'Tendencia'},
                            {val: 'HISTORICAL', label: 'Histórica'}
                        ].map(o => `<option value="${o.val}" ${item.calc_type === o.val ? 'selected' : ''}>${o.label}</option>`).join('');
                        calcSelect = `<select class="form-control form-control-sm calc-type-select" style="font-size:0.75rem;" onchange="updateRowType(this)">${calcOpts}</select>`;
                        
                        const sourceVal = item.source_trend_variable || '';
                        let sourceOpts = '';
                        if (item.calc_type === 'HISTORICAL') {
                            let filteredErAccounts = window.erAccounts;
                            if (item.account_prefix) {
                                filteredErAccounts = window.erAccounts.filter(a => a.val.startsWith(item.account_prefix));
                            }
                            sourceOpts = `<option value="">-- Cuenta --</option>` + 
                                filteredErAccounts.map(a => `<option value="${a.val}" ${sourceVal === a.val ? 'selected' : ''}>${a.label}</option>`).join('');
                            sourceSelect = `<div class="d-flex align-items-center" style="gap:3px;">
                                <select class="form-control form-control-sm source-select select2" style="font-size:0.72rem;min-width:120px;">${sourceOpts}</select>
                                <div class="input-group input-group-sm" style="width:90px;flex-shrink:0;">
                                    <input type="number" class="form-control form-control-sm text-center pct-adjustment" style="font-size:0.72rem;padding:2px 4px;" value="0" step="0.5">
                                    <div class="input-group-append"><span class="input-group-text" style="font-size:0.72rem;padding:2px 4px;">%</span></div>
                                </div>
                                <button type="button" class="btn btn-sm btn-outline-info" style="font-size:0.7rem;padding:2px 6px;" onclick="loadHistoricalForManual(this)"><i class="fas fa-download"></i></button>
                            </div>`;
                        } else if (item.calc_type === 'TREND') {
                            sourceOpts = `<option value="">-- Variable --</option>
                                <option value="cartera" ${sourceVal === 'cartera' ? 'selected' : ''}>Cartera</option>
                                <option value="rendimiento_cartera" ${sourceVal === 'rendimiento_cartera' ? 'selected' : ''}>Rendimiento Cartera</option>
                                <option value="ahorros" ${sourceVal === 'ahorros' ? 'selected' : ''}>Ahorros</option>
                                <option value="dpf" ${sourceVal === 'dpf' ? 'selected' : ''}>Plazo Fijo</option>
                                <option value="aportes" ${sourceVal === 'aportes' ? 'selected' : ''}>Aportaciones</option>
                                <option value="socios" ${sourceVal === 'socios' ? 'selected' : ''}>Nro Socios</option>
                                <option value="mora_soles" ${sourceVal === 'mora_soles' ? 'selected' : ''}>Mora</option>`;
                            sourceSelect = `<select class="form-control form-control-sm source-select select2" style="font-size:0.75rem;">${sourceOpts}</select>`;
                        }
                    }

                    let monthCells = '';
                    for (let i = 0; i < 12; i++) {
                        const val = fmt(itemMonths[i]);
                        if (!isManual || isApproved) {
                            monthCells += `<td class="text-right text-monospace" style="min-width:85px;padding:4px 6px;font-size:0.8rem;">
                                <span class="month-input" data-month="${i}" data-raw="${itemMonths[i]}">${val}</span></td>`;
                        } else {
                            monthCells += `<td style="min-width:85px;"><input type="text" inputmode="decimal"
                                class="month-input form-control form-control-sm text-right bg-white" style="width:84px;font-size:0.8rem;"
                                data-month="${i}" value="${val}"
                                onfocus="this.value=this.value.replace(/,/g,'');this.select();"
                                onblur="this.value=fmt_local(parseNum(this.value));updateRowTotal(this);"
                                onchange="updateRowTotal(this)"></td>`;
                        }
                    }

                    const y2fmt = fmt(iY2);
                    const y3fmt = fmt(iY3);
                    const y2Cell = (!isManual || isApproved) ? `<td class="text-right text-monospace" style="min-width:100px;padding:4px 6px;font-size:0.8rem;"><span class="y2-input" data-raw="${iY2}">${y2fmt}</span></td>`
                        : `<td style="min-width:100px;"><input type="text" inputmode="decimal" class="y2-input form-control form-control-sm text-right bg-white" style="width:98px;font-size:0.8rem;" value="${y2fmt}" onfocus="this.value=this.value.replace(/,/g,'');this.select();" onblur="this.value=fmt_local(parseNum(this.value));updateRowTotal(this);" onchange="updateRowTotal(this)"></td>`;
                    const y3Cell = (!isManual || isApproved) ? `<td class="text-right text-monospace" style="min-width:100px;padding:4px 6px;font-size:0.8rem;"><span class="y3-input" data-raw="${iY3}">${y3fmt}</span></td>`
                        : `<td style="min-width:100px;"><input type="text" inputmode="decimal" class="y3-input form-control form-control-sm text-right bg-white" style="width:98px;font-size:0.8rem;" value="${y3fmt}" onfocus="this.value=this.value.replace(/,/g,'');this.select();" onblur="this.value=fmt_local(parseNum(this.value));updateRowTotal(this);" onchange="updateRowTotal(this)"></td>`;

                    itemsHtml += `<tr class="lvl4 lvl4-${d2} lvl4-${d1}" data-item-id="${item.item_id}" data-calc-type="${item.calc_type}" data-sign="${sign}" data-category="${item.category}" data-account-prefix="${item.account_prefix || ''}" style="background-color: #fafafa;">
                        <td class="pl-5" style="min-width:260px; border-left: 3px solid #dee2e6;"><span class="text-muted mr-1">${item.account_prefix}</span> ${item.name}</td>
                        <td class="text-center">${calcSelect}</td>
                        <td class="text-center">${sourceSelect}</td>
                        ${monthCells}
                        <td class="bg-light font-weight-bold text-right text-monospace y1-total" style="min-width:110px;">${fmt(iY1)}</td>
                        ${y2Cell}${y3Cell}
                    </tr>`;
                });

                // Level 2 Header
                const d2Name = digit2Names[d2] || 'OTRAS CUENTAS';
                let d2Html = `<tr class="bg-light font-weight-bold border-top lvl2 lvl2-${d1}" style="cursor:pointer;" onclick="$('.lvl4-${d2}').toggle(); $(this).find('.toggle-icon').toggleClass('fa-chevron-down fa-chevron-right');">
                    <td class="${color}" style="padding-left:25px;">
                        <i class="fas fa-chevron-down mr-2 toggle-icon text-secondary" style="width:14px;"></i> ${d2} - ${d2Name}
                    </td>
                    <td colspan="2"></td>`;
                for (let i = 0; i < 12; i++) {
                    d2Html += `<td class="text-right text-monospace ${color} cat-sum-m${i}-${d2}">${fmt(d2Months[i])}</td>`;
                }
                d2Html += `<td class="text-right text-monospace ${color} cat-sum-y1-${d2}">${fmt(d2Y1)}</td>
                            <td class="text-right text-monospace ${color} cat-sum-y2-${d2}">${fmt(d2Y2)}</td>
                            <td class="text-right text-monospace ${color} cat-sum-y3-${d2}">${fmt(d2Y3)}</td>
                </tr>`;
                
                d2HtmlAcc += d2Html + itemsHtml;
            }

            // Level 1 Header
            d1Html = `<tr class="bg-white font-weight-bold border-top border-bottom lvl1" style="cursor:pointer; background-color: #f1f3f5 !important;" onclick="const isCollapsed = $(this).find('.toggle-icon').hasClass('fa-chevron-right'); if(isCollapsed){ $('.lvl2-${d1}').show(); $('.lvl4-${d1}').show(); $(this).find('.toggle-icon').removeClass('fa-chevron-right').addClass('fa-chevron-down'); $('.lvl2-${d1} .toggle-icon').removeClass('fa-chevron-right').addClass('fa-chevron-down'); } else { $('.lvl2-${d1}').hide(); $('.lvl4-${d1}').hide(); $(this).find('.toggle-icon').removeClass('fa-chevron-down').addClass('fa-chevron-right'); }">
                <td class="${color}" style="padding-left:10px; font-size: 1.05rem;">
                    <i class="fas fa-chevron-down mr-2 toggle-icon text-dark" style="width:14px;"></i><i class="fas ${icon} mr-2"></i>${d1} - ${d1Name}
                </td>
                <td colspan="2"></td>`;
            for (let i = 0; i < 12; i++) {
                d1Html += `<td class="text-right text-monospace ${color}">${fmt(d1Months[i])}</td>`;
            }
            d1Html += `<td class="text-right text-monospace ${color}">${fmt(d1Y1)}</td>
                        <td class="text-right text-monospace ${color}">${fmt(d1Y2)}</td>
                        <td class="text-right text-monospace ${color}">${fmt(d1Y3)}</td>
            </tr>`;

            html += d1Html + d2HtmlAcc;
        }

        tbody.innerHTML = html;
        for(let i=0; i<12; i++) {
            document.getElementById('footer-ing-m'+i).innerText = fmt(ingMonths[i]);
            document.getElementById('footer-eg-m'+i).innerText = fmt(egMonths[i]);
            document.getElementById('footer-res-m'+i).innerText = fmt(resMonths[i]);
        }
        document.getElementById('footer-ing-y1').innerText = fmt(ingY1);
        document.getElementById('footer-ing-y2').innerText = fmt(ingY2);
        document.getElementById('footer-ing-y3').innerText = fmt(ingY3);
        document.getElementById('footer-eg-y1').innerText = fmt(egY1);
        document.getElementById('footer-eg-y2').innerText = fmt(egY2);
        document.getElementById('footer-eg-y3').innerText = fmt(egY3);
        document.getElementById('footer-y1').innerText = fmt(rY1);
        document.getElementById('footer-y2').innerText = fmt(rY2);
        document.getElementById('footer-y3').innerText = fmt(rY3);
        
        $('.select2').select2({ width: '100%' });
        updateUIForStatus();
    }"""

    new_content = content[:start_idx] + new_render + content[end_idx:]
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Done")
