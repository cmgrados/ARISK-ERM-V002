
                    document.addEventListener('DOMContentLoaded', function() {
                        const loadingDatesSpan = document.getElementById('portfolio-dates-loading');
                        const thead = document.getElementById('portfolio-history-thead');
                        const tbody = document.getElementById('portfolio-history-tbody');
                        const planId = 'VAR';

                        const MONTH_NAMES = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'];
                        let portAllPeriods = [];
                        let savedPortPeriods = VAR;
                        let portSelectedPeriods = [];

                        // 1. Fetch available dates
                        fetch("URL")
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
                            
                            URL
                            // Save to backend
                            fetch("URL", {
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
                            URL
                        };

                        // 2. Load Portfolio Data
                        window.loadHistoricalPortfolio = function() {
                            const btn = document.getElementById('btn-load-portfolio');
                            if(btn) btn.innerHTML = '<i class="fas fa-spinner fa-spin mr-1"></i> Cargando...';
                            
                            const selectedDates = portSelectedPeriods.join(',');
                            
                            fetch("URL?plan_id=" + planId + "&dates=" + selectedDates)
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
                                    <th colspan="6" class="text-center bg-light" style="color: #28a745;">Cobranza Est. (Monto)</th>
                                    <th rowspan="2" class="text-center text-danger">Cartera Vcda. (Monto)</th>
                                </tr>
                                <tr>
                                    ${Array(5).fill(types.map(t => `<th class="text-center">${t}</th>`).join('')).join('')}
                                </tr>
                            `;

                            let html = '';
                            const agencies = Object.keys(backendData).sort((a,b) => a === 'ACUMULADO' ? -1 : (b === 'ACUMULADO' ? 1 : a.localeCompare(b)));
                            
                            agencies.forEach(agName => {
                                const periods = backendData[agName];
                                if(!periods || periods.length === 0) return;
                                
                                let prevSaldos = null;
                                
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
                                    let currentSaldos = {};
                                    prods.forEach(t => {
                                        const val = p.types[t] ? p.types[t].saldo_cart : 0;
                                        tot_sld_car += val;
                                        currentSaldos[t] = val;
                                        html += `<td class="text-monospace text-right">${formatNum(val)}</td>`;
                                    });
                                    html += `<td class="text-monospace text-right font-weight-bold bg-light">${formatNum(tot_sld_car)}</td>`;

                                    // Cobranza Estimada
                                    let tot_cobranza = 0;
                                    prods.forEach(t => {
                                        if (prevSaldos !== null) {
                                            const des = p.types[t] ? p.types[t].monto_des : 0;
                                            const cobranza = prevSaldos[t] + des - currentSaldos[t];
                                            tot_cobranza += cobranza;
                                            html += `<td class="text-monospace text-right" style="color: #28a745;">${formatNum(cobranza)}</td>`;
                                        } else {
                                            html += `<td class="text-monospace text-right text-muted">-</td>`;
                                        }
                                    });
                                    if (prevSaldos !== null) {
                                        html += `<td class="text-monospace text-right font-weight-bold bg-light" style="color: #28a745;">${formatNum(tot_cobranza)}</td>`;
                                    } else {
                                        html += `<td class="text-monospace text-right font-weight-bold bg-light text-muted">-</td>`;
                                    }

                                    // Mora
                                    html += `<td class="text-monospace text-right text-danger font-weight-bold bg-light">${formatNum(p.vcda)}</td>`;
                                    
                                    html += `</tr>`;
                                    
                                    prevSaldos = currentSaldos;
                                });
                            });

                            tbody.innerHTML = html;
                        }

                        function formatNum(val, decimals=2) {
                            if (!val || val === 0) return '<span class="text-muted">-</span>';
                            return val.toLocaleString('en-US', {minimumFractionDigits: decimals, maximumFractionDigits: decimals});
                        }
                    });
                