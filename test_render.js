const fs = require('fs');
const data = JSON.parse(fs.readFileSync('test_data.json', 'utf8'));

let currentBudgetData = data.data;
let currentVersionStatus = data.version_status;
window = { erAccounts: data.er_accounts || [], hasYieldParams: data.has_yield_params, hasCostParams: data.has_cost_params };

const CATEGORY_CONFIG = {
    'ING_FIN':    { name: 'INGRESOS FINANCIEROS',           sign: 1,  color: 'text-success', icon: 'fa-plus-circle' },
    'ING_SERV':   { name: 'INGRESOS POR SERVICIOS',         sign: 1,  color: 'text-success', icon: 'fa-plus-circle' },
    'OTROS_ING':  { name: 'OTROS INGRESOS',                 sign: 1,  color: 'text-success', icon: 'fa-plus-circle' },
    'GAS_FIN':    { name: 'GASTOS FINANCIEROS',             sign: -1, color: 'text-danger',  icon: 'fa-minus-circle' },
    'GAS_SERV':   { name: 'GASTOS POR SERVICIOS FIN.',      sign: -1, color: 'text-danger',  icon: 'fa-minus-circle' },
    'PROV':       { name: 'PROVISIONES',                    sign: -1, color: 'text-danger',  icon: 'fa-minus-circle' },
    'DEP_AMORT':  { name: 'DEPRECIACIÓN Y AMORTIZACIÓN',    sign: -1, color: 'text-warning', icon: 'fa-minus-circle' },
    'GAS_ADMIN':  { name: 'GASTOS ADMINISTRATIVOS',         sign: -1, color: 'text-danger',  icon: 'fa-minus-circle' },
    'OTROS_EG':   { name: 'OTROS EGRESOS',                  sign: -1, color: 'text-secondary',icon: 'fa-minus-circle' },
};

function fmt(val) {
    return parseFloat(val || 0).toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
}

function parseNum(val) {
    return parseFloat(String(val || '0').replace(/,/g, '')) || 0;
}

try {
    let grouped = {};
    currentBudgetData.forEach(item => {
        const cat = CATEGORY_CONFIG[item.category] ? item.category : 'OTROS_EG';
        if (!grouped[cat]) grouped[cat] = [];
        grouped[cat].push(item);
    });

    let html = '';
    let rY1 = 0, rY2 = 0, rY3 = 0;
    let ingY1 = 0, ingY2 = 0, ingY3 = 0;
    let egY1 = 0, egY2 = 0, egY3 = 0;
    let resMonths = new Array(12).fill(0);
    let ingMonths = new Array(12).fill(0);
    let egMonths = new Array(12).fill(0);
    const isApproved = currentVersionStatus === 'APPROVED';

    for (const catKey of Object.keys(CATEGORY_CONFIG)) {
        if (!grouped[catKey] || grouped[catKey].length === 0) continue;
        const catInfo = CATEGORY_CONFIG[catKey];
        
        let catMonths = new Array(12).fill(0);
        let catY1 = 0, catY2 = 0, catY3 = 0;
        
        grouped[catKey].forEach(item => {
            catY1 += parseFloat(item.y1_total) || 0;
            catY2 += parseFloat(item.y2_total) || 0;
            catY3 += parseFloat(item.y3_total) || 0;
            for (let i=0; i<12; i++) {
                catMonths[i] += parseFloat(item.monthly_values[i]) || 0;
            }
        });

        let catHtml = `<tr class="bg-light font-weight-bold border-top">
            <td class="${catInfo.color}" style="padding-left:10px;">
                <i class="fas ${catInfo.icon} mr-2"></i>${catInfo.name}
            </td>
            <td colspan="2"></td>`;
            
        for (let i = 0; i < 12; i++) {
            catHtml += `<td class="text-right text-monospace ${catInfo.color} cat-sum-m${i}-${catKey}">${fmt(catMonths[i])}</td>`;
        }
        catHtml += `<td class="text-right text-monospace ${catInfo.color} cat-sum-y1-${catKey}">${fmt(catY1)}</td>
                    <td class="text-right text-monospace ${catInfo.color} cat-sum-y2-${catKey}">${fmt(catY2)}</td>
                    <td class="text-right text-monospace ${catInfo.color} cat-sum-y3-${catKey}">${fmt(catY3)}</td>
        </tr>`;
        
        html += catHtml;

        grouped[catKey].forEach(item => {
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
                        filteredErAccounts = window.erAccounts.filter(a => String(a.val).startsWith(String(item.account_prefix)));
                    }
                    sourceOpts = `<option value="">-- Cuenta Base --</option>` + 
                        filteredErAccounts.map(a => `<option value="${a.val}" ${sourceVal === a.val ? 'selected' : ''}>${a.label}</option>`).join('');
                    sourceSelect = `<select class="form-control form-control-sm source-select select2" style="font-size:0.75rem;">${sourceOpts}</select>`;
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
                } else {
                    // MANUAL: show historical account selector + % adjustment + load button
                    let filteredErAccounts = window.erAccounts;
                    if (item.account_prefix) {
                        filteredErAccounts = window.erAccounts.filter(a => String(a.val).startsWith(String(item.account_prefix)));
                    }
                    sourceOpts = `<option value="">-- Seleccionar Cuenta --</option>` + 
                        filteredErAccounts.map(a => `<option value="${a.val}" ${sourceVal === a.val ? 'selected' : ''}>${a.label}</option>`).join('');
                    sourceSelect = `<div class="d-flex align-items-center" style="gap:3px;">
                        <select class="form-control form-control-sm source-select select2" style="font-size:0.72rem;min-width:120px;">${sourceOpts}</select>
                        <div class="input-group input-group-sm" style="width:90px;flex-shrink:0;">
                            <input type="number" class="form-control form-control-sm text-center pct-adjustment" 
                                style="font-size:0.72rem;padding:2px 4px;" value="0" step="0.5" 
                                title="% de ajuste sobre dato histórico">
                            <div class="input-group-append"><span class="input-group-text" style="font-size:0.72rem;padding:2px 4px;">%</span></div>
                        </div>
                        <button type="button" class="btn btn-sm btn-outline-info" style="font-size:0.7rem;padding:2px 6px;white-space:nowrap;" 
                            onclick="loadHistoricalForManual(this)" title="Cargar datos históricos con ajuste %">
                            <i class="fas fa-download"></i>
                        </button>
                    </div>`;
                }

                rY1 += item.y1_total * catInfo.sign;
                rY2 += item.y2_total * catInfo.sign;
                rY3 += item.y3_total * catInfo.sign;
                if (catInfo.sign === 1) {
                    ingY1 += item.y1_total;
                    ingY2 += item.y2_total;
                    ingY3 += item.y3_total;
                } else {
                    egY1 += item.y1_total;
                    egY2 += item.y2_total;
                    egY3 += item.y3_total;
                }

                let monthCells = '';
                for (let i = 0; i < 12; i++) {
                    const mVal = item.monthly_values[i] || 0;
                    resMonths[i] += mVal * catInfo.sign;
                    if (catInfo.sign === 1) ingMonths[i] += mVal;
                    else egMonths[i] += mVal;
                    
                    const val = fmt(mVal);
                    if (!isManual || isApproved) {
                        monthCells += `<td class="text-right text-monospace" style="min-width:85px;padding:4px 6px;font-size:0.8rem;">
                            <span class="month-input" data-month="${i}" data-raw="${(item.monthly_values[i] || 0)}">${val}</span></td>`;
                    } else {
                        monthCells += `<td style="min-width:85px;"><input type="text" inputmode="decimal"
                            class="month-input form-control form-control-sm text-right bg-white" style="width:84px;font-size:0.8rem;"
                            data-month="${i}" value="${val}"
                            onfocus="this.value=this.value.replace(/,/g,'');this.select();"
                            onblur="this.value=fmt_local(parseNum(this.value));updateRowTotal(this);"
                            onchange="updateRowTotal(this)"></td>`;
                    }
                }
            } // Close if(!isApproved) else
        });
    }
    console.log('Success HTML length:', html.length);
} catch (e) {
    console.error('ERROR:', e.stack);
}
