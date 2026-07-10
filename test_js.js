(function() {
    let currentBudgetData = [];
    let currentVersionStatus = 'DRAFT';
    const planId = '{{ plan.id }}';
    const csrfToken = '{{ csrf_token }}';

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

    // Strip commas before parsing (text inputs show "1,234.56")
    function parseNum(val) {
        return parseFloat(String(val || '0').replace(/,/g, '')) || 0;
    }

    function renderBudgetTable() {
        const tbody = document.getElementById('budget-table-body');
        if (currentBudgetData.length === 0) {
            tbody.innerHTML = `<tr><td colspan="17" class="text-center py-5 text-muted">
                <i class="fas fa-folder-open fa-3x mb-3 text-secondary d-block"></i>
                No hay rubros presupuestales. Haz clic en <strong>"Inicializar Rubros"</strong> y luego <strong>"Sincronizar con Tendencias"</strong>.
            </td></tr>`;
            return;
        }

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
                            filteredErAccounts = window.erAccounts.filter(a => a.val.startsWith(item.account_prefix));
                        }
                        sourceOpts = `<option value="">-- Cuenta Base --</option>` + 
                            filteredErAccounts.map(a => `<option value="${a.val}" ${sourceVal === a.val ? 'selected' : ''}>${a.label}</option>`).join('');
                    } else if (item.calc_type === 'TREND') {
                        sourceOpts = `<option value="">-- Variable --</option>
                            <option value="cartera" ${sourceVal === 'cartera' ? 'selected' : ''}>Cartera</option>
                            <option value="rendimiento_cartera" ${sourceVal === 'rendimiento_cartera' ? 'selected' : ''}>Rendimiento Cartera</option>
                            <option value="ahorros" ${sourceVal === 'ahorros' ? 'selected' : ''}>Ahorros</option>
                            <option value="dpf" ${sourceVal === 'dpf' ? 'selected' : ''}>Plazo Fijo</option>
                            <option value="aportes" ${sourceVal === 'aportes' ? 'selected' : ''}>Aportaciones</option>
                            <option value="socios" ${sourceVal === 'socios' ? 'selected' : ''}>Nro Socios</option>
                            <option value="mora_soles" ${sourceVal === 'mora_soles' ? 'selected' : ''}>Mora</option>`;
                    } else {
                        sourceOpts = `<option value="">-- N/A --</option>`;
                    }
                    sourceSelect = `<select class="form-control form-control-sm source-select select2" style="font-size:0.75rem;">${sourceOpts}</select>`;
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

                const y2fmt = fmt(item.y2_total);
                const y3fmt = fmt(item.y3_total);
                const y2Cell = (!isManual || isApproved)
                    ? `<td class="text-right text-monospace" style="min-width:100px;padding:4px 6px;font-size:0.8rem;"><span class="y2-input" data-raw="${item.y2_total}">${y2fmt}</span></td>`
                    : `<td style="min-width:100px;"><input type="text" inputmode="decimal" class="y2-input form-control form-control-sm text-right bg-white" style="width:98px;font-size:0.8rem;" value="${y2fmt}"
                        onfocus="this.value=this.value.replace(/,/g,'');this.select();"
                        onblur="this.value=fmt_local(parseNum(this.value));updateRowTotal(this);" onchange="updateRowTotal(this)"></td>`;
                const y3Cell = (!isManual || isApproved)
                    ? `<td class="text-right text-monospace" style="min-width:100px;padding:4px 6px;font-size:0.8rem;"><span class="y3-input" data-raw="${item.y3_total}">${y3fmt}</span></td>`
                    : `<td style="min-width:100px;"><input type="text" inputmode="decimal" class="y3-input form-control form-control-sm text-right bg-white" style="width:98px;font-size:0.8rem;" value="${y3fmt}"
                        onfocus="this.value=this.value.replace(/,/g,'');this.select();"
                        onblur="this.value=fmt_local(parseNum(this.value));updateRowTotal(this);" onchange="updateRowTotal(this)"></td>`;

                html += `<tr data-item-id="${item.item_id}" data-calc-type="${item.calc_type}" data-sign="${catInfo.sign}" data-category="${catKey}" data-account-prefix="${item.account_prefix || ''}">
                    <td class="pl-4" style="min-width:260px;">${item.name}</td>
                    <td class="text-center">${calcSelect}</td>
                    <td class="text-center">${sourceSelect}</td>
                    ${monthCells}
                    <td class="bg-light font-weight-bold text-right text-monospace y1-total" style="min-width:110px;">${fmt(item.y1_total)}</td>
                    ${y2Cell}${y3Cell}
                </tr>`;
            });
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
    }

    window.fmt_local = fmt;

    window.updateRowType = function(sel) {
        const tr = sel.closest('tr');
        tr.dataset.calcType = sel.value;
        const srcSelect = tr.querySelector('.source-select');
        const accountPrefix = tr.dataset.accountPrefix;
        
        if (srcSelect) {
            if ($(srcSelect).hasClass("select2-hidden-accessible")) {
                $(srcSelect).select2('destroy');
            }

            if (sel.value === 'HISTORICAL') {
                let filteredErAccounts = window.erAccounts;
                if (accountPrefix) {
                    filteredErAccounts = window.erAccounts.filter(a => a.val.startsWith(accountPrefix));
                }
                srcSelect.innerHTML = `<option value="">-- Cuenta Base --</option>` + 
                    filteredErAccounts.map(a => `<option value="${a.val}">${a.label}</option>`).join('');
            } else if (sel.value === 'TREND') {
                srcSelect.innerHTML = `<option value="">-- Variable --</option>
                    <option value="cartera">Cartera</option>
                    <option value="rendimiento_cartera">Rendimiento Cartera</option>
                    <option value="ahorros">Ahorros</option>
                    <option value="dpf">Plazo Fijo</option>
                    <option value="aportes">Aportaciones</option>
                    <option value="socios">Nro Socios</option>
                    <option value="mora_soles">Mora</option>`;
            } else {
                srcSelect.innerHTML = `<option value="">-- N/A --</option>`;
            }
            $(srcSelect).select2({ width: '100%' });
        }
    };

    window.updateRowTotal = function(inp) {
        const tr = inp.closest('tr');
        let y1 = 0;
        tr.querySelectorAll('.month-input').forEach(el => {
            y1 += el.dataset.raw !== undefined ? parseNum(el.dataset.raw) : parseNum(el.value);
        });
        tr.querySelector('.y1-total').innerText = fmt(y1);
        recalcFooter();
    };

    function getMonthVal(el) {
        return el.dataset.raw !== undefined ? parseNum(el.dataset.raw) : parseNum(el.value);
    }
    function getYearVal(el) {
        return el && el.dataset.raw !== undefined ? parseNum(el.dataset.raw) : parseNum(el?.value);
    }

    function recalcFooter() {
        let rY1 = 0, rY2 = 0, rY3 = 0;
        let ingY1 = 0, ingY2 = 0, ingY3 = 0;
        let egY1 = 0, egY2 = 0, egY3 = 0;
        let resMonths = new Array(12).fill(0);
        let ingMonths = new Array(12).fill(0);
        let egMonths = new Array(12).fill(0);
        
        let catTotals = {};
        Object.keys(CATEGORY_CONFIG).forEach(c => {
            catTotals[c] = { m: new Array(12).fill(0), y1:0, y2:0, y3:0 };
        });

        document.querySelectorAll('#budget-table-body tr[data-item-id]').forEach(tr => {
            const sign = parseInt(tr.dataset.sign || '1');
            const cat = tr.dataset.category || 'OTROS_EG';
            let y1 = 0;
            tr.querySelectorAll('.month-input').forEach((el, i) => {
                const mVal = getMonthVal(el);
                y1 += mVal;
                resMonths[i] += mVal * sign;
                if (sign === 1) ingMonths[i] += mVal;
                else egMonths[i] += mVal;
                if (catTotals[cat]) catTotals[cat].m[i] += mVal;
            });
            const y2 = getYearVal(tr.querySelector('.y2-input'));
            const y3 = getYearVal(tr.querySelector('.y3-input'));
            rY1 += y1 * sign;
            rY2 += y2 * sign;
            rY3 += y3 * sign;
            if (sign === 1) {
                ingY1 += y1; ingY2 += y2; ingY3 += y3;
            } else {
                egY1 += y1; egY2 += y2; egY3 += y3;
            }
            if (catTotals[cat]) {
                catTotals[cat].y1 += y1;
                catTotals[cat].y2 += y2;
                catTotals[cat].y3 += y3;
            }
        });
        
        Object.keys(catTotals).forEach(c => {
            for(let i=0; i<12; i++) {
                const el = document.querySelector(`.cat-sum-m${i}-${c}`);
                if (el) el.innerText = fmt(catTotals[c].m[i]);
            }
            const elY1 = document.querySelector(`.cat-sum-y1-${c}`);
            if (elY1) elY1.innerText = fmt(catTotals[c].y1);
            const elY2 = document.querySelector(`.cat-sum-y2-${c}`);
            if (elY2) elY2.innerText = fmt(catTotals[c].y2);
            const elY3 = document.querySelector(`.cat-sum-y3-${c}`);
            if (elY3) elY3.innerText = fmt(catTotals[c].y3);
        });
        
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
    }

    function updateUIForStatus() {
        const badge = document.getElementById('budget-status-badge');
        const btnSave = document.getElementById('btnSaveBudget');
        const btnApprove = document.getElementById('btnApproveBudget');
        if (currentVersionStatus === 'APPROVED') {
            badge.className = 'badge badge-success px-3 py-2 rounded-pill shadow-sm';
            badge.innerHTML = '<i class="fas fa-check-double mr-1"></i> Aprobado';
            btnSave.disabled = true;
            btnApprove.disabled = true;
        } else {
            badge.className = 'badge badge-warning px-3 py-2 rounded-pill shadow-sm';
            badge.innerHTML = '<i class="fas fa-pen mr-1"></i> Borrador';
            btnSave.disabled = false;
            btnApprove.disabled = false;
        }
    }

    window.loadBudgetData = function() {
        const scenario = document.getElementById('budget-scenario').value;
        document.getElementById('budget-table-body').innerHTML =
            '<tr><td colspan="17" class="text-center py-4"><div class="spinner-border text-primary" role="status"></div><p class="mt-2 text-muted">Cargando presupuesto...</p></td></tr>';

        fetch(`/planificacion-financiera/plan/${planId}/api/api_get_budget_data/?scenario=${scenario}&_t=${Date.now()}`)
            .then(r => r.json())
            .then(data => {
                if (data.status === 'success') {
                    currentBudgetData = data.data;
                    currentVersionStatus = data.version_status;
                    window.hasYieldParams = data.has_yield_params;
                    window.hasCostParams = data.has_cost_params;
                    window.erAccounts = data.er_accounts || [];
                    renderBudgetTable();
                } else {
                    document.getElementById('budget-table-body').innerHTML =
                        `<tr><td colspan="17" class="text-center py-4 text-danger"><i class="fas fa-exclamation-triangle fa-2x mb-2"></i><br>${data.message || 'Error desconocido'}</td></tr>`;
                }
            })
            .catch(err => {
                console.error(err);
                document.getElementById('budget-table-body').innerHTML =
                    '<tr><td colspan="17" class="text-center py-4 text-danger"><i class="fas fa-exclamation-triangle"></i> Error de conexión.</td></tr>';
            });
    };

    window.seedAndSync = function() {
        Swal.fire({
            title: 'Inicializar Rubros',
            text: 'Se crearán los rubros presupuestales estándar (Ingresos, Gastos Financieros, Administrativos, etc.) vinculados al plan de cuentas.',
            icon: 'question',
            showCancelButton: true,
            confirmButtonText: 'Inicializar'
        }).then(res => {
            if (!res.isConfirmed) return;
            Swal.fire({title: 'Inicializando...', allowOutsideClick: false, didOpen: () => Swal.showLoading()});
            fetch(`/planificacion-financiera/plan/${planId}/api/api_seed_budget_items/`, {
                method: 'POST',
                headers: {'X-CSRFToken': csrfToken}
            })
            .then(r => r.json())
            .then(data => {
                if (data.status === 'success') {
                    Swal.fire('Listo', data.message, 'success').then(() => loadBudgetData());
                } else {
                    Swal.fire('Error', data.message, 'error');
                }
            })
            .catch(() => Swal.fire('Error', 'Error de red', 'error'));
        });
    };

    window.syncWithTrends = function() {
        if (currentVersionStatus === 'APPROVED') {
            Swal.fire('Aviso', 'No se puede sincronizar un presupuesto aprobado.', 'warning');
            return;
        }
        
        const tableData = gatherTableData();
        let missingParams = false;
        let missingType = '';
        
        for (const row of tableData) {
            if (row.calc_type === 'TREND') {
                if (row.source_trend_variable === 'rendimiento_cartera' && !window.hasYieldParams) {
                    missingParams = true;
                    missingType = 'Rendimiento de Cartera (Paso 2)';
                    break;
                }
                if (['ahorros', 'dpf', 'ahorros_usd', 'dpf_usd'].includes(row.source_trend_variable) && !window.hasCostParams) {
                    missingParams = true;
                    missingType = 'Costos Financieros de Pasivos (Paso 2)';
                    break;
                }
            }
        }
        
        if (missingParams) {
            Swal.fire({
                title: 'Faltan Supuestos Institucionales',
                html: `Se requiere configurar los supuestos para <b>${missingType}</b> antes de sincronizar estos rubros. Por favor, regresa al Paso 2 y completa la información.`,
                icon: 'warning'
            });
            return;
        }

        const scenario = document.getElementById('budget-scenario').value;
        Swal.fire({
            title: 'Sincronizar con Tendencias',
            html: `Calculará <b>Ingresos y Gastos</b> proyectados tomando como base el <b>E.R. Histórico 2025</b> y aplicando las tasas de crecimiento del Paso 6.`,
            icon: 'info',
            showCancelButton: true,
            confirmButtonText: 'Sincronizar'
        }).then(res => {
            if (!res.isConfirmed) return;
            Swal.fire({title: 'Calculando...', allowOutsideClick: false, didOpen: () => Swal.showLoading()});
            
            fetch(`/planificacion-financiera/plan/${planId}/api/api_save_budget_version/`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json', 'X-CSRFToken': csrfToken},
                body: JSON.stringify({scenario, lines: tableData})
            }).then(() => {
                fetch(`/planificacion-financiera/plan/${planId}/api/api_sync_budget_trends/`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json', 'X-CSRFToken': csrfToken},
                    body: JSON.stringify({scenario: scenario})
                })
                .then(r => r.json())
                .then(data => {
                    if (data.status === 'success') {
                        Swal.fire('Éxito', data.message, 'success').then(() => loadBudgetData());
                    } else {
                        Swal.fire('Error', data.message || 'Error en la sincronización', 'error');
                    }
                })
                .catch(() => Swal.fire('Error', 'Error de red', 'error'));
            });
        });
    };

    let erPanelLoaded = false;
    window.toggleErPanel = function() {
        const panel = document.getElementById('er-historico-panel');
        if (panel.style.display === 'none') {
            panel.style.display = 'block';
            if (!erPanelLoaded) loadErHistorico();
        } else {
            panel.style.display = 'none';
        }
    };

    function loadErHistorico() {
        fetch(`/planificacion-financiera/plan/${planId}/api/api_get_er_historico/`)
            .then(r => r.json())
            .then(data => {
                erPanelLoaded = true;
                const cont = document.getElementById('er-historico-content');
                if (data.status !== 'success') {
                    cont.innerHTML = `<div class="alert alert-warning">${data.msg || 'Error cargando E.R. histórico.'}</div>`;
                    return;
                }
                document.getElementById('er-hist-year-badge').innerText = `Año Base: ${data.base_year}`;
                let html = '<div class="row">';

                html += '<div class="col-md-6"><table class="table table-sm table-bordered mb-2" style="font-size:0.82rem;">';
                html += '<thead class="bg-success text-white"><tr><th>Grupo Ingreso</th><th class="text-right">Total Anual</th></tr></thead><tbody>';
                data.income_groups.forEach(g => {
                    html += `<tr><td>${g.group_code} - ${g.group_name}</td><td class="text-right text-monospace">${fmt(g.total)}</td></tr>`;
                });
                html += `</tbody><tfoot class="font-weight-bold bg-light"><tr><td>TOTAL INGRESOS</td><td class="text-right text-monospace text-success">${fmt(data.totals.total_ingresos)}</td></tr></tfoot></table></div>`;

                html += '<div class="col-md-6"><table class="table table-sm table-bordered mb-2" style="font-size:0.82rem;">';
                html += '<thead class="bg-danger text-white"><tr><th>Grupo Gasto</th><th class="text-right">Total Anual</th></tr></thead><tbody>';
                data.expense_groups.forEach(g => {
                    html += `<tr><td>${g.group_code} - ${g.group_name}</td><td class="text-right text-monospace">${fmt(g.total)}</td></tr>`;
                });
                html += `</tbody><tfoot class="font-weight-bold bg-light"><tr><td>TOTAL GASTOS</td><td class="text-right text-monospace text-danger">${fmt(data.totals.total_gastos)}</td></tr></tfoot></table></div>`;

                html += '</div>';
                const utilColor = data.totals.utilidad_neta >= 0 ? 'text-success' : 'text-danger';
                html += `<div class="alert alert-light border py-2 text-right font-weight-bold ${utilColor}" style="font-size:0.9rem;">
                    UTILIDAD NETA HISTÓRICA: <span class="ml-2">${fmt(data.totals.utilidad_neta)}</span>
                </div>`;
                cont.innerHTML = html;
            })
            .catch(() => {
                document.getElementById('er-historico-content').innerHTML =
                    '<div class="alert alert-danger">Error de conexión al cargar E.R. histórico.</div>';
            });
    }

    function gatherTableData() {
        const rows = document.querySelectorAll('#budget-table-body tr[data-item-id]');
        return Array.from(rows).map(tr => {
            const monthlyVals = Array.from(tr.querySelectorAll('.month-input')).map(el => getMonthVal(el));
            const calcSelect = tr.querySelector('.calc-type-select');
            const srcSelect = tr.querySelector('.source-select');
            return {
                item_id: tr.dataset.itemId,
                calc_type: calcSelect ? calcSelect.value : tr.dataset.calcType,
                source_trend_variable: srcSelect ? srcSelect.value : '',
                account_prefix: tr.dataset.accountPrefix || '',
                monthly_values: monthlyVals,
                y1_total: monthlyVals.reduce((a, b) => a + b, 0),
                y2_total: getYearVal(tr.querySelector('.y2-input')),
                y3_total: getYearVal(tr.querySelector('.y3-input')),
            };
        });
    }

    window.saveBudgetVersion = function() {
        const scenario = document.getElementById('budget-scenario').value;
        Swal.fire({title: 'Guardando...', allowOutsideClick: false, didOpen: () => Swal.showLoading()});
        fetch(`/planificacion-financiera/plan/${planId}/api/api_save_budget_version/`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json', 'X-CSRFToken': csrfToken},
            body: JSON.stringify({scenario, lines: gatherTableData()})
        })
        .then(r => r.json())
        .then(data => {
            if (data.status === 'success') {
                Swal.fire({toast: true, position: 'top-end', icon: 'success', title: 'Guardado', showConfirmButton: false, timer: 2000});
                loadBudgetData();
            } else {
                Swal.fire('Error', data.message, 'error');
            }
        });
    };

    window.approveBudgetVersion = function() {
        const scenario = document.getElementById('budget-scenario').value;
        Swal.fire({
            title: 'Aprobar Presupuesto',
            text: 'Una vez aprobado, no podrá ser editado. ¿Continuar?',
            icon: 'warning', showCancelButton: true,
            confirmButtonColor: '#28a745', confirmButtonText: 'Sí, Aprobar'
        }).then(res => {
            if (!res.isConfirmed) return;
            fetch(`/planificacion-financiera/plan/${planId}/api/api_save_budget_version/`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json', 'X-CSRFToken': csrfToken},
                body: JSON.stringify({scenario, lines: gatherTableData()})
            }).then(r => r.json()).then(d => {
                if (d.status !== 'success') { Swal.fire('Error', d.message, 'error'); return; }
                let fd = new FormData();
                fd.append('scenario', scenario);
                fd.append('csrfmiddlewaretoken', csrfToken);
                fetch(`/planificacion-financiera/plan/${planId}/api/api_approve_budget_version/`, {method: 'POST', body: fd})
                    .then(r => r.json())
                    .then(d2 => {
                        if (d2.status === 'success') { Swal.fire('Aprobado', 'Presupuesto aprobado.', 'success').then(() => loadBudgetData()); }
                        else { Swal.fire('Error', d2.message, 'error'); }
                    });
            });
        });
    };

    // Init
    document.addEventListener('DOMContentLoaded', function() {
        if (!window.budgetScriptInitialized) {
            window.budgetScriptInitialized = true;
            setTimeout(loadBudgetData, 400);
        }
    });
})();
</script>
