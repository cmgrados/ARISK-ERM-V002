
                    document.addEventListener('DOMContentLoaded', function() {
                        const loadingDatesSpan = document.getElementById('passive-dates-loading');
                        const thead = document.getElementById('passive-history-thead');
                        const tbody = document.getElementById('passive-history-tbody');
                        const planId = 'VAR';
                        
                        let passAllPeriods = [];
                        let savedPassPeriods = VAR;
                        let passSelectedPeriods = [];

                        // 1. Fetch available dates
                        fetch("URL")
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
                            
                            URL
                            // Save to backend
                            fetch("URL", {
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
                            URL
                        };

                        // 2. Load Passive Data
                        window.loadHistoricalPassive = function() {
                            const btn = document.getElementById('btn-load-passive');
                            if(btn) btn.innerHTML = '<i class="fas fa-spinner fa-spin mr-1"></i> Cargando...';
                            
                            const selectedDates = passSelectedPeriods.join(',');

                            fetch("URL?plan_id=" + planId + "&dates=" + selectedDates)
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
                