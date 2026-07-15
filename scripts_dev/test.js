
                        document.addEventListener('DOMContentLoaded', function() {
                            const MONTH_NAMES = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'];
                            const historicalDataJson = '{{ historical_data_json|escapejs }}';
                            let histSavedPeriods = [];
                            let histBalanceData = null;
                            let histMode = 'accum';

                            function histGetLevelClass(level){if(level<=1)return'1';if(level===2)return'2';if(level<=4)return'3';if(level<=6)return'4';if(level<=8)return'5';if(level<=10)return'6';return'7';}
                            function histFmtAmt(amount){const rounded=Math.round(amount);if(rounded===0){return amount===0?'<span class="zero-amount" style="color:#adb5bd;">-</span>':'<span>0</span>';}const formatted=Math.abs(rounded).toLocaleString('en-US',{minimumFractionDigits:0,maximumFractionDigits:0});if(rounded<0)return`<span class="negative-amount" style="color:#dc3545;">(${formatted})</span>`;return`<span>${formatted}</span>`;}

                            // Parse saved periods
                            try {
                                const parsed = JSON.parse(historicalDataJson);
                                if (parsed && parsed.selected_periods && parsed.selected_periods.length > 0) {
                                    histSavedPeriods = parsed.selected_periods;
                                }
                            } catch(e) { console.error("Error parsing historical_data", e); }

                            if (!histSavedPeriods.length) {
                                document.getElementById('no-historical-warning').style.display = 'block';
                                document.getElementById('hist-content-wrapper').style.display = 'none';
                                return;
                            }

                            document.getElementById('no-historical-warning').style.display = 'none';
                            document.getElementById('hist-content-wrapper').style.display = 'block';

                            // Render period badges
                            const badgesHtml = histSavedPeriods.map(p => {
                                const [y,m] = p.split('-');
                                return `<span class="badge badge-primary mr-1 mb-1" style="font-size:0.78rem;border-radius:20px;padding:4px 10px;">${MONTH_NAMES[parseInt(m)-1]}-${y}</span>`;
                            }).join('');
                            document.getElementById('hist-period-badges').innerHTML = badgesHtml;

                            // Fetch from API
                            histFetchData();

                            function histFetchData() {
                                $.ajax({
                                    url: "{% url 'financial_planning:api_trial_balance_data' %}",
                                    data: { periods: JSON.stringify(histSavedPeriods), currency: 'MN' },
                                    success: function(resp) {
                                        if (resp.status === 'success') {
                                            histBalanceData = resp;
                                            histRenderAll();
                                        } else {
                                            $('#hist-bs-body').html('<tr><td colspan="99" class="text-center p-4 text-danger">Error: '+resp.msg+'</td></tr>');
                                        }
                                    },
                                    error: function() {
                                        $('#hist-bs-body').html('<tr><td colspan="99" class="text-center p-4 text-danger">Error de conexión.</td></tr>');
                                    }
                                });
                            }

                            window.histSetMode = function(mode) {
                                histMode = mode;
                                document.getElementById('hist-toggleAccum').style.background = mode==='accum'?'#fff':'none';
                                document.getElementById('hist-toggleAccum').style.boxShadow = mode==='accum'?'0 2px 6px rgba(0,0,0,0.1)':'none';
                                document.getElementById('hist-toggleAccum').style.color = mode==='accum'?'#212529':'#6c757d';
                                document.getElementById('hist-toggleMonth').style.background = mode==='month'?'#fff':'none';
                                document.getElementById('hist-toggleMonth').style.boxShadow = mode==='month'?'0 2px 6px rgba(0,0,0,0.1)':'none';
                                document.getElementById('hist-toggleMonth').style.color = mode==='month'?'#212529':'#6c757d';
                                histRenderAll();
                            };

                            function histRenderAll() {
                                if (!histBalanceData) return;
                                const periods = histBalanceData.periods;
                                const numCols = periods.length;
                                const colW = numCols<=3?120:numCols<=6?100:numCols<=12?88:80;
                                const pHeaders = periods.map(p=>{const[y,m]=p.split('-');return`<th style="min-width:${colW}px;width:${colW}px;text-align:right;">${MONTH_NAMES[parseInt(m)-1]}-${y}</th>`;}).join('');
                                const theadHtml = `<tr><th style="width:90px;min-width:90px;text-align:left;">Código</th><th class="col-desc" style="width:260px;min-width:260px;text-align:left;">Descripción</th>${pHeaders}</tr>`;
                                
                                $('#hist-bs-thead').html(theadHtml);
                                $('#hist-is-thead').html(theadHtml);
                                $('#hist-mis-thead').html(theadHtml);

                                $('#hist-bs-body').html(histBuildRows(histBalanceData.balance_sheet, periods, 'bs') || '<tr><td colspan="99" class="text-center text-muted p-4">Sin datos.</td></tr>');
                                $('#hist-is-body').html(histBuildRows(histBalanceData.income_statement, periods, 'bis') || '<tr><td colspan="99" class="text-center text-muted p-4">Sin datos.</td></tr>');
                                $('#hist-mis-body').html(histBuildRows(histBalanceData.income_statement, periods, 'bmis') || '<tr><td colspan="99" class="text-center text-muted p-4">Sin datos.</td></tr>');

                                if (histBalanceData.totals) histRenderSummary(histBalanceData.totals, periods);
                            }

                            function histBuildRows(items, periods, prefix) {
                                let html = '';
                                items.forEach(item => {
                                    const hasChildren = item.children_codes && item.children_codes.length > 0;
                                    const lvl = histGetLevelClass(item.level);
                                    const isRoot = !item.parent_code;
                                    const bDict = (prefix==='bmis') ? item.monthly_balances : item.balances;
                                    const cells = periods.map(p => {
                                        const val = (bDict && bDict[p]!=null) ? bDict[p] : 0;
                                        return `<td class="text-right text-monospace">${histFmtAmt(val)}</td>`;
                                    }).join('');
                                    html += `<tr class="accounting-row level-${lvl} ${hasChildren?'':'level-leaf'} node-collapsed" style="${isRoot?'':'display:none;'}" data-code="${item.code}" data-parent="${item.parent_code||''}" data-prefix="${prefix}" data-depth="${item.depth}" id="${prefix}-row-${item.code}" onclick="histToggleRow('${item.code}','${prefix}')">
                                        <td style="padding-left:${item.depth*14}px;">${hasChildren?'<span class="node-expander"><i class="fas fa-chevron-down"></i></span>':'<span style="display:inline-block;width:26px;"></span>'}<span class="badge badge-light border text-monospace text-dark">${item.code}</span></td>
                                        <td class="col-desc">${item.name}${item.has_discrepancy?'<i class="fas fa-exclamation-triangle text-warning ml-1" title="Discrepancia"></i>':''}</td>
                                        ${cells}</tr>`;
                                });
                                return html;
                            }

                            function histRenderSummary(totals, periods) {
                                const numCols=periods.length;const colW=numCols<=3?120:numCols<=6?100:numCols<=12?88:80;
                                const fmt=v=>histFmtAmt(v);
                                const mn=name=>`<th class="text-left font-weight-bold" style="width:350px;min-width:350px;white-space:nowrap">${name}</th>`;
                                const pH=p=>{const[y,m]=p.split('-');return`<th class="text-right" style="min-width:${colW}px;width:${colW}px;">${MONTH_NAMES[parseInt(m)-1]}-${y}</th>`;};
                                const theadRow=`<tr>${mn('Concepto')}${periods.map(pH).join('')}</tr>`;

                                // Balance General
                                const bsRows=[{label:'Total Activos (1)',key:'total_activo',cls:'text-primary'},{label:'Total Pasivos (2)',key:'total_pasivo',cls:'text-danger'},{label:'Total Patrimonio (3)',key:'total_patrimonio',cls:'text-info'},{label:'Pasivo + Patrimonio',key:'total_pasivo_patrimonio',cls:'font-weight-bold text-dark'},{label:'Diferencia',key:'diferencia',cls:'font-italic text-secondary'}];
                                let bsTbody=bsRows.map(row=>{const cells=periods.map(p=>{const val=totals[p]?totals[p][row.key]:0;return`<td class="text-right ${row.cls}">${fmt(val)}</td>`;}).join('');return`<tr><td class="font-weight-bold" style="white-space:nowrap">${row.label}</td>${cells}</tr>`;}).join('');
                                $('#hist-sum-bs-thead').html(theadRow);$('#hist-sum-bs-tbody').html(bsTbody);

                                // Estado de Resultados (Acumulado)
                                const isRows=[{label:'Total Ingresos (5)',key:'total_ingresos',cls:'text-success'},{label:'Total Gastos (4)',key:'total_gastos',cls:'text-danger'},{label:'Utilidad / Pérdida Neta',key:'utilidad_neta',cls:'table-warning font-weight-bold'}];
                                let isTbody=isRows.map(row=>{const cells=periods.map(p=>{const val=totals[p]?totals[p][row.key]:0;return`<td class="text-right ${row.cls}">${fmt(val)}</td>`;}).join('');return`<tr class="${row.cls.includes('table')?row.cls:''}"><td class="font-weight-bold" style="white-space:nowrap">${row.label}</td>${cells}</tr>`;}).join('');
                                $('#hist-sum-is-thead').html(theadRow);$('#hist-sum-is-tbody').html(isTbody);

                                // Estado de Resultados (Mensual)
                                const misRows=[{label:'Total Ingresos (5)',key:'total_ingresos_monthly',cls:'text-success'},{label:'Total Gastos (4)',key:'total_gastos_monthly',cls:'text-danger'},{label:'Utilidad / Pérdida Neta',key:'utilidad_neta_monthly',cls:'table-warning font-weight-bold'}];
                                let misTbody=misRows.map(row=>{const cells=periods.map(p=>{const val=totals[p]?totals[p][row.key]:0;return`<td class="text-right ${row.cls}">${fmt(val)}</td>`;}).join('');return`<tr class="${row.cls.includes('table')?row.cls:''}"><td class="font-weight-bold" style="white-space:nowrap">${row.label}</td>${cells}</tr>`;}).join('');
                                $('#hist-sum-mis-thead').html(theadRow);$('#hist-sum-mis-tbody').html(misTbody);

                                // Update cuadratura badge
                                const allSquared=periods.every(p=>totals[p]&&totals[p].es_cuadrado);
                                if(allSquared){$('#hist-squareBadge').removeClass('badge-danger').addClass('badge-success').html('<i class="fas fa-check-circle mr-1"></i>Balance Cuadrado');}
                                else{$('#hist-squareBadge').removeClass('badge-success').addClass('badge-danger').html('<i class="fas fa-exclamation-triangle mr-1"></i>Descuadrado');}
                            }

                            // Tree interaction
                            window.histToggleRow = function(code, prefix) {
                                const row = $(`#${prefix}-row-${code}`);
                                if (row.hasClass('node-collapsed')) { row.removeClass('node-collapsed'); histShowChildren(code, prefix); }
                                else { row.addClass('node-collapsed'); histHideChildren(code, prefix); }
                            };
                            function histShowChildren(pc, prefix) {
                                $(`tr[data-parent="${pc}"][data-prefix="${prefix}"]`).each(function(){const r=$(this);r.show();if(!r.hasClass('node-collapsed'))histShowChildren(r.data('code'),prefix);});
                            }
                            function histHideChildren(pc, prefix) {
                                $(`tr[data-parent="${pc}"][data-prefix="${prefix}"]`).each(function(){$(this).hide();histHideChildren($(this).data('code'),prefix);});
                            }
                            window.histExpandAll = function() { $('#hist-content-wrapper .accounting-row').removeClass('node-collapsed').show(); };
                            window.histCollapseAll = function() {
                                $('#hist-content-wrapper .accounting-row').each(function(){const r=$(this);r.data('parent')!==''?r.hide():r.show();r.addClass('node-collapsed');});
                            };
                            let filterTimer;
                            window.histFilterAccounts = function() {
                                clearTimeout(filterTimer);
                                filterTimer = setTimeout(function() {
                                    const q=$('#hist-accountSearch').val().toLowerCase().trim();
                                    if(!q){histCollapseAll();return;}
                                    $('#hist-content-wrapper .accounting-row').each(function(){const r=$(this);const code=r.data('code').toString();const name=r.find('td:nth-child(2)').text().toLowerCase();const prefix=r.data('prefix');if(code.includes(q)||name.includes(q)){r.show();histRevealParents(r.data('parent'),prefix);}else{r.hide();}});
                                }, 300);
                            };
                            function histRevealParents(pc, prefix) {
                                if(!pc)return;const p=$(`#${prefix}-row-${pc}`);p.removeClass('node-collapsed').show();histRevealParents(p.data('parent'),prefix);
                            }
                        });
                        

                    document.addEventListener('DOMContentLoaded', function() {
                        const loadingDatesSpan = document.getElementById('portfolio-dates-loading');
                        const thead = document.getElementById('portfolio-history-thead');
                        const tbody = document.getElementById('portfolio-history-tbody');
                        const planId = '{{ plan.id }}';

                        const MONTH_NAMES = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'];
                        let portAllPeriods = [];
                        let savedPortPeriods = {{ plan.historical_data.portfolio_periods|safe|default:"null" }};
                        let portSelectedPeriods = [];

                        // 1. Fetch available dates
                        fetch("{% url 'financial_planning:api_available_portfolio_dates' %}")
                            .then(r => r.json())
                            .then(data => {
                                loadingDatesSpan.style.display = 'none';
                                if(data.status === 'success' && data.data && data.data.length > 0) {
                                    portAllPeriods = data.data.map(d => d.value || d).sort().reverse();
                                    
                                    if (savedPortPeriods && savedPortPeriods.length > 0) {
                                        portSelectedPeriods = savedPortPeriods;
                                    } else {
                                        // Select top 3 by default
                                        portSelectedPeriods = portAllPeriods.slice(0, 3);
                                    }
                                    
                                    document.getElementById('port-period-selector-wrapper').style.display = 'block';
                                    buildPortSelectorUI();
                                    updatePortSummaryBadges();
                                    loadHistoricalPortfolio();
                                } else {
                                    thead.innerHTML = `<tr><th class="p-3 text-warning">No se encontraron cierres de cartera en el sistema.</th></tr>`;
                                }
                            })
                            .catch(err => {
                                loadingDatesSpan.style.display = 'none';
                                thead.innerHTML = `<tr><th class="p-3 text-danger">Error de conexión al obtener periodos.</th></tr>`;
                            });

                        window.togglePortSelector = function() {
                            const activeDiv = document.getElementById('port-period-selector-active');
                            const btn = document.getElementById('toggle-port-period-selector-btn');
                            if (activeDiv.style.display === 'none') {
                                activeDiv.style.display = 'block';
                                btn.innerHTML = '<i class="fas fa-times mr-1"></i> Ocultar Edición';
                                
                                // Sync checkboxes
                                document.querySelectorAll('.port-period-cb').forEach(cb => {
                                    cb.checked = portSelectedPeriods.includes(cb.value);
                                });
                            } else {
                                activeDiv.style.display = 'none';
                                btn.innerHTML = '<i class="fas fa-edit mr-1"></i> Modificar Períodos';
                            }
                        };
                        
                        window.buildPortSelectorUI = function() {
                            const byYear = {};
                            portAllPeriods.forEach(p => {
                                const [y, m] = p.split('-');
                                if (!byYear[y]) byYear[y] = [];
                                byYear[y].push({ period: p, month: parseInt(m) });
                            });

                            const container = document.getElementById('port-period-selector-container');
                            container.innerHTML = '';

                            Object.keys(byYear).sort().reverse().forEach(year => {
                                const months = byYear[year];
                                const yearDiv = document.createElement('div');
                                yearDiv.className = 'mb-3 pb-2 border-bottom';

                                const monthChecks = months.map(({ period, month }) => `
                                    <div class="custom-control custom-checkbox custom-control-inline mb-1 mr-3">
                                        <input type="checkbox" class="custom-control-input port-period-cb"
                                            id="port-pcb-${period}" value="${period}">
                                        <label class="custom-control-label small text-secondary" for="port-pcb-${period}">
                                            ${MONTH_NAMES[month - 1]}
                                        </label>
                                    </div>`).join('');

                                yearDiv.innerHTML = `
                                    <div class="d-flex justify-content-between align-items-center mb-2">
                                        <strong class="text-primary" style="font-size:0.9rem;">
                                            <i class="fas fa-calendar-check mr-1 text-success"></i> AÑO ${year}
                                        </strong>
                                        <div>
                                            <button class="btn btn-xs btn-outline-success mr-1 bg-white" onclick="portYearAction('${year}','all')">
                                                <i class="fas fa-check-square mr-1"></i>Todo
                                            </button>
                                            <button class="btn btn-xs btn-outline-secondary bg-white" onclick="portYearAction('${year}','none')">
                                                <i class="fas fa-square mr-1"></i>Limpiar
                                            </button>
                                        </div>
                                    </div>
                                    <div class="d-flex flex-wrap">${monthChecks}</div>`;
                                container.appendChild(yearDiv);
                            });
                        };
                        
                        window.portYearAction = function(year, action) {
                            document.querySelectorAll('.port-period-cb').forEach(cb => {
                                if (cb.value.startsWith(year + '-')) cb.checked = (action === 'all');
                            });
                        };
                        
                        window.updatePortSummaryBadges = function() {
                            const badges = portSelectedPeriods.map(p => {
                                const [y, m] = p.split('-');
                                return `<span class="badge badge-success mr-1 mb-1" style="font-size:0.78rem;">${MONTH_NAMES[parseInt(m)-1]}-${y}</span>`;
                            }).join('');
                            document.getElementById('port-period-summary-badges').innerHTML = badges || '<span class="text-muted small">Ninguno</span>';
                        };
                        
                        window.confirmPortSelection = function() {
                            const checked = Array.from(document.querySelectorAll('.port-period-cb:checked'))
                                                 .map(cb => cb.value).sort();
                            if (checked.length === 0) {
                                toastr.warning('Seleccione al menos un período.');
                                return;
                            }
                            portSelectedPeriods = checked;
                            togglePortSelector(); // close
                            updatePortSummaryBadges();
                            loadHistoricalPortfolio();
                            
                            {% if plan %}
                            // Save to backend
                            fetch("{% url 'financial_planning:api_save_step_periods' plan.id %}", {
                                method: "POST",
                                headers: {
                                    "Content-Type": "application/json",
                                    "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]') ? document.querySelector('[name=csrfmiddlewaretoken]').value : ''
                                },
                                body: JSON.stringify({ step: '3', periods: portSelectedPeriods })
                            })
                            .then(res => res.json())
                            .then(data => {
                                if (data.status !== 'success') {
                                    console.error('Error saving portfolio periods:', data.msg);
                                }
                            });
                            {% endif %}
                        };

                        // 2. Load Portfolio Data
                        window.loadHistoricalPortfolio = function() {
                            const btn = document.getElementById('btn-load-portfolio');
                            if(btn) btn.innerHTML = '<i class="fas fa-spinner fa-spin mr-1"></i> Cargando...';
                            
                            const selectedDates = portSelectedPeriods.join(',');
                            
                            fetch("{% url 'financial_planning:api_historical_portfolio_data' %}?plan_id=" + planId + "&dates=" + selectedDates)
                                .then(r => r.json())
                                .then(data => {
                                    if(btn) btn.innerHTML = '<i class="fas fa-sync-alt mr-1"></i> Refrescar';
                                    if(data.status === 'success') {
                                        renderPortfolioTable(data.data);
                                    } else {
                                        tbody.innerHTML = `<tr><td colspan="99" class="text-center text-danger p-3">Error: ${data.msg}</td></tr>`;
                                    }
                                })
                                .catch(err => {
                                    if(btn) btn.innerHTML = '<i class="fas fa-sync-alt mr-1"></i> Refrescar';
                                    tbody.innerHTML = `<tr><td colspan="99" class="text-center text-danger p-3">Error de red al cargar datos.</td></tr>`;
                                });
                        };

                        function renderPortfolioTable(backendData) {
                            if (!backendData || Object.keys(backendData).length === 0) {
                                tbody.innerHTML = `<tr><td colspan="99" class="text-center text-muted p-3">No hay datos históricos.</td></tr>`;
                                return;
                            }

                            const types = ['G.EMP.', 'M.EMP.', 'P.EMP.', 'MI.EMP.', 'CONS', 'TOTAL'];
                            
                            // Header
                            thead.innerHTML = `
                                <tr>
                                    <th rowspan="2" class="portfolio-col-text">Agencia</th>
                                    <th rowspan="2" class="portfolio-col-text text-center">Mes</th>
                                    <th rowspan="2" class="text-center">Asesores</th>
                                    <th colspan="6" class="text-center bg-light">Desembolsos (Nro)</th>
                                    <th colspan="6" class="text-center bg-light">Desembolsos (Monto)</th>
                                    <th colspan="6" class="text-center bg-light">Cartera (Nro)</th>
                                    <th colspan="6" class="text-center bg-light">Cartera (Saldo)</th>
                                    <th rowspan="2" class="text-center text-danger">Cartera Vcda. (Monto)</th>
                                </tr>
                                <tr>
                                    ${Array(4).fill(types.map(t => `<th class="text-center">${t}</th>`).join('')).join('')}
                                </tr>
                            `;

                            let html = '';
                            const agencies = Object.keys(backendData).sort((a,b) => a === 'ACUMULADO' ? -1 : (b === 'ACUMULADO' ? 1 : a.localeCompare(b)));
                            
                            agencies.forEach(agName => {
                                const periods = backendData[agName];
                                if(!periods || periods.length === 0) return;
                                
                                periods.forEach((p, pIdx) => {
                                    html += `<tr>`;
                                    if (pIdx === 0) {
                                        html += `<td rowspan="${periods.length}" class="font-weight-bold portfolio-col-text bg-white" style="vertical-align: middle; position: sticky; left: 0; z-index: 1;">${agName}</td>`;
                                    }
                                    html += `<td class="portfolio-col-text text-secondary text-center">${p.period}</td>`;
                                    html += `<td class="text-monospace text-center">${p.advisors || 0}</td>`;
                                    
                                    // Calculate totals
                                    let tot_nro_des = 0, tot_mto_des = 0, tot_nro_car = 0, tot_sld_car = 0;
                                    const prods = ['G.EMP.', 'M.EMP.', 'P.EMP.', 'MI.EMP.', 'CONS'];
                                    
                                    // Nro Desembolsos
                                    prods.forEach(t => {
                                        const val = p.types[t] ? p.types[t].nro_des : 0;
                                        tot_nro_des += val;
                                        html += `<td class="text-monospace text-right">${formatNum(val, 0)}</td>`;
                                    });
                                    html += `<td class="text-monospace text-right font-weight-bold bg-light">${formatNum(tot_nro_des, 0)}</td>`;
                                    
                                    // Monto Desembolsos
                                    prods.forEach(t => {
                                        const val = p.types[t] ? p.types[t].monto_des : 0;
                                        tot_mto_des += val;
                                        html += `<td class="text-monospace text-right">${formatNum(val)}</td>`;
                                    });
                                    html += `<td class="text-monospace text-right font-weight-bold bg-light">${formatNum(tot_mto_des)}</td>`;

                                    // Nro Cartera
                                    prods.forEach(t => {
                                        const val = p.types[t] ? p.types[t].nro_cart : 0;
                                        tot_nro_car += val;
                                        html += `<td class="text-monospace text-right">${formatNum(val, 0)}</td>`;
                                    });
                                    html += `<td class="text-monospace text-right font-weight-bold bg-light">${formatNum(tot_nro_car, 0)}</td>`;

                                    // Saldo Cartera
                                    prods.forEach(t => {
                                        const val = p.types[t] ? p.types[t].saldo_cart : 0;
                                        tot_sld_car += val;
                                        html += `<td class="text-monospace text-right">${formatNum(val)}</td>`;
                                    });
                                    html += `<td class="text-monospace text-right font-weight-bold bg-light">${formatNum(tot_sld_car)}</td>`;

                                    // Mora
                                    html += `<td class="text-monospace text-right text-danger font-weight-bold bg-light">${formatNum(p.vcda)}</td>`;
                                    
                                    html += `</tr>`;
                                });
                            });

                            tbody.innerHTML = html;
                        }

                        function formatNum(val, decimals=2) {
                            if (!val || val === 0) return '<span class="text-muted">-</span>';
                            return val.toLocaleString('en-US', {minimumFractionDigits: decimals, maximumFractionDigits: decimals});
                        }
                    });
                

                    document.addEventListener('DOMContentLoaded', function() {
                        const loadingDatesSpan = document.getElementById('passive-dates-loading');
                        const thead = document.getElementById('passive-history-thead');
                        const tbody = document.getElementById('passive-history-tbody');
                        const planId = '{{ plan.id }}';
                        
                        let passAllPeriods = [];
                        let savedPassPeriods = {{ plan.historical_data.passive_periods|safe|default:"null" }};
                        let passSelectedPeriods = [];

                        // 1. Fetch available dates
                        fetch("{% url 'financial_planning:api_available_passive_dates' %}")
                            .then(r => r.json())
                            .then(data => {
                                loadingDatesSpan.style.display = 'none';
                                if(data.status === 'success' && data.data && data.data.length > 0) {
                                    passAllPeriods = data.data.map(d => d.value || d).sort().reverse();
                                    
                                    if (savedPassPeriods && savedPassPeriods.length > 0) {
                                        passSelectedPeriods = savedPassPeriods;
                                    } else {
                                        // Select top 3 by default
                                        passSelectedPeriods = passAllPeriods.slice(0, 3);
                                    }
                                    
                                    document.getElementById('pass-period-selector-wrapper').style.display = 'block';
                                    buildPassSelectorUI();
                                    updatePassSummaryBadges();
                                    loadHistoricalPassive();
                                } else {
                                    thead.innerHTML = `<tr><th class="p-3 text-warning">No se encontraron datos de pasivos en el sistema.</th></tr>`;
                                }
                            })
                            .catch(err => {
                                loadingDatesSpan.style.display = 'none';
                                thead.innerHTML = `<tr><th class="p-3 text-danger">Error de conexión al obtener periodos.</th></tr>`;
                            });

                        window.togglePassSelector = function() {
                            const activeDiv = document.getElementById('pass-period-selector-active');
                            const btn = document.getElementById('toggle-pass-period-selector-btn');
                            if (activeDiv.style.display === 'none') {
                                activeDiv.style.display = 'block';
                                btn.innerHTML = '<i class="fas fa-times mr-1"></i> Ocultar Edición';
                                
                                // Sync checkboxes
                                document.querySelectorAll('.pass-period-cb').forEach(cb => {
                                    cb.checked = passSelectedPeriods.includes(cb.value);
                                });
                            } else {
                                activeDiv.style.display = 'none';
                                btn.innerHTML = '<i class="fas fa-edit mr-1"></i> Modificar Períodos';
                            }
                        };
                        
                        window.buildPassSelectorUI = function() {
                            const byYear = {};
                            const MONTH_NAMES = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'];
                            passAllPeriods.forEach(p => {
                                const [y, m] = p.split('-');
                                if (!byYear[y]) byYear[y] = [];
                                byYear[y].push({ period: p, month: parseInt(m) });
                            });

                            const container = document.getElementById('pass-period-selector-container');
                            container.innerHTML = '';

                            Object.keys(byYear).sort().reverse().forEach(year => {
                                const months = byYear[year];
                                const yearDiv = document.createElement('div');
                                yearDiv.className = 'mb-3 pb-2 border-bottom';

                                const monthChecks = months.map(({ period, month }) => `
                                    <div class="custom-control custom-checkbox custom-control-inline mb-1 mr-3">
                                        <input type="checkbox" class="custom-control-input pass-period-cb"
                                            id="pass-pcb-${period}" value="${period}">
                                        <label class="custom-control-label small text-secondary" for="pass-pcb-${period}">
                                            ${MONTH_NAMES[month - 1]}
                                        </label>
                                    </div>`).join('');

                                yearDiv.innerHTML = `
                                    <div class="d-flex justify-content-between align-items-center mb-2">
                                        <strong class="text-info" style="font-size:0.9rem;">
                                            <i class="fas fa-calendar-check mr-1 text-info"></i> AÑO ${year}
                                        </strong>
                                        <div>
                                            <button class="btn btn-xs btn-outline-info mr-1 bg-white" onclick="passYearAction('${year}','all')">
                                                <i class="fas fa-check-square mr-1"></i>Todo
                                            </button>
                                            <button class="btn btn-xs btn-outline-secondary bg-white" onclick="passYearAction('${year}','none')">
                                                <i class="fas fa-square mr-1"></i>Limpiar
                                            </button>
                                        </div>
                                    </div>
                                    <div class="d-flex flex-wrap">${monthChecks}</div>`;
                                container.appendChild(yearDiv);
                            });
                        };
                        
                        window.passYearAction = function(year, action) {
                            document.querySelectorAll('.pass-period-cb').forEach(cb => {
                                if (cb.value.startsWith(year + '-')) cb.checked = (action === 'all');
                            });
                        };
                        
                        window.updatePassSummaryBadges = function() {
                            const MONTH_NAMES = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'];
                            const badges = passSelectedPeriods.map(p => {
                                const [y, m] = p.split('-');
                                return `<span class="badge badge-info mr-1 mb-1" style="font-size:0.78rem;">${MONTH_NAMES[parseInt(m)-1]}-${y}</span>`;
                            }).join('');
                            document.getElementById('pass-period-summary-badges').innerHTML = badges || '<span class="text-muted small">Ninguno</span>';
                        };
                        
                        window.confirmPassSelection = function() {
                            const checked = Array.from(document.querySelectorAll('.pass-period-cb:checked'))
                                                 .map(cb => cb.value).sort();
                            if (checked.length === 0) {
                                toastr.warning('Seleccione al menos un período.');
                                return;
                            }
                            passSelectedPeriods = checked;
                            togglePassSelector(); // close
                            updatePassSummaryBadges();
                            loadHistoricalPassive();
                            
                            {% if plan %}
                            // Save to backend
                            fetch("{% url 'financial_planning:api_save_step_periods' plan.id %}", {
                                method: "POST",
                                headers: {
                                    "Content-Type": "application/json",
                                    "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]') ? document.querySelector('[name=csrfmiddlewaretoken]').value : ''
                                },
                                body: JSON.stringify({ step: '4', periods: passSelectedPeriods })
                            })
                            .then(res => res.json())
                            .then(data => {
                                if (data.status !== 'success') {
                                    console.error('Error saving passive periods:', data.msg);
                                }
                            });
                            {% endif %}
                        };

                        // 2. Load Passive Data
                        window.loadHistoricalPassive = function() {
                            const btn = document.getElementById('btn-load-passive');
                            if(btn) btn.innerHTML = '<i class="fas fa-spinner fa-spin mr-1"></i> Cargando...';
                            
                            const selectedDates = passSelectedPeriods.join(',');

                            fetch("{% url 'financial_planning:api_historical_passive_data' %}?plan_id=" + planId + "&dates=" + selectedDates)
                                .then(r => r.json())
                                .then(data => {
                                    if(btn) btn.innerHTML = '<i class="fas fa-sync-alt mr-1"></i> Refrescar';
                                    if(data.status === 'success') {
                                        renderPassiveTable(data.data);
                                    } else {
                                        tbody.innerHTML = `<tr><td colspan="99" class="text-center text-danger p-3">Error: ${data.msg}</td></tr>`;
                                    }
                                })
                                .catch(err => {
                                    if(btn) btn.innerHTML = '<i class="fas fa-sync-alt mr-1"></i> Refrescar';
                                    tbody.innerHTML = `<tr><td colspan="99" class="text-center text-danger p-3">Error de red al cargar datos.</td></tr>`;
                                });
                        };

                        function renderPassiveTable(backendData) {
                            if (!backendData || Object.keys(backendData).length === 0) {
                                tbody.innerHTML = `<tr><td colspan="99" class="text-center text-muted p-3">No hay datos históricos.</td></tr>`;
                                return;
                            }

                            // Format numbers
                            const fm = (val) => Number(val || 0).toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
                            const fn = (val) => Number(val || 0).toLocaleString('en-US');

                            // Build Headers
                            thead.innerHTML = `
                                <tr>
                                    <th rowspan="2" class="text-center align-middle bg-light border-bottom" style="width: 150px;">Meses</th>
                                    <th colspan="5" class="text-center bg-light border-bottom">SALDOS</th>
                                </tr>
                                <tr>
                                    <th class="text-center bg-light">Ahorros Cte<br><small class="text-muted">MONTO</small></th>
                                    <th class="text-center bg-light">Ahorros Programado<br><small class="text-muted">MONTO</small></th>
                                    <th class="text-center bg-light">CDPFijo<br><small class="text-muted">MONTO</small></th>
                                    <th class="text-center bg-light">Aportaciones<br><small class="text-muted">MONTO</small></th>
                                    <th class="text-center bg-light">Socios<br><small class="text-muted">NRO</small></th>
                                </tr>
                            `;

                            const agencies = Object.keys(backendData).sort((a,b) => a === 'ACUMULADO' ? -1 : (b === 'ACUMULADO' ? 1 : a.localeCompare(b)));
                            
                            let rowsHtml = '';
                            agencies.forEach(agName => {
                                const records = backendData[agName] || [];
                                if (records.length === 0) return;
                                
                                rowsHtml += `
                                    <tr>
                                        <td colspan="6" class="text-left font-weight-bold text-white" style="background-color: #4a5568;">
                                            <i class="fas fa-building mr-2"></i> ${agName}
                                        </td>
                                    </tr>
                                `;
                                
                                records.forEach(row => {
                                    rowsHtml += `
                                        <tr>
                                            <td class="text-center font-weight-bold" style="vertical-align: middle;">${row.period}</td>
                                            <td class="text-right text-monospace" style="vertical-align: middle;">${fm(row.ahorros_cte)}</td>
                                            <td class="text-right text-monospace" style="vertical-align: middle;">${fm(row.ahorros_prog)}</td>
                                            <td class="text-right text-monospace" style="vertical-align: middle;">${fm(row.dpf)}</td>
                                            <td class="text-right text-monospace" style="vertical-align: middle;">${fm(row.aportes)}</td>
                                            <td class="text-center font-weight-bold" style="background-color: #ffffcc; color: #000; vertical-align: middle;">${fn(row.socios)}</td>
                                        </tr>
                                    `;
                                });
                            });
                            
                            if (rowsHtml === '') {
                                tbody.innerHTML = `<tr><td colspan="99" class="text-center text-muted p-3">No hay datos históricos.</td></tr>`;
                            } else {
                                tbody.innerHTML = rowsHtml;
                            }
                        }

                        function formatNum(val, decimals=2) {
                            if (!val || val === 0) return '<span class="text-muted">-</span>';
                            return val.toLocaleString('en-US', {minimumFractionDigits: decimals, maximumFractionDigits: decimals});
                        }
                    });
                

                        function toggleProjRow(code, btn) {
                            const icon = $(btn).find('i');
                            const isExpanded = icon.hasClass('fa-chevron-down');
                            if (isExpanded) {
                                icon.removeClass('fa-chevron-down').addClass('fa-chevron-right');
                                // hide all descendants
                                $('.proj-row').each(function() {
                                    const parent = $(this).data('parent').toString();
                                    if (parent.startsWith(code) || parent === code) {
                                        $(this).hide();
                                        $(this).find('i.fa-chevron-down').removeClass('fa-chevron-down').addClass('fa-chevron-right');
                                    }
                                });
                            } else {
                                icon.removeClass('fa-chevron-right').addClass('fa-chevron-down');
                                // show direct children
                                $('.proj-row[data-parent="' + code + '"]').show();
                            }
                        }
                        

    function exportAnalysisToImage() {
        const container = document.getElementById('step6-export-area') || document.querySelector('.row.mb-4');
        if (!container) return;
        
        // Disable buttons temporarily to hide from image
        const exportBtn = document.getElementById('dropdownMenuButtonExport');
        if(exportBtn) exportBtn.style.visibility = 'hidden';

        html2canvas(container, {
            scale: 2,
            backgroundColor: '#ffffff',
            useCORS: true
        }).then(canvas => {
            if(exportBtn) exportBtn.style.visibility = 'visible';
            const link = document.createElement('a');
            link.download = `Proyeccion_Tendencias_${new Date().toISOString().slice(0,10)}.png`;
            link.href = canvas.toDataURL('image/png');
            link.click();
        });
    }

    function exportAnalysisToPDF() {
        const container = document.getElementById('step6-export-area') || document.querySelector('.row.mb-4');
        if (!container) return;

        // Disable buttons temporarily to hide from image
        const exportBtn = document.getElementById('dropdownMenuButtonExport');
        if(exportBtn) exportBtn.style.visibility = 'hidden';

        html2canvas(container, {
            scale: 2,
            backgroundColor: '#ffffff',
            useCORS: true
        }).then(canvas => {
            if(exportBtn) exportBtn.style.visibility = 'visible';
            const imgData = canvas.toDataURL('image/png');
            const { jsPDF } = window.jspdf;
            
            // Calculate dimensions to fit in A4 landscape
            const pdf = new jsPDF({
                orientation: 'landscape',
                unit: 'mm',
                format: 'a4'
            });
            
            const pdfWidth = pdf.internal.pageSize.getWidth();
            const pdfHeight = pdf.internal.pageSize.getHeight();
            const imgWidth = canvas.width;
            const imgHeight = canvas.height;
            const ratio = Math.min(pdfWidth / imgWidth, pdfHeight / imgHeight);
            
            const width = imgWidth * ratio;
            const height = imgHeight * ratio;
            
            pdf.addImage(imgData, 'PNG', 0, 0, width, height);
            pdf.save(`Proyeccion_Tendencias_${new Date().toISOString().slice(0,10)}.pdf`);
        });
    }

    document.addEventListener('DOMContentLoaded', function() {
        const projStartYearInput = document.getElementById('{{ form.projection_start_year.id_for_label }}');
        const projYearsInput = document.getElementById('{{ form.projection_years.id_for_label }}');

        function updateTables() {
            if (projStartYearInput && projYearsInput) {
                const projYearVal = projStartYearInput.value;
                const projYearsVal = parseInt(projYearsInput.value, 10);

                if (projYearVal) {
                    const projYear = parseInt(projYearVal, 10);
                    
                    document.getElementById('dyn_year_x_minus_2').textContent = projYear - 3;
                    document.getElementById('dyn_year_x_minus_1').textContent = projYear - 2;
                    document.getElementById('dyn_year_x').textContent = projYear - 1;
                    document.getElementById('dyn_proj_year').textContent = projYear;
                    
                    // Formatting proj date (Always Enero as requested)
                    document.getElementById('dyn_proj_start_date').textContent = 'Enero';
                    document.getElementById('dyn_hist_start_year').textContent = projYear - 3; // Dos años antes del ejecutado
                    document.getElementById('dyn_start_month').textContent = 'Enero';
                    document.getElementById('dyn_hist_start_date').textContent = 'Enero';
                    
                    if (!isNaN(projYearsVal) && projYearsVal > 0) {
                        let tbodyHTML = '';
                        for (let i = 0; i < projYearsVal; i++) {
                            tbodyHTML += `<tr><td class="font-weight-bold">${projYear + i}</td></tr>`;
                        }
                        document.querySelector('#dyn_proj_years_table tbody').innerHTML = tbodyHTML;
                    } else {
                        document.querySelector('#dyn_proj_years_table tbody').innerHTML = '<tr><td>-</td></tr>';
                    }
                } else {
                    document.getElementById('dyn_year_x_minus_2').textContent = '-';
                    document.getElementById('dyn_year_x_minus_1').textContent = '-';
                    document.getElementById('dyn_year_x').textContent = '-';
                    document.getElementById('dyn_proj_year').textContent = '-';
                    document.getElementById('dyn_proj_start_date').textContent = '-';
                    document.getElementById('dyn_hist_start_year').textContent = '-';
                    document.getElementById('dyn_start_month').textContent = '-';
                    document.getElementById('dyn_hist_start_date').textContent = '-';
                    document.querySelector('#dyn_proj_years_table tbody').innerHTML = '<tr><td>-</td></tr>';
                }
            }
        }

        if (projStartYearInput) projStartYearInput.addEventListener('input', updateTables);
        if (projYearsInput) projYearsInput.addEventListener('input', updateTables);

        // Initial update
        updateTables();

        // Locked Steps Logic
        const lockedStepsJsonStr = '{{ locked_steps_json|escapejs }}';
        let lockedSteps = {};
        try {
            if (lockedStepsJsonStr) {
                lockedSteps = JSON.parse(lockedStepsJsonStr);
            }
        } catch(e) { console.error('Error parsing locked steps', e); }

        window.toggleStepLock = function(step, action, extraData={}) {
            {% if plan %}
            fetch("{% url 'financial_planning:toggle_step_lock' plan.id %}", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]') ? document.querySelector('[name=csrfmiddlewaretoken]').value : ''
                },
                body: JSON.stringify({ step: step, action: action, extra_data: extraData })
            })
            .then(res => res.json())
            .then(data => {
                if (data.status === 'success') {
                    lockedSteps[step] = (action === 'lock');
                    applyLockState(step);
                    alert(data.msg);
                } else {
                    alert('Error: ' + data.msg);
                }
            })
            .catch(err => {
                console.error(err);
                alert('Error de conexión.');
            });
            {% else %}
            alert("Debe crear o guardar el plan primero.");
            {% endif %}
        };

        function applyLockState(step) {
            const isLocked = lockedSteps[step] === true;
            const btnLock = document.getElementById(`btn-lock-step${step}`);
            const btnUnlock = document.getElementById(`btn-unlock-step${step}`);

            if (btnLock && btnUnlock) {
                if (isLocked) {
                    btnLock.style.display = 'none';
                    btnUnlock.style.display = 'inline-block';
                } else {
                    btnLock.style.display = 'inline-block';
                    btnUnlock.style.display = 'none';
                }
            }

            // Specific logic per step to disable UI components
            if (step == '2') {
                const reasignarBtn = document.querySelector('a[href*="balance-comprobacion"]');
                if (reasignarBtn) {
                    if (isLocked) {
                        reasignarBtn.classList.add('disabled');
                        reasignarBtn.style.pointerEvents = 'none';
                    } else {
                        reasignarBtn.classList.remove('disabled');
                        reasignarBtn.style.pointerEvents = 'auto';
                    }
                }
            } else if (step == '3') {
                const btnLoadPortfolio = document.getElementById('btn-load-portfolio');
                if (btnLoadPortfolio) {
                    btnLoadPortfolio.disabled = isLocked;
                }
                document.querySelectorAll('.portfolio-date-checkbox').forEach(chk => {
                    chk.disabled = isLocked;
                });
            } else if (step == '4') {
                const btnLoadPassive = document.getElementById('btn-load-passive');
                if (btnLoadPassive) {
                    btnLoadPassive.disabled = isLocked;
                }
                document.querySelectorAll('.passive-date-checkbox').forEach(chk => {
                    chk.disabled = isLocked;
                });
            }
            // Add other steps as needed
        }

        // Apply lock states on load
        Object.keys(lockedSteps).forEach(step => {
            if (lockedSteps[step]) applyLockState(step);
        });

        // ---------------------------------------------------------------------
        // STEP 6: Análisis de Tendencias Logic
        // ---------------------------------------------------------------------
        {% if step == 6 %}
        let trendChartInstance = null;
        let trendDatasetsByAgency = null;
        let trendLabels = null;
        let histMonthsCount = 12;
        let currentAgency = null;
        let currentVariable = null;
        let currentPeriod = 12;
        let chartMode = 'tendencia';
        let showTrendCols = false;
        let showMCCols = false;
        let mcDataObj = null;

        window.exportAnalysisToExcel = function() {
            if (!currentAgency || !trendDatasetsByAgency || !trendDatasetsByAgency[currentAgency]) {
                Swal.fire('Error', 'No hay datos cargados para exportar.', 'error');
                return;
            }
            
            const vars = trendDatasetsByAgency[currentAgency].variables;
            if (!vars || vars.length === 0) return;
            
            const wb = XLSX.utils.book_new();
            
            // Hoja 1: Ajustes de Escenarios
            const wsAjustesData = [
                ['VARIABLE', 'TENDENCIA (%)', 'PESIMISTA (%)', 'BASE (%)', 'OPTIMISTA (%)']
            ];
            vars.forEach(v => {
                const trend = (v.rates && v.rates.trend) ? parseFloat(v.rates.trend).toFixed(2) : '0.00';
                const pes = (v.rates && v.rates.pesimista) ? parseFloat(v.rates.pesimista).toFixed(2) : '0.00';
                const base = (v.rates && v.rates.base) ? parseFloat(v.rates.base).toFixed(2) : '0.00';
                const opt = (v.rates && v.rates.optimista) ? parseFloat(v.rates.optimista).toFixed(2) : '0.00';
                wsAjustesData.push([v.name, trend, pes, base, opt]);
            });
            const wsAjustes = XLSX.utils.aoa_to_sheet(wsAjustesData);
            XLSX.utils.book_append_sheet(wb, wsAjustes, 'Ajustes de Escenarios');
            
            // Hoja para cada variable (Proyecciones)
            vars.forEach(v => {
                const wsData = [
                    ['Mes', 'Pesimista', 'Base', 'Optimista', 'Tendencia']
                ];
                
                const hasMC = (showMCCols && mcDataObj && Object.keys(mcDataObj).length > 0 && currentVariable === v.id);
                if (hasMC) {
                    wsData[0].push('MC Pesimista', 'MC Base', 'MC Optimista');
                }
                
                const numRows = Math.min(currentPeriod, v.base.length - 1);
                const startIdx = 1;
                for (let i = 0; i < numRows; i++) {
                    const idx = startIdx + i;
                    const lbl = trendLabels ? trendLabels[histMonthsCount + i] || `Mes ${i+1}` : `Mes ${i+1}`;
                    
                    const rowData = [
                        lbl,
                        v.pesimista[idx],
                        v.base[idx],
                        v.optimista[idx],
                        v.trend[idx]
                    ];
                    
                    if (hasMC) {
                        rowData.push(
                            mcDataObj.pesimista[i],
                            mcDataObj.base[i],
                            mcDataObj.optimista[i]
                        );
                    }
                    wsData.push(rowData);
                }
                
                const wsVar = XLSX.utils.aoa_to_sheet(wsData);
                const safeName = v.name.replace(/[:\\/?*\[\]]/g, '').substring(0, 31);
                XLSX.utils.book_append_sheet(wb, wsVar, safeName);
            });
            
            XLSX.writeFile(wb, `Proyecciones_${currentAgency}_${new Date().toISOString().slice(0,10)}.xlsx`);
        };

        function renderTrendChart(agencyId, variableId) {
            if (!trendDatasetsByAgency || !trendDatasetsByAgency[agencyId]) return;

            const agencyData = trendDatasetsByAgency[agencyId].variables;
            const dataObj = agencyData.find(d => d.id === variableId);
            if (!dataObj) return;

            const ctx = document.getElementById('trendChart');
            if (!ctx) return;

            if (trendChartInstance) {
                trendChartInstance.destroy();
            }

            const displayLen = histMonthsCount + currentPeriod;
            const displayLabels = trendLabels.slice(0, displayLen);

            const histData = [...dataObj.hist];
            while(histData.length < displayLen) histData.push(null);
            histData.length = Math.min(histData.length, displayLen);

            // Func helper to pad arrays
            const padData = (projArr) => {
                const arr = Array(histMonthsCount).fill(null);
                if (dataObj.hist.length > 0) arr[histMonthsCount-1] = dataObj.hist[histMonthsCount-1];
                if (projArr) arr.push(...projArr.slice(0, currentPeriod));
                return arr;
            };

            const linearData = padData(dataObj.trend);
            const baseData = padData(dataObj.base);
            const pesimistaData = padData(dataObj.pesimista);
            const optimistaData = padData(dataObj.optimista);

            const mcPesimistaData = (mcDataObj && mcDataObj.pesimista) ? padData(mcDataObj.pesimista) : Array(displayLen).fill(null);
            const mcBaseData = (mcDataObj && mcDataObj.base) ? padData(mcDataObj.base) : Array(displayLen).fill(null);
            const mcOptimistaData = (mcDataObj && mcDataObj.optimista) ? padData(mcDataObj.optimista) : Array(displayLen).fill(null);

            const datasets = [
                {
                    label: 'Histrico Real',
                    data: histData,
                    borderColor: '#343a40',
                    backgroundColor: 'rgba(52, 58, 64, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.3,
                    pointRadius: 4,
                }
            ];

            const addTendencia = () => {
                datasets.push({
                    label: 'Tendencia Estadstica',
                    data: linearData,
                    borderColor: '#17a2b8',
                    borderWidth: 2,
                    borderDash: [5, 5],
                    fill: false,
                    tension: 0.3,
                    pointRadius: 3,
                    hidden: true,
                });
                datasets.push({
                    label: 'Pesimista',
                    data: pesimistaData,
                    borderColor: '#dc3545',
                    borderWidth: 2,
                    borderDash: [5, 5],
                    fill: false,
                    tension: 0.3,
                    pointRadius: 3,
                });
                datasets.push({
                    label: 'Base / Neutral',
                    data: baseData,
                    borderColor: '#007bff',
                    borderWidth: 3,
                    fill: false,
                    tension: 0.3,
                    pointRadius: 4,
                });
                datasets.push({
                    label: 'Optimista',
                    data: optimistaData,
                    borderColor: '#28a745',
                    borderWidth: 2,
                    borderDash: [5, 5],
                    fill: false,
                    tension: 0.3,
                    pointRadius: 3,
                });
            };

            const addMontecarlo = () => {
                datasets.push({
                    label: 'MC Pesimista',
                    data: mcPesimistaData,
                    borderColor: '#e83e8c', // Pink/Reddish
                    borderWidth: 2,
                    borderDash: [3, 3],
                    fill: false,
                    tension: 0.3,
                    pointRadius: 3,
                });
                datasets.push({
                    label: 'MC Base',
                    data: mcBaseData,
                    borderColor: '#6610f2', // Indigo/Purple
                    borderWidth: 3,
                    borderDash: [3, 3],
                    fill: false,
                    tension: 0.3,
                    pointRadius: 4,
                });
                datasets.push({
                    label: 'MC Optimista',
                    data: mcOptimistaData,
                    borderColor: '#20c997', // Teal/Greenish
                    borderWidth: 2,
                    borderDash: [3, 3],
                    fill: false,
                    tension: 0.3,
                    pointRadius: 3,
                });
            };

            if (chartMode === 'tendencia' || chartMode === 'ambos') {
                addTendencia();
            }
            if ((chartMode === 'montecarlo' || chartMode === 'ambos') && showMCCols && mcDataObj && Object.keys(mcDataObj).length > 0) {
                addMontecarlo();
            }

            trendChartInstance = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: displayLabels,
                    datasets: datasets
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: { mode: 'index', intersect: false },
                    plugins: {
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    let label = context.dataset.label || '';
                                    if (label) {
                                        label += ': ';
                                    }
                                    if (context.parsed.y !== null) {
                                        label += new Intl.NumberFormat('es-PE', { style: 'currency', currency: 'PEN' }).format(context.parsed.y);
                                    }
                                    return label;
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            ticks: {
                                callback: function(value) {
                                    if (value >= 1000000) return (value / 1000000).toFixed(1) + 'M';
                                    if (value >= 1000) return (value / 1000).toFixed(0) + 'k';
                                    return value;
                                }
                            }
                        }
                    }
                }
            });
        }

        function loadTrendData() {
            if (typeof Chart === 'undefined') {
                const script = document.createElement('script');
                script.src = 'https://cdn.jsdelivr.net/npm/chart.js';
                script.onload = fetchTrendData;
                document.head.appendChild(script);
            } else {
                fetchTrendData();
            }
        }

        let isStep6Locked = {{ plan.locked_steps.step6|yesno:"true,false" }};

        function updateLockUI() {
            if (isStep6Locked) {
                $('#btn-save-step6').hide();
                $('#btn-edit-step6').show();
                $('.trend-period-btn').prop('disabled', true);
                $('#mc-iterations').prop('disabled', true);
                $('#btn-run-mc').prop('disabled', true);
                $('#btn-apply-trend').prop('disabled', true);
                $('#scenario-adjust-table input').prop('disabled', true);
                $('#scenario-adjust-table .btn-primary').prop('disabled', true);
            } else {
                $('#btn-save-step6').show();
                $('#btn-edit-step6').hide();
                $('.trend-period-btn').prop('disabled', false);
                $('#mc-iterations').prop('disabled', false);
                $('#btn-run-mc').prop('disabled', false);
                $('#btn-apply-trend').prop('disabled', false);
                $('#scenario-adjust-table input').prop('disabled', false);
                $('#scenario-adjust-table .btn-primary').prop('disabled', false);
            }
        }

        function lockStep6() {
            Swal.fire({
                title: 'Guardando Proyección',
                text: 'Por favor espere...',
                allowOutsideClick: false,
                didOpen: () => { Swal.showLoading(); }
            });
            
            const payload = {
                status: "success",
                labels: trendLabels,
                hist_months: histMonthsCount,
                datasets_by_agency: trendDatasetsByAgency
            };

            $.ajax({
                url: "{% url 'financial_planning:api_lock_step6' plan.id %}",
                method: "POST",
                contentType: "application/json",
                data: JSON.stringify({ full_payload: payload }),
                headers: { "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]') ? document.querySelector('[name=csrfmiddlewaretoken]').value : '{{ csrf_token }}' },
                success: function(resp) {
                    Swal.close();
                    if(resp.status === 'success') {
                        isStep6Locked = true;
                        updateLockUI();
                        Swal.fire('Guardado', 'Proyección guardada y bloqueada exitosamente.', 'success');
                    } else {
                        Swal.fire('Error', resp.msg, 'error');
                    }
                },
                error: function(err) {
                    Swal.fire('Error', 'No se pudo guardar la proyección', 'error');
                }
            });
        }

        function unlockStep6() {
            Swal.fire({
                title: 'Desbloqueando',
                text: 'Por favor espere...',
                allowOutsideClick: false,
                didOpen: () => { Swal.showLoading(); }
            });
            $.ajax({
                url: "{% url 'financial_planning:api_unlock_step6' plan.id %}",
                method: "POST",
                headers: { "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]') ? document.querySelector('[name=csrfmiddlewaretoken]').value : '{{ csrf_token }}' },
                success: function(resp) {
                    Swal.close();
                    if(resp.status === 'success') {
                        isStep6Locked = false;
                        updateLockUI();
                        Swal.fire({ toast: true, position: 'top-end', icon: 'success', title: 'Paso desbloqueado', showConfirmButton: false, timer: 2000 });
                    }
                }
            });
        }

        function fetchTrendData() {
            $.ajax({
                url: "{% url 'financial_planning:api_get_trend_data' plan.id %}",
                method: "GET",
                success: function(response) {
                    if (response.status === 'success') {
                        trendLabels = response.labels;
                        trendDatasetsByAgency = response.datasets_by_agency;
                        histMonthsCount = response.hist_months;
                        
                        const selectAgency = $('#trend-agency-select');
                        selectAgency.empty();
                        for (const agencyId in trendDatasetsByAgency) {
                            selectAgency.append(new Option(trendDatasetsByAgency[agencyId].name, agencyId));
                        }
                        
                        function updateVariablesUI(agencyId) {
                            const btnGroup = $('#variable-btn-group');
                            btnGroup.empty();
                            if (trendDatasetsByAgency[agencyId]) {
                                const vars = trendDatasetsByAgency[agencyId].variables;
                                let keepVariable = vars.find(v => v.id === currentVariable) ? currentVariable : (vars.length > 0 ? vars[0].id : null);
                                currentVariable = keepVariable;

                                vars.forEach((d) => {
                                    const isActive = d.id === currentVariable;
                                    const btn = $(`<button type="button" class="btn btn-outline-primary font-weight-bold ${isActive ? 'active' : ''}" data-var="${d.id}" style="font-size: 0.85rem;">${d.name}</button>`);
                                    btn.on('click', function() {
                                        btnGroup.find('.btn').removeClass('active');
                                        $(this).addClass('active');
                                        currentVariable = d.id;
                                        
                                        updateDashboard();

                                    });
                                    btnGroup.append(btn);
                                });
                            }
                        }
                        
                        function updateDashboard() {
                            if (!currentAgency || !currentVariable) return;
                            renderTrendChart(currentAgency, currentVariable);
                            renderAdjustmentsTable(currentAgency);
                            renderMonthlyTable(currentAgency, currentVariable, currentPeriod);
                        }
                        

                        function renderAdjustmentsTable(agencyId) {
                            const tbody = $('#scenario-adjust-table tbody');
                            tbody.empty();
                            if (!trendDatasetsByAgency[agencyId]) return;
                            const vars = trendDatasetsByAgency[agencyId].variables;
                            vars.forEach(v => {
                                const pesimistaRate = (v.rates && v.rates.pesimista) ? parseFloat(v.rates.pesimista).toFixed(1) : 0;
                                const baseRate = (v.rates && v.rates.base) ? parseFloat(v.rates.base).toFixed(1) : 0;
                                const optimistaRate = (v.rates && v.rates.optimista) ? parseFloat(v.rates.optimista).toFixed(1) : 0;
                                
                                tbody.append(`
                                    <tr style="border-bottom: 1px dashed #e9ecef;">
                                        <td class="font-weight-bold text-dark py-2">${v.name}</td>
                                        <td class="text-center py-2 text-muted" style="font-size: 0.85rem;"><i class="fas fa-arrow-trend-up mr-1"></i>${baseRate}%</td>
                                        <td class="text-center py-2 text-danger font-weight-bold cell-pesimista">${pesimistaRate}%</td>
                                        <td class="text-center py-2 text-primary font-weight-bold cell-base">${baseRate}%</td>
                                        <td class="text-center py-2 text-success font-weight-bold cell-optimista">${optimistaRate}%</td>
                                        <td class="text-center py-2 cell-action">
                                            <button class="btn btn-sm btn-light text-primary rounded-circle shadow-sm" style="width: 28px; height: 28px; padding: 0;" title="Ajustar" onclick="editScenarioAdjustments(this, '${v.id}', '${agencyId}')">
                                                <i class="fas fa-edit"></i>
                                            </button>
                                        </td>
                                    </tr>
                                `);
                            });
                        }

                        window.editScenarioAdjustments = function(btn, vId, agencyId) {
                            const tr = $(btn).closest('tr');
                            
                            const tdPesimista = tr.find('.cell-pesimista');
                            const tdBase = tr.find('.cell-base');
                            const tdOptimista = tr.find('.cell-optimista');
                            
                            const valPesimista = tdPesimista.text().replace('%', '');
                            const valBase = tdBase.text().replace('%', '');
                            const valOptimista = tdOptimista.text().replace('%', '');
                            
                            tdPesimista.html(`<input type="number" step="0.1" class="form-control form-control-sm input-pesimista text-center mx-auto" style="width: 60px; font-size: 0.8rem; padding: 2px;" value="${valPesimista}">`);
                            tdBase.html(`<input type="number" step="0.1" class="form-control form-control-sm input-base text-center mx-auto" style="width: 60px; font-size: 0.8rem; padding: 2px;" value="${valBase}">`);
                            tdOptimista.html(`<input type="number" step="0.1" class="form-control form-control-sm input-optimista text-center mx-auto" style="width: 60px; font-size: 0.8rem; padding: 2px;" value="${valOptimista}">`);
                            
                            const tdAction = tr.find('.cell-action');
                            tdAction.html(`
                                <div class="d-flex justify-content-center">
                                    <button class="btn btn-sm btn-success rounded-circle shadow-sm" style="width: 28px; height: 28px; padding: 0;" title="Guardar" onclick="saveScenarioAdjustments(this, '${vId}', '${agencyId}')">
                                        <i class="fas fa-check"></i>
                                    </button>
                                    <button class="btn btn-sm btn-danger rounded-circle shadow-sm ml-1" style="width: 28px; height: 28px; padding: 0;" title="Cancelar" onclick="renderAdjustmentsTable('${agencyId}')">
                                        <i class="fas fa-times"></i>
                                    </button>
                                </div>
                            `);
                        };

                        window.saveScenarioAdjustments = function(btn, vId, agencyId) {
                            const tr = $(btn).closest('tr');
                            const newPesimista = tr.find('.input-pesimista').val();
                            const newBase = tr.find('.input-base').val();
                            const newOptimista = tr.find('.input-optimista').val();
                            
                            if (!trendDatasetsByAgency[agencyId]) return;
                            const vars = trendDatasetsByAgency[agencyId].variables;
                            const v = vars.find(d => d.id === vId);
                            if (v) {
                                if (!v.rates) v.rates = {};
                                v.rates.pesimista = newPesimista;
                                v.rates.base = newBase;
                                v.rates.optimista = newOptimista;
                            }
                            
                            const scenariosPayload = {};
                            vars.forEach(vv => {
                                if (vv.rates) {
                                    scenariosPayload[vv.id] = {
                                        pessimistic: vv.rates.pesimista,
                                        base: vv.rates.base,
                                        optimistic: vv.rates.optimista
                                    };
                                }
                            });
                            
                            $(btn).html('<i class="fas fa-spinner fa-spin"></i>').prop('disabled', true);
                            tr.find('.btn-danger').prop('disabled', true);
                            
                            $.ajax({
                                url: "{% url 'financial_planning:api_save_trend_scenarios' plan.id %}",
                                method: "POST",
                                contentType: "application/json",
                                data: JSON.stringify({
                                    agency: agencyId,
                                    scenarios: scenariosPayload
                                }),
                                headers: {
                                    "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]') ? document.querySelector('[name=csrfmiddlewaretoken]').value : '{{ csrf_token }}'
                                },
                                success: function(response) {
                                    if (response.status === 'success') {
                                        Swal.fire({
                                            toast: true,
                                            position: 'top-end',
                                            icon: 'success',
                                            title: 'Ajustes guardados correctamente',
                                            showConfirmButton: false,
                                            timer: 2000
                                        });
                                        fetchTrendData();
                                    } else {
                                        Swal.fire('Error', response.msg || 'Hubo un error al guardar.', 'error');
                                        renderAdjustmentsTable(agencyId);
                                    }
                                },
                                error: function(err) {
                                    Swal.fire('Error', 'Error de conexión', 'error');
                                    renderAdjustmentsTable(agencyId);
                                }
                            });
                        };
                        
                        
                        showTrendCols = false;
                        showMCCols = false;
                        mcDataObj = null;

                        function renderMonthlyTable(agencyId, variableId, period) {

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
                                    <th class="text-right font-weight-bold text-danger" style="min-width: 140px;">Pesimista</th>
                                    <th class="text-right font-weight-bold text-primary" style="min-width: 140px;">Base</th>
                                    <th class="text-right font-weight-bold text-success" style="min-width: 140px;">Optimista</th>`;
                            
                            if (showTrendCols) {
                                theadHtml += `
                                    <th class="text-right font-weight-bold text-secondary" style="min-width: 140px;">Tend. Año Ant.</th>`;
                            }
                            
                            if (showMCCols && mcDataObj) {
                                theadHtml += `
                                    <th class="text-right font-weight-bold text-danger" style="min-width: 140px; border-left: 2px solid #dee2e6;">MC Pesimista</th>
                                    <th class="text-right font-weight-bold text-primary" style="min-width: 140px;">MC Base</th>
                                    <th class="text-right font-weight-bold text-success" style="min-width: 140px;">MC Optimista</th>`;
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
                                    <td class="text-right text-danger">${formatVal(v.pesimista[idx])}</td>
                                    <td class="text-right font-weight-bold text-primary">${formatVal(v.base[idx])}</td>
                                    <td class="text-right text-success">${formatVal(v.optimista[idx])}</td>`;
                                
                                if (showTrendCols) {
                                    html += `<td class="text-right text-secondary font-weight-bold">${formatVal(v.trend[idx])}</td>`;
                                }
                                
                                if (showMCCols && mcDataObj) {
                                    html += `
                                        <td class="text-right text-danger" style="border-left: 2px solid #dee2e6;">${formatVal(mcDataObj.pesimista[i])}</td>
                                        <td class="text-right font-weight-bold text-primary">${formatVal(mcDataObj.base[i])}</td>
                                        <td class="text-right text-success">${formatVal(mcDataObj.optimista[i])}</td>`;
                                }
                                
                                html += `</tr>`;
                            }
                            html += `</tbody></table>`;
                            container.html(html);
                        }
                        
                        currentAgency = selectAgency.val();
                        updateVariablesUI(currentAgency);
                        
                        $('#trend-loading').hide();
                        $('#trend-chart-container').fadeIn();
                        
                        updateDashboard();
                        updateLockUI();
                        
                $('#btn-apply-trend').off('click').on('click', function() {
                    showTrendCols = !showTrendCols;
                    if (showTrendCols) {
                        showMCCols = false; // Hide Montecarlo when showing trend
                        mcDataObj = null;     // Clear simulated data
                        chartMode = 'tendencia';
                        $('#chart-mode-group .btn').removeClass('active');
                        $('#chart-mode-group .btn[data-mode="tendencia"]').addClass('active');
                    }
                    updateDashboard();
                });

                $('#chart-mode-group .btn').off('click').on('click', function() {
                    $('#chart-mode-group .btn').removeClass('active');
                    $(this).addClass('active');
                    chartMode = $(this).data('mode');
                    
                    if (chartMode === 'tendencia') {
                        showTrendCols = true;
                        showMCCols = false;
                    } else if (chartMode === 'montecarlo') {
                        showTrendCols = false;
                        showMCCols = !!mcDataObj;
                    } else if (chartMode === 'ambos') {
                        showTrendCols = true;
                        showMCCols = !!mcDataObj;
                    }
                    
                    updateDashboard();
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
                    
                    // Activate Montecarlo Mode automatically for the animation
                    $('#chart-mode-group .btn').removeClass('active');
                    $('#chart-mode-group .btn[data-mode="montecarlo"]').addClass('active');
                    chartMode = 'montecarlo';
                    showTrendCols = false;
                    showMCCols = true;
                    
                    // Start Animation Interval (20 FPS)
                    let animationInterval = setInterval(() => {
                        let fakeObj = { pesimista: [], base: [], optimista: [] };
                        const startIdx = 1;
                        for (let i = 0; i < period; i++) {
                            const idx = startIdx + i;
                            let baseVal = v.base[idx] || 0; 
                            let noiseP = baseVal * (0.85 + Math.random() * 0.10); // 85%-95%
                            let noiseB = baseVal * (0.95 + Math.random() * 0.10); // 95%-105%
                            let noiseO = baseVal * (1.05 + Math.random() * 0.10); // 105%-115%
                            
                            if (variableId.toLowerCase().includes('mora')) {
                                let tmp = noiseP;
                                noiseP = noiseO;
                                noiseO = tmp;
                            }
                            
                            fakeObj.pesimista.push(noiseP);
                            fakeObj.base.push(noiseB);
                            fakeObj.optimista.push(noiseO);
                        }
                        mcDataObj = fakeObj;
                        renderMonthlyTable(agencyId, variableId, period);
                    }, 50);
                    
                    $.ajax({
                        url: "{% url 'financial_planning:api_run_montecarlo' plan.id %}",
                        type: 'POST',
                        contentType: 'application/json',
                        data: JSON.stringify({
                            history: v.hist,
                            proj_months: period,
                            iterations: parseInt(iterations),
                            variable_id: v.id
                        }),
                        headers: {
                            'X-CSRFToken': '{{ csrf_token }}'
                        },
                        success: function(res) {
                            clearInterval(animationInterval);
                            if(res.status === 'success') {
                                mcDataObj = res.data;
                                updateDashboard(); // updates both chart and table with final data
                            } else {
                                alert("Error en Montecarlo: " + res.msg);
                            }
                        },
                        error: function() {
                            clearInterval(animationInterval);
                            alert("Error de conexión al generar Montecarlo");
                        },
                        complete: function() {
                            btn.html(originalHtml);
                            btn.prop('disabled', false);
                        }
                    });
                });
                
                selectAgency.on('change', function() {
                    currentAgency = $(this).val();
                    updateVariablesUI(currentAgency);
                    updateDashboard();
                });
                
                $('.trend-period-btn').on('click', function() {
                    $('.trend-period-btn').removeClass('active');
                    $(this).addClass('active');
                    currentPeriod = parseInt($(this).data('months'));
                    updateDashboard();
                });
            } else {
                $('#trend-loading').html('<div class="alert alert-danger">Error al cargar datos: ' + response.msg + '</div>');
            }
        },
        error: function() {
            $('#trend-loading').html('<div class="alert alert-danger">Error de conexión al cargar las tendencias.</div>');
        }
    });
}

$(document).ready(function() {
    loadTrendData();
});
{% endif %}

function filterERByYear(year) {
    // update tab styles
    document.querySelectorAll('#erTabs .nav-link').forEach(t => {
        t.classList.remove('active', 'font-weight-bold', 'text-primary');
        t.classList.add('text-muted');
        t.style.backgroundColor = '#f8f9fa';
    });
    const activeTab = document.getElementById('er-' + year + '-tab');
    if(activeTab) {
        activeTab.classList.add('active', 'font-weight-bold', 'text-primary');
        activeTab.classList.remove('text-muted');
        activeTab.style.backgroundColor = '#fff';
    }

    const table = document.getElementById('erTable');
    if (!table) return;

    // get headers
    const ths = table.querySelectorAll('thead th');
    const colsToShow = [];
    ths.forEach((th, index) => {
        if (index === 0) {
            colsToShow.push(index); // Always show Concepto
            th.classList.remove('d-none');
            return;
        }
        // Use textContent instead of innerText because innerText returns "" if the element is display: none
        const text = (th.textContent || "").trim();
        const colYear = text.split('-')[0];
        if (year === 'all' || colYear === String(year)) {
            colsToShow.push(index);
            th.classList.remove('d-none');
        } else {
            th.classList.add('d-none');
        }
    });

    // apply to all rows
    const rows = table.querySelectorAll('tbody tr');
    rows.forEach(row => {
        const tds = row.querySelectorAll('td');
        tds.forEach((td, index) => {
            if (colsToShow.includes(index)) {
                td.classList.remove('d-none');
            } else {
                td.classList.add('d-none');
            }
        });
    });
}

document.addEventListener('DOMContentLoaded', function() {
    {% if step == 7 and projected_years %}
    filterERByYear('{{ projected_years.0 }}');
    {% endif %}
});

function exportAnalysisToExcelStep7() {
    const table = document.getElementById('erTable');
    if (!table) return;
    
    // Create a clone to strip out hidden elements
    const clone = table.cloneNode(true);
    
    // Remove hidden headers
    clone.querySelectorAll('thead th').forEach(th => {
        if (th.classList.contains('d-none') || th.style.display === 'none') {
            th.remove();
        }
    });
    
    // Remove hidden cells in rows
    clone.querySelectorAll('tbody tr').forEach(tr => {
        if (tr.classList.contains('d-none') || tr.style.display === 'none') {
            tr.remove();
        } else {
            tr.querySelectorAll('td').forEach(td => {
                if (td.classList.contains('d-none') || td.style.display === 'none') {
                    td.remove();
                } else {
                    // Remove buttons/icons from text content for excel
                    let btn = td.querySelector('button');
                    if (btn) btn.remove();
                }
            });
        }
    });
    
    const wb = XLSX.utils.table_to_book(clone, {sheet: "PyL Proyectado"});
    XLSX.writeFile(wb, 'Proyeccion_PyL.xlsx');
}

function exportAnalysisToImageStep7() {
    const container = document.querySelector('.table-responsive');
    if (!container) return;
    
    const exportBtn = document.getElementById('dropdownMenuButtonExportP7');
    if(exportBtn) exportBtn.style.visibility = 'hidden';

    html2canvas(container, {
        scale: 2,
        backgroundColor: '#ffffff',
        useCORS: true
    }).then(canvas => {
        if(exportBtn) exportBtn.style.visibility = 'visible';
        const link = document.createElement('a');
        link.download = `Proyeccion_PyL_${new Date().toISOString().slice(0,10)}.png`;
        link.href = canvas.toDataURL('image/png');
        link.click();
    });
}

function exportAnalysisToPDFStep7() {
    const container = document.querySelector('.table-responsive');
    if (!container) return;

    const exportBtn = document.getElementById('dropdownMenuButtonExportP7');
    if(exportBtn) exportBtn.style.visibility = 'hidden';

    html2canvas(container, {
        scale: 2,
        backgroundColor: '#ffffff',
        useCORS: true
    }).then(canvas => {
        if(exportBtn) exportBtn.style.visibility = 'visible';
        const imgData = canvas.toDataURL('image/png');
        const { jsPDF } = window.jspdf;
        
        const pdf = new jsPDF('l', 'mm', 'a4');
        const pdfWidth = pdf.internal.pageSize.getWidth();
        const pdfHeight = (canvas.height * pdfWidth) / canvas.width;
        
        pdf.addImage(imgData, 'PNG', 0, 0, pdfWidth, pdfHeight);
        pdf.save(`Proyeccion_PyL_${new Date().toISOString().slice(0,10)}.pdf`);
    });
}
