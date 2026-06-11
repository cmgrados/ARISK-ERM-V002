
    function prepareContainerForExport(container) {
        // Hide all buttons and inputs
        const uiElements = container.querySelectorAll('button, input, .dropdown');
        const hiddenElements = [];
        uiElements.forEach(el => {
            if (el.style.display !== 'none') {
                hiddenElements.push({ el, origDisplay: el.style.display });
                el.style.display = 'none';
            }
        });

        // Expand table responsive areas to avoid scrollbars in the capture
        const tableResp = container.querySelector('.table-responsive');
        let origOverflow = '', origMaxHeight = '';
        if (tableResp) {
            origOverflow = tableResp.style.overflow;
            origMaxHeight = tableResp.style.maxHeight;
            tableResp.style.overflow = 'visible';
            tableResp.style.maxHeight = 'none';
        }

        return { hiddenElements, tableResp, origOverflow, origMaxHeight };
    }

    function restoreContainerAfterExport(restoreState) {
        if (restoreState.hiddenElements) {
            restoreState.hiddenElements.forEach(item => {
                item.el.style.display = item.origDisplay;
            });
        }
        if (restoreState.tableResp) {
            restoreState.tableResp.style.overflow = restoreState.origOverflow;
            restoreState.tableResp.style.maxHeight = restoreState.origMaxHeight;
        }
    }

    function exportAnalysisToImage() {
        const container = document.getElementById('step6-export-area') || document.querySelector('.row.mb-4');
        if (!container) return;
        
        const restoreState = prepareContainerForExport(container);

        html2canvas(container, {
            scale: 2,
            backgroundColor: '#ffffff',
            useCORS: true
        }).then(canvas => {
            restoreContainerAfterExport(restoreState);
            const link = document.createElement('a');
            link.download = `Proyeccion_Tendencias_${new Date().toISOString().slice(0,10)}.png`;
            link.href = canvas.toDataURL('image/png');
            link.click();
        }).catch(err => {
            restoreContainerAfterExport(restoreState);
            console.error("Error generating image:", err);
        });
    }

    function exportAnalysisToPDF() {
        const container = document.getElementById('step6-export-area') || document.querySelector('.row.mb-4');
        if (!container) return;

        const restoreState = prepareContainerForExport(container);

        html2canvas(container, {
            scale: 2,
            backgroundColor: '#ffffff',
            useCORS: true
        }).then(canvas => {
            restoreContainerAfterExport(restoreState);
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
        }).catch(err => {
            restoreContainerAfterExport(restoreState);
            console.error("Error generating PDF:", err);
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

        window.costParams = {};
        window.yieldParams = {};
        {% if institutional_assumptions_json and institutional_assumptions_json != '{}' %}
        try {
            const instAssump = JSON.parse('{{ institutional_assumptions_json|escapejs }}');
            if (instAssump.costParams) {
                window.costParams = instAssump.costParams;
            }
            if (instAssump.yieldParams) {
                window.yieldParams = instAssump.yieldParams;
            }
        } catch(e) {
            console.error("Error parsing institutional_assumptions:", e);
        }
        {% endif %}

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
                
                // Si la variable tiene datos de Montecarlo y el modo MC o Ambos está activo, incluirlos en la exportación
                const hasMC = (showMCCols && v.mc_data && Object.keys(v.mc_data).length > 0);
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
                            v.mc_data.pesimista[i],
                            v.mc_data.base[i],
                            v.mc_data.optimista[i]
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
                $('#scenario-adjust-table button').prop('disabled', true);
                $('#yield-simulation-container input').prop('disabled', true);
                $('#yield-simulation-container button').prop('disabled', true);
                $('#cost-simulation-container input').prop('disabled', true);
                $('#cost-simulation-container button').prop('disabled', true);
            } else {
                $('#btn-save-step6').show();
                $('#btn-edit-step6').hide();
                $('.trend-period-btn').prop('disabled', false);
                $('#mc-iterations').prop('disabled', false);
                $('#btn-run-mc').prop('disabled', false);
                $('#btn-apply-trend').prop('disabled', false);
                $('#scenario-adjust-table input').prop('disabled', false);
                $('#scenario-adjust-table button').prop('disabled', false);
                $('#yield-simulation-container input').prop('disabled', false);
                $('#yield-simulation-container button').prop('disabled', false);
                $('#cost-simulation-container input').prop('disabled', false);
                $('#cost-simulation-container button').prop('disabled', false);
            }
        }

        function lockStep6() {
            Swal.fire({
                title: 'Guardando Proyección',
                text: 'Por favor espere...',
                allowOutsideClick: false,
                didOpen: () => { Swal.showLoading(); }
            });
            
            const doLock = () => {
                const payload = {
                    status: "success",
                    labels: trendLabels,
                    hist_months: histMonthsCount,
                    datasets_by_agency: trendDatasetsByAgency,
                    ui_state: {
                        chartMode: chartMode,
                        showTrendCols: showTrendCols,
                        showMCCols: showMCCols,
                        currentAgency: currentAgency,
                        currentVariable: currentVariable,
                        currentPeriod: currentPeriod
                    }
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
                        Swal.close();
                        Swal.fire('Error', 'No se pudo guardar la proyección', 'error');
                    }
                });
            };

            if (window.costParams || window.yieldParams) {
                const assumptionsPayload = {};
                if (window.costParams) assumptionsPayload.costParams = window.costParams;
                if (window.yieldParams) assumptionsPayload.yieldParams = window.yieldParams;
                
                fetch(`{% url 'financial_planning:save_institutional_assumptions' plan.id %}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]') ? document.querySelector('[name=csrfmiddlewaretoken]').value : '{{ csrf_token }}'
                    },
                    body: JSON.stringify(assumptionsPayload)
                }).then(res => res.json())
                  .then(data => {
                      doLock();
                  })
                  .catch(err => {
                      console.error('Error saving assumptions:', err);
                      doLock(); // Even if assumptions fail, attempt to save the projection data to not block the user entirely
                  });
            } else {
                doLock();
            }
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
                        
                        if (response.ui_state) {
                            chartMode = response.ui_state.chartMode;
                            showTrendCols = response.ui_state.showTrendCols;
                            showMCCols = response.ui_state.showMCCols;
                            if (response.ui_state.currentAgency) {
                                currentAgency = response.ui_state.currentAgency;
                            }
                            if (response.ui_state.currentVariable) {
                                currentVariable = response.ui_state.currentVariable;
                            }
                            if (response.ui_state.currentPeriod) {
                                currentPeriod = response.ui_state.currentPeriod;
                            }
                        }
                        
                        const selectAgency = $('#trend-agency-select');
                        selectAgency.empty();
                        for (const agencyId in trendDatasetsByAgency) {
                            selectAgency.append(new Option(trendDatasetsByAgency[agencyId].name, agencyId));
                        }
                        if (currentAgency) {
                            selectAgency.val(currentAgency);
                        }
                        
                        function updateVariablesUI(agencyId) {
                            const btnGroup = $('#variable-btn-group');
                            btnGroup.empty();
                            if (trendDatasetsByAgency[agencyId]) {
                                const vars = trendDatasetsByAgency[agencyId].variables;
                                let keepVariable = vars.find(v => v.id === currentVariable) ? currentVariable : (vars.length > 0 ? vars[0].id : null);
                                currentVariable = keepVariable;
                                const cv = vars.find(v => v.id === currentVariable);
                                mcDataObj = cv ? (cv.mc_data || null) : null;
                                if(mcDataObj && chartMode !== 'tendencia') showMCCols = true;

                                vars.forEach((d) => {
                                    const isActive = d.id === currentVariable;
                                    const btn = $(`<button type="button" class="btn btn-outline-primary font-weight-bold ${isActive ? 'active' : ''}" data-var="${d.id}" style="font-size: 0.85rem;">${d.name}</button>`);
                                    btn.on('click', function() {
                                        btnGroup.find('.btn').removeClass('active');
                                        $(this).addClass('active');
                                        currentVariable = d.id;
                                        mcDataObj = d.mc_data || null;
                                        if(mcDataObj) {
                                            showMCCols = true;
                                            chartMode = 'ambos'; // or 'montecarlo'
                                            $('#chart-mode-group .btn').removeClass('active');
                                            $('#chart-mode-group .btn[data-mode="ambos"]').addClass('active');
                                        } else {
                                            showMCCols = false;
                                        }
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
                                const pesimistaRate = (v.rates && v.rates.pesimista) ? parseFloat(v.rates.pesimista).toFixed(2) : '0.00';
                                const baseRate = (v.rates && v.rates.base) ? parseFloat(v.rates.base).toFixed(2) : '0.00';
                                const optimistaRate = (v.rates && v.rates.optimista) ? parseFloat(v.rates.optimista).toFixed(2) : '0.00';
                                const trendRate = (v.rates && v.rates.trend) ? parseFloat(v.rates.trend).toFixed(2) : '0.00';
                                
                                tbody.append(`
                                    <tr style="border-bottom: 1px dashed #e9ecef;">
                                        <td class="font-weight-bold text-dark py-2">${v.name}</td>
                                        <td class="text-center py-2 text-muted" style="font-size: 0.85rem;"><i class="fas fa-arrow-trend-up mr-1"></i>${trendRate}%</td>
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
                            
                            tdPesimista.html(`<input type="number" step="0.01" class="form-control form-control-sm input-pesimista text-center mx-auto" style="width: 70px; font-size: 0.8rem; padding: 2px;" value="${valPesimista}">`);
                            tdBase.html(`<input type="number" step="0.01" class="form-control form-control-sm input-base text-center mx-auto" style="width: 70px; font-size: 0.8rem; padding: 2px;" value="${valBase}">`);
                            tdOptimista.html(`<input type="number" step="0.01" class="form-control form-control-sm input-optimista text-center mx-auto" style="width: 70px; font-size: 0.8rem; padding: 2px;" value="${valOptimista}">`);
                            
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
                                        const oldMcData = {};
                                        for (const ag in trendDatasetsByAgency) {
                                            oldMcData[ag] = {};
                                            trendDatasetsByAgency[ag].variables.forEach(vv => {
                                                if (vv.mc_data) oldMcData[ag][vv.id] = vv.mc_data;
                                            });
                                        }
                                        
                                        $.ajax({
                                            url: "{% url 'financial_planning:api_get_trend_data' plan.id %}",
                                            method: "GET",
                                            success: function(response) {
                                                if (response.status === 'success') {
                                                    trendLabels = response.labels;
                                                    trendDatasetsByAgency = response.datasets_by_agency;
                                                    histMonthsCount = response.hist_months;
                                                    
                                                    // Restore mc_data
                                                    for (const ag in oldMcData) {
                                                        if (trendDatasetsByAgency[ag]) {
                                                            trendDatasetsByAgency[ag].variables.forEach(vv => {
                                                                if (oldMcData[ag][vv.id]) {
                                                                    vv.mc_data = oldMcData[ag][vv.id];
                                                                }
                                                            });
                                                        }
                                                    }
                                                    
                                                    const cv = trendDatasetsByAgency[currentAgency]?.variables.find(v => v.id === currentVariable);
                                                    mcDataObj = cv ? (cv.mc_data || null) : null;
                                                    
                                                    updateDashboard();
                                                }
                                            }
                                        });
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
                            window.renderMonthlyTable = renderMonthlyTable;
                            window.recalculateYieldSimulation = function() {
                                renderMonthlyTable(currentAgency, currentVariable, currentPeriod);
                            };

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

                            // Yield Simulation for Cartera
                            const yieldContainer = $('#yield-simulation-container');
                            if (v.id.toLowerCase().includes('cartera')) {
                                yieldContainer.show();
                                
                                if (!window.yieldParams) window.yieldParams = {};
                                const isNewVarForYield = (window.lastYieldVarId !== currentVariable);
                                window.lastYieldVarId = currentVariable;

                                const parseInput = (id, def) => {
                                    if (isNewVarForYield) {
                                        return window.yieldParams[currentVariable]?.[id] !== undefined ? window.yieldParams[currentVariable][id] : def;
                                    }
                                    const val = $(id).val();
                                    const parsed = val ? parseFloat(val.toString().replace(/,/g, '')) : NaN;
                                    const finalVal = !isNaN(parsed) ? parsed : def;
                                    
                                    if (!window.yieldParams[currentVariable]) window.yieldParams[currentVariable] = {};
                                    window.yieldParams[currentVariable][id] = finalVal;
                                    return finalVal;
                                };

                                let defYieldVigente = 65164885.0;
                                if (v.hist && v.hist.length > 0) {
                                    defYieldVigente = v.hist[v.hist.length - 1];
                                } else if (v.base && v.base.length > 0) {
                                    defYieldVigente = v.base[0];
                                }

                                const oldVigenteVal = parseInput('#yield-old-vigente', defYieldVigente);
                                const oldIngresosVal = parseInput('#yield-old-ingresos', 10793241.0);
                                const amortRate = parseInput('#yield-amort-rate', 5.0);
                                const pctVigente = parseInput('#yield-pct-vigente', 95.0);
                                const rateNew = parseInput('#yield-rate-new', 32.0);
                                
                                const rateActual = oldVigenteVal > 0 ? (oldIngresosVal / oldVigenteVal) * 100 : 0;
                                
                                const fmtInp = (v) => v.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
                                const onBlurFmt = "this.value = parseFloat(this.value.replace(/,/g, '') || 0).toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})";
                                
                                let yieldHtml = `
                                    <h6 class="font-weight-bold text-indigo text-uppercase mb-3">
                                        <i class="fas fa-chart-line mr-2"></i> Simulación de Rendimiento (Ingresos Financieros)
                                    </h6>
                                    <div class="d-flex flex-wrap align-items-end mb-3" style="gap: 15px;">
                                        <div style="width: 160px;">
                                            <label class="font-weight-bold text-muted small" title="Cartera Vigente al Cierre del Año Anterior">Cartera Vig. (Año Base)</label>
                                            <input type="text" id="yield-old-vigente" class="form-control form-control-sm text-right font-weight-bold text-secondary" value="${fmtInp(oldVigenteVal)}" onblur="${onBlurFmt}">
                                        </div>
                                        <div style="width: 160px;">
                                            <label class="font-weight-bold text-muted small" title="Ingresos Financieros del Año Anterior">Ingresos (Año Base)</label>
                                            <input type="text" id="yield-old-ingresos" class="form-control form-control-sm text-right font-weight-bold text-secondary" value="${fmtInp(oldIngresosVal)}" onblur="${onBlurFmt}">
                                        </div>
                                        <div style="width: 140px;">
                                            <label class="font-weight-bold text-muted small" title="Tasa Promedio Actual Anual Calculada">Tasa Histórica</label>
                                            <div class="input-group input-group-sm">
                                                <input type="text" class="form-control bg-light text-right font-weight-bold text-secondary" value="${rateActual.toFixed(2)}" readonly>
                                                <div class="input-group-append"><span class="input-group-text">%</span></div>
                                            </div>
                                        </div>
                                        <div style="width: 140px;">
                                            <label class="font-weight-bold text-muted small" title="Tasa de Amortización Mensual de la Cartera del Año Base">% Amort. Mensual</label>
                                            <div class="input-group input-group-sm">
                                                <input type="text" id="yield-amort-rate" class="form-control text-right font-weight-bold text-secondary" value="${fmtInp(amortRate)}" onblur="${onBlurFmt}">
                                                <div class="input-group-append"><span class="input-group-text">%</span></div>
                                            </div>
                                        </div>
                                        <div style="width: 140px;">
                                            <label class="font-weight-bold text-muted small">Tasa Nueva Cartera</label>
                                            <div class="input-group input-group-sm">
                                                <input type="text" id="yield-rate-new" class="form-control text-right font-weight-bold text-info" value="${fmtInp(rateNew)}" onblur="${onBlurFmt}">
                                                <div class="input-group-append"><span class="input-group-text">%</span></div>
                                            </div>
                                        </div>
                                        <div style="width: 140px;">
                                            <label class="font-weight-bold text-muted small">% Vigente s/ Total</label>
                                            <div class="input-group input-group-sm">
                                                <input type="text" id="yield-pct-vigente" class="form-control text-right font-weight-bold text-secondary" value="${fmtInp(pctVigente)}" onblur="${onBlurFmt}">
                                                <div class="input-group-append"><span class="input-group-text">%</span></div>
                                            </div>
                                        </div>
                                        <div class="w-100 mt-2"></div>
                                        <div class="col-12 px-0">
                                            <button type="button" class="btn btn-sm btn-indigo shadow-sm text-white px-4" onclick="recalculateYieldSimulation()" style="background-color: #6610f2;">
                                                <i class="fas fa-calculator mr-1"></i> Calcular Escenarios
                                            </button>
                                        </div>
                                    </div>
                                    <div class="row">
                                        <div class="col-xl-8">
                                            <div class="table-responsive">
                                                <table class="table table-bordered table-sm m-0 w-100" style="font-size: 0.8rem;">
                                                    <thead class="text-white" style="background-color: #6610f2;">
                                                        <tr>
                                                            <th class="font-weight-bold align-middle" rowspan="2" style="min-width: 120px;">Mes</th>
                                                            <th class="text-center font-weight-bold" colspan="2" style="border-bottom: 1px solid rgba(255,255,255,0.2);">Saldos Vigentes (Base)</th>
                                                            <th class="text-center font-weight-bold" colspan="2" style="border-bottom: 1px solid rgba(255,255,255,0.2);">Rendimiento Separado (Base)</th>
                                                            <th class="text-center font-weight-bold" colspan="3" style="border-bottom: 1px solid rgba(255,255,255,0.2);">Rendimiento Total</th>
                                                        </tr>
                                                        <tr>
                                                            <th class="text-right font-weight-bold" style="min-width: 120px; background-color: rgba(0,0,0,0.1);">Cartera Año Base</th>
                                                            <th class="text-right font-weight-bold" style="min-width: 120px; background-color: rgba(0,0,0,0.1);">Nueva Cartera</th>
                                                            <th class="text-right font-weight-bold" style="min-width: 120px; background-color: rgba(0,0,0,0.1);">Rend. Año Base</th>
                                                            <th class="text-right font-weight-bold" style="min-width: 120px; background-color: rgba(0,0,0,0.1);">Rend. Nueva</th>
                                                            <th class="text-right font-weight-bold" style="min-width: 120px; background-color: rgba(0,0,0,0.1);">Pesimista</th>
                                                            <th class="text-right font-weight-bold" style="min-width: 120px; background-color: rgba(0,0,0,0.1);">Base</th>
                                                            <th class="text-right font-weight-bold" style="min-width: 120px; background-color: rgba(0,0,0,0.1);">Optimista</th>
                                                        </tr>
                                                    </thead>
                                                    <tbody>
                                `;

                                const getSeparation = (total, monthIndex) => {
                                    const vigente = (total || 0) * (pctVigente / 100);
                                    let currentOldVigente = oldVigenteVal * Math.pow(1 - (amortRate / 100), monthIndex);
                                    
                                    let oldPort = 0;
                                    let newPort = 0;
                                    let yieldOld = 0;
                                    let yieldNew = 0;
                                    
                                    if (vigente > currentOldVigente) {
                                        oldPort = currentOldVigente;
                                        newPort = vigente - currentOldVigente;
                                    } else {
                                        oldPort = vigente;
                                        newPort = 0;
                                    }
                                    
                                    yieldOld = oldPort * (rateActual / 100) / 12;
                                    yieldNew = newPort * (rateNew / 100) / 12;
                                    
                                    return { oldPort, newPort, yieldOld, yieldNew, totalYield: yieldOld + yieldNew };
                                };

                                let sumYieldOld = 0;
                                let sumYieldNew = 0;
                                let sumTotalPes = 0;
                                let sumTotalBase = 0;
                                let sumTotalOpt = 0;

                                const formatVal = (val) => {
                                    return 'S/ ' + val.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
                                };

                                for (let i = 0; i < numRows; i++) {
                                    const idx = startIdx + i;
                                    const lbl = trendLabels[histMonthsCount + i] || `Mes ${i+1}`;

                                    const sepBase = getSeparation(v.base[idx], i);
                                    const totalPes = getSeparation(v.pesimista[idx], i).totalYield;
                                    const totalOpt = getSeparation(v.optimista[idx], i).totalYield;

                                    sumYieldOld += sepBase.yieldOld;
                                    sumYieldNew += sepBase.yieldNew;
                                    sumTotalPes += totalPes;
                                    sumTotalBase += sepBase.totalYield;
                                    sumTotalOpt += totalOpt;

                                    yieldHtml += `<tr>
                                        <td class="font-weight-bold text-dark bg-light">${lbl}</td>
                                        <td class="text-right text-secondary">${formatVal(sepBase.oldPort)}</td>
                                        <td class="text-right text-info">${formatVal(sepBase.newPort)}</td>
                                        <td class="text-right text-secondary">${formatVal(sepBase.yieldOld)}</td>
                                        <td class="text-right text-info">${formatVal(sepBase.yieldNew)}</td>
                                        <td class="text-right text-danger">${formatVal(totalPes)}</td>
                                        <td class="text-right font-weight-bold text-primary">${formatVal(sepBase.totalYield)}</td>
                                        <td class="text-right text-success">${formatVal(totalOpt)}</td>
                                    </tr>`;
                                }
                                yieldHtml += `
                                    <tr style="background-color: #e9ecef;">
                                        <td class="font-weight-bold text-dark text-right text-uppercase" colspan="3" style="letter-spacing: 0.5px;">Ingreso Total del Año:</td>
                                        <td class="text-right font-weight-bold text-secondary">${formatVal(sumYieldOld)}</td>
                                        <td class="text-right font-weight-bold text-info">${formatVal(sumYieldNew)}</td>
                                        <td class="text-right font-weight-bold text-danger">${formatVal(sumTotalPes)}</td>
                                        <td class="text-right font-weight-bold text-primary" style="font-size: 0.95rem;">${formatVal(sumTotalBase)}</td>
                                        <td class="text-right font-weight-bold text-success">${formatVal(sumTotalOpt)}</td>
                                    </tr>
                                            </tbody>
                                        </table>
                                    </div>`;
                                
                                if (showMCCols && mcDataObj) {
                                    let sumMcYieldOld = 0;
                                    let sumMcYieldNew = 0;
                                    let sumMcTotalPes = 0;
                                    let sumMcTotalBase = 0;
                                    let sumMcTotalOpt = 0;
                                    
                                    yieldHtml += `
                                    <div class="mt-4">
                                        <h6 class="font-weight-bold text-indigo mb-2" style="font-size: 0.85rem;"><i class="fas fa-dice mr-1"></i> Basado en Simulación Montecarlo</h6>
                                        <div class="table-responsive">
                                            <table class="table table-bordered table-sm m-0 w-100" style="font-size: 0.8rem;">
                                                <thead class="text-white" style="background-color: #e83e8c;">
                                                    <tr>
                                                        <th class="font-weight-bold align-middle" rowspan="2" style="min-width: 120px;">Mes</th>
                                                        <th class="text-center font-weight-bold" colspan="2" style="border-bottom: 1px solid rgba(255,255,255,0.2);">Saldos Vigentes (MC Base)</th>
                                                        <th class="text-center font-weight-bold" colspan="2" style="border-bottom: 1px solid rgba(255,255,255,0.2);">Rendimiento Separado (MC Base)</th>
                                                        <th class="text-center font-weight-bold" colspan="3" style="border-bottom: 1px solid rgba(255,255,255,0.2);">Rendimiento Total (Montecarlo)</th>
                                                    </tr>
                                                    <tr>
                                                        <th class="text-right font-weight-bold" style="min-width: 120px; background-color: rgba(0,0,0,0.1);">Cartera Año Base</th>
                                                        <th class="text-right font-weight-bold" style="min-width: 120px; background-color: rgba(0,0,0,0.1);">Nueva Cartera</th>
                                                        <th class="text-right font-weight-bold" style="min-width: 120px; background-color: rgba(0,0,0,0.1);">Rend. Año Base</th>
                                                        <th class="text-right font-weight-bold" style="min-width: 120px; background-color: rgba(0,0,0,0.1);">Rend. Nueva</th>
                                                        <th class="text-right font-weight-bold" style="min-width: 120px; background-color: rgba(0,0,0,0.1);">MC Pesimista</th>
                                                        <th class="text-right font-weight-bold" style="min-width: 120px; background-color: rgba(0,0,0,0.1);">MC Base</th>
                                                        <th class="text-right font-weight-bold" style="min-width: 120px; background-color: rgba(0,0,0,0.1);">MC Optimista</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                    `;
                                    
                                    for (let i = 0; i < numRows; i++) {
                                        const lbl = trendLabels[histMonthsCount + i] || `Mes ${i+1}`;

                                        const sepBase = getSeparation(mcDataObj.base[i], i);
                                        const totalPes = getSeparation(mcDataObj.pesimista[i], i).totalYield;
                                        const totalOpt = getSeparation(mcDataObj.optimista[i], i).totalYield;

                                        sumMcYieldOld += sepBase.yieldOld;
                                        sumMcYieldNew += sepBase.yieldNew;
                                        sumMcTotalPes += totalPes;
                                        sumMcTotalBase += sepBase.totalYield;
                                        sumMcTotalOpt += totalOpt;

                                        yieldHtml += `<tr>
                                            <td class="font-weight-bold text-dark bg-light">${lbl}</td>
                                            <td class="text-right text-secondary">${formatVal(sepBase.oldPort)}</td>
                                            <td class="text-right text-info">${formatVal(sepBase.newPort)}</td>
                                            <td class="text-right text-secondary">${formatVal(sepBase.yieldOld)}</td>
                                            <td class="text-right text-info">${formatVal(sepBase.yieldNew)}</td>
                                            <td class="text-right text-danger">${formatVal(totalPes)}</td>
                                            <td class="text-right font-weight-bold" style="color: #e83e8c;">${formatVal(sepBase.totalYield)}</td>
                                            <td class="text-right text-success">${formatVal(totalOpt)}</td>
                                        </tr>`;
                                    }
                                    
                                    yieldHtml += `
                                                    <tr style="background-color: #e9ecef;">
                                                        <td class="font-weight-bold text-dark text-right text-uppercase" colspan="3" style="letter-spacing: 0.5px;">Ingreso Total del Año (MC):</td>
                                                        <td class="text-right font-weight-bold text-secondary">${formatVal(sumMcYieldOld)}</td>
                                                        <td class="text-right font-weight-bold text-info">${formatVal(sumMcYieldNew)}</td>
                                                        <td class="text-right font-weight-bold text-danger">${formatVal(sumMcTotalPes)}</td>
                                                        <td class="text-right font-weight-bold" style="font-size: 0.95rem; color: #e83e8c;">${formatVal(sumMcTotalBase)}</td>
                                                        <td class="text-right font-weight-bold text-success">${formatVal(sumMcTotalOpt)}</td>
                                                    </tr>
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>`;
                                }
                                
                                yieldHtml += `
                                    </div>
                                </div>
                                <div class="col-xl-4">
                                    <div class="alert alert-info shadow-sm border-0 h-100 mb-0" style="font-size: 0.85rem; border-left: 4px solid #17a2b8 !important;">
                                        <h6 class="font-weight-bold text-info mb-3"><i class="fas fa-info-circle mr-1"></i> Metodología de Cálculo</h6>
                                        <p class="mb-3">El modelo proyecta los ingresos financieros separando el portafolio proyectado en dos tramos para mayor precisión analítica:</p>
                                        <ul class="pl-3 mb-3" style="line-height: 1.5;">
                                            <li class="mb-2"><strong>Tramo Año Base:</strong> Se asume que el saldo vigente al cierre del año anterior se mantiene y rinde a la <span class="badge badge-light text-muted border border-secondary">Tasa Histórica</span> (derivada de la relación entre sus propios ingresos y saldo final).</li>
                                            <li><strong>Tramo Nuevo:</strong> Todo saldo proyectado que <em>exceda</em> la Cartera del Año Base se considera como nueva colocación neta. Este diferencial genera ingresos bajo la <span class="badge badge-light text-muted border border-secondary">Tasa Nueva Cartera</span>.</li>
                                        </ul>
                                        <p class="mb-0 text-muted small">
                                            <strong>Nota:</strong> Los rendimientos se calculan aplicando las tasas anualmente sobre las porciones de saldo correspondientes, las cuales se ajustan primero descontando la mora proyectada definida en <em>% Vigente s/ Total</em>.
                                        </p>
                                    </div>
                                </div>
                                </div>`;
                                yieldContainer.html(yieldHtml);

                            } else {
                                yieldContainer.hide();
                            }

                            // Cost Simulation for Obligaciones
                            const costContainer = $('#cost-simulation-container');
                            const varNameLower = v.name ? v.name.toLowerCase() : '';
                            const varIdLower = v.id ? v.id.toLowerCase() : '';
                            if (varIdLower.includes('obligacion') || varNameLower.includes('obligacion') || varNameLower.includes('ahorro') || varNameLower.includes('deposito') || varNameLower.includes('depósito') || varNameLower.includes('plazo') || varIdLower.startsWith('21')) {
                                costContainer.show();
                                
                                if (!window.costParams) window.costParams = {};
                                const isNewVarForCost = (window.lastCostVarId !== currentVariable);
                                window.lastCostVarId = currentVariable;

                                const parseInput = (id, def) => {
                                    if (isNewVarForCost) {
                                        return window.costParams[currentVariable]?.[id] !== undefined ? window.costParams[currentVariable][id] : def;
                                    }
                                    const val = $(id).val();
                                    const parsed = val ? parseFloat(val.toString().replace(/,/g, '')) : NaN;
                                    const finalVal = !isNaN(parsed) ? parsed : def;
                                    
                                    if (!window.costParams[currentVariable]) window.costParams[currentVariable] = {};
                                    window.costParams[currentVariable][id] = finalVal;
                                    return finalVal;
                                };

                                let defCostVigente = 63933556.0;
                                if (v.hist && v.hist.length > 0) {
                                    defCostVigente = v.hist[v.hist.length - 1];
                                } else if (v.base && v.base.length > 0) {
                                    defCostVigente = v.base[0];
                                }
                                
                                let defCostGastos = 4500000.0;
                                let defCostNew = 8.0;

                                if (varNameLower.includes('ahorro') || varIdLower === '2101') {
                                    defCostGastos = 657769.0;
                                    defCostNew = 5.0; // Estimate
                                } else if (varNameLower.includes('plazo') || varIdLower === '2103') {
                                    defCostGastos = 4396022.0;
                                    defCostNew = 7.5; // Estimate
                                }

                                const oldVigenteCostVal = parseInput('#cost-old-vigente', defCostVigente);
                                const oldGastosVal = parseInput('#cost-old-gastos', defCostGastos);
                                const amortCostRate = parseInput('#cost-amort-rate', 5.0);
                                const pctCostVigente = parseInput('#cost-pct-vigente', 100.0);
                                const rateCostNew = parseInput('#cost-rate-new', defCostNew);
                                
                                const rateCostActual = oldVigenteCostVal > 0 ? (oldGastosVal / oldVigenteCostVal) * 100 : 0;
                                
                                const fmtInp = (v) => v.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
                                const onBlurFmt = "this.value = parseFloat(this.value.replace(/,/g, '') || 0).toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})";
                                
                                let costHtml = `
                                    <h6 class="font-weight-bold text-danger text-uppercase mb-3">
                                        <i class="fas fa-file-invoice-dollar mr-2"></i> Simulación de Gastos Financieros (Obligaciones)
                                    </h6>
                                    <div class="d-flex flex-wrap align-items-end mb-3" style="gap: 15px;">
                                        <div style="width: 160px;">
                                            <label class="font-weight-bold text-muted small" title="Obligaciones al Cierre del Año Anterior">Obligaciones (Año Base)</label>
                                            <input type="text" id="cost-old-vigente" class="form-control form-control-sm text-right font-weight-bold text-secondary" value="${fmtInp(oldVigenteCostVal)}" onblur="${onBlurFmt}">
                                        </div>
                                        <div style="width: 160px;">
                                            <label class="font-weight-bold text-muted small" title="Gastos Financieros del Año Anterior">Gastos (Año Base)</label>
                                            <input type="text" id="cost-old-gastos" class="form-control form-control-sm text-right font-weight-bold text-secondary" value="${fmtInp(oldGastosVal)}" onblur="${onBlurFmt}">
                                        </div>
                                        <div style="width: 140px;">
                                            <label class="font-weight-bold text-muted small" title="Tasa Promedio Actual Anual Calculada">Tasa Histórica</label>
                                            <div class="input-group input-group-sm">
                                                <input type="text" class="form-control bg-light text-right font-weight-bold text-secondary" value="${rateCostActual.toFixed(2)}" readonly>
                                                <div class="input-group-append"><span class="input-group-text">%</span></div>
                                            </div>
                                        </div>
                                        <div style="width: 140px;">
                                            <label class="font-weight-bold text-muted small" title="Tasa de Retiros/Cancelación Mensual">% Retiros Mensual</label>
                                            <div class="input-group input-group-sm">
                                                <input type="text" id="cost-amort-rate" class="form-control text-right font-weight-bold text-secondary" value="${fmtInp(amortCostRate)}" onblur="${onBlurFmt}">
                                                <div class="input-group-append"><span class="input-group-text">%</span></div>
                                            </div>
                                        </div>
                                        <div style="width: 140px;">
                                            <label class="font-weight-bold text-muted small">Tasa Nuevas Obli.</label>
                                            <div class="input-group input-group-sm">
                                                <input type="text" id="cost-rate-new" class="form-control text-right font-weight-bold text-info" value="${fmtInp(rateCostNew)}" onblur="${onBlurFmt}">
                                                <div class="input-group-append"><span class="input-group-text">%</span></div>
                                            </div>
                                        </div>
                                        <div style="width: 140px;">
                                            <label class="font-weight-bold text-muted small">% Efectivo s/ Total</label>
                                            <div class="input-group input-group-sm">
                                                <input type="text" id="cost-pct-vigente" class="form-control text-right font-weight-bold text-secondary" value="${fmtInp(pctCostVigente)}" onblur="${onBlurFmt}">
                                                <div class="input-group-append"><span class="input-group-text">%</span></div>
                                            </div>
                                        </div>
                                        <div class="w-100 mt-2"></div>
                                        <div class="col-12 px-0">
                                            <button type="button" class="btn btn-sm btn-danger shadow-sm text-white px-4" onclick="recalculateYieldSimulation()" style="background-color: #dc3545;">
                                                <i class="fas fa-calculator mr-1"></i> Calcular Escenarios
                                            </button>
                                        </div>
                                    </div>
                                    <div class="row">
                                        <div class="col-xl-8">
                                            <div class="table-responsive">
                                                <table class="table table-bordered table-sm m-0 w-100" style="font-size: 0.8rem;">
                                                    <thead class="text-white" style="background-color: #dc3545;">
                                                        <tr>
                                                            <th class="font-weight-bold align-middle" rowspan="2" style="min-width: 120px;">Mes</th>
                                                            <th class="text-center font-weight-bold" colspan="2" style="border-bottom: 1px solid rgba(255,255,255,0.2);">Saldos Vigentes (Base)</th>
                                                            <th class="text-center font-weight-bold" colspan="2" style="border-bottom: 1px solid rgba(255,255,255,0.2);">Gasto Separado (Base)</th>
                                                            <th class="text-center font-weight-bold" colspan="3" style="border-bottom: 1px solid rgba(255,255,255,0.2);">Gasto Total</th>
                                                        </tr>
                                                        <tr>
                                                            <th class="text-right font-weight-bold" style="min-width: 120px; background-color: rgba(0,0,0,0.1);">Obli. Año Base</th>
                                                            <th class="text-right font-weight-bold" style="min-width: 120px; background-color: rgba(0,0,0,0.1);">Nuevas Obli.</th>
                                                            <th class="text-right font-weight-bold" style="min-width: 120px; background-color: rgba(0,0,0,0.1);">Gasto Año Base</th>
                                                            <th class="text-right font-weight-bold" style="min-width: 120px; background-color: rgba(0,0,0,0.1);">Gasto Nuevas</th>
                                                            <th class="text-right font-weight-bold" style="min-width: 120px; background-color: rgba(0,0,0,0.1);">Pesimista</th>
                                                            <th class="text-right font-weight-bold" style="min-width: 120px; background-color: rgba(0,0,0,0.1);">Base</th>
                                                            <th class="text-right font-weight-bold" style="min-width: 120px; background-color: rgba(0,0,0,0.1);">Optimista</th>
                                                        </tr>
                                                    </thead>
                                                    <tbody>
                                `;

                                const getCostSeparation = (total, monthIndex) => {
                                    const vigente = (total || 0) * (pctCostVigente / 100);
                                    let currentOldVigente = oldVigenteCostVal * Math.pow(1 - (amortCostRate / 100), monthIndex);
                                    
                                    let oldPort = 0;
                                    let newPort = 0;
                                    let costOld = 0;
                                    let costNew = 0;
                                    
                                    if (vigente > currentOldVigente) {
                                        oldPort = currentOldVigente;
                                        newPort = vigente - currentOldVigente;
                                    } else {
                                        oldPort = vigente;
                                        newPort = 0;
                                    }
                                    
                                    costOld = oldPort * (rateCostActual / 100) / 12;
                                    costNew = newPort * (rateCostNew / 100) / 12;
                                    
                                    return { oldPort, newPort, costOld, costNew, totalCost: costOld + costNew };
                                };

                                let sumCostOld = 0;
                                let sumCostNew = 0;
                                let sumTotalPes = 0;
                                let sumTotalBase = 0;
                                let sumTotalOpt = 0;

                                const formatVal = (val) => {
                                    return 'S/ ' + val.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
                                };

                                for (let i = 0; i < numRows; i++) {
                                    const idx = startIdx + i;
                                    const lbl = trendLabels[histMonthsCount + i] || `Mes ${i+1}`;

                                    const sepBase = getCostSeparation(v.base[idx], i);
                                    const totalPes = getCostSeparation(v.pesimista[idx], i).totalCost;
                                    const totalOpt = getCostSeparation(v.optimista[idx], i).totalCost;

                                    sumCostOld += sepBase.costOld;
                                    sumCostNew += sepBase.costNew;
                                    sumTotalPes += totalPes;
                                    sumTotalBase += sepBase.totalCost;
                                    sumTotalOpt += totalOpt;

                                    costHtml += `<tr>
                                        <td class="font-weight-bold text-dark bg-light">${lbl}</td>
                                        <td class="text-right text-secondary">${formatVal(sepBase.oldPort)}</td>
                                        <td class="text-right text-info">${formatVal(sepBase.newPort)}</td>
                                        <td class="text-right text-secondary">${formatVal(sepBase.costOld)}</td>
                                        <td class="text-right text-info">${formatVal(sepBase.costNew)}</td>
                                        <td class="text-right text-danger">${formatVal(totalPes)}</td>
                                        <td class="text-right font-weight-bold text-primary">${formatVal(sepBase.totalCost)}</td>
                                        <td class="text-right text-success">${formatVal(totalOpt)}</td>
                                    </tr>`;
                                }
                                costHtml += `
                                    <tr style="background-color: #e9ecef;">
                                        <td class="font-weight-bold text-dark text-right text-uppercase" colspan="3" style="letter-spacing: 0.5px;">Gasto Total del Año:</td>
                                        <td class="text-right font-weight-bold text-secondary">${formatVal(sumCostOld)}</td>
                                        <td class="text-right font-weight-bold text-info">${formatVal(sumCostNew)}</td>
                                        <td class="text-right font-weight-bold text-danger">${formatVal(sumTotalPes)}</td>
                                        <td class="text-right font-weight-bold text-primary" style="font-size: 0.95rem;">${formatVal(sumTotalBase)}</td>
                                        <td class="text-right font-weight-bold text-success">${formatVal(sumTotalOpt)}</td>
                                    </tr>
                                            </tbody>
                                        </table>
                                    </div>`;
                                
                                if (showMCCols && mcDataObj) {
                                    let sumMcCostOld = 0;
                                    let sumMcCostNew = 0;
                                    let sumMcTotalPes = 0;
                                    let sumMcTotalBase = 0;
                                    let sumMcTotalOpt = 0;
                                    
                                    costHtml += `
                                    <div class="mt-4">
                                        <h6 class="font-weight-bold text-danger mb-2" style="font-size: 0.85rem;"><i class="fas fa-dice mr-1"></i> Basado en Simulación Montecarlo</h6>
                                        <div class="table-responsive">
                                            <table class="table table-bordered table-sm m-0 w-100" style="font-size: 0.8rem;">
                                                <thead class="text-white" style="background-color: #e83e8c;">
                                                    <tr>
                                                        <th class="font-weight-bold align-middle" rowspan="2" style="min-width: 120px;">Mes</th>
                                                        <th class="text-center font-weight-bold" colspan="2" style="border-bottom: 1px solid rgba(255,255,255,0.2);">Saldos Vigentes (MC Base)</th>
                                                        <th class="text-center font-weight-bold" colspan="2" style="border-bottom: 1px solid rgba(255,255,255,0.2);">Gasto Separado (MC Base)</th>
                                                        <th class="text-center font-weight-bold" colspan="3" style="border-bottom: 1px solid rgba(255,255,255,0.2);">Gasto Total (Montecarlo)</th>
                                                    </tr>
                                                    <tr>
                                                        <th class="text-right font-weight-bold" style="min-width: 120px; background-color: rgba(0,0,0,0.1);">Obli. Año Base</th>
                                                        <th class="text-right font-weight-bold" style="min-width: 120px; background-color: rgba(0,0,0,0.1);">Nuevas Obli.</th>
                                                        <th class="text-right font-weight-bold" style="min-width: 120px; background-color: rgba(0,0,0,0.1);">Gasto Año Base</th>
                                                        <th class="text-right font-weight-bold" style="min-width: 120px; background-color: rgba(0,0,0,0.1);">Gasto Nuevas</th>
                                                        <th class="text-right font-weight-bold" style="min-width: 120px; background-color: rgba(0,0,0,0.1);">MC Pesimista</th>
                                                        <th class="text-right font-weight-bold" style="min-width: 120px; background-color: rgba(0,0,0,0.1);">MC Base</th>
                                                        <th class="text-right font-weight-bold" style="min-width: 120px; background-color: rgba(0,0,0,0.1);">MC Optimista</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                    `;
                                    
                                    for (let i = 0; i < numRows; i++) {
                                        const lbl = trendLabels[histMonthsCount + i] || `Mes ${i+1}`;

                                        const sepBase = getCostSeparation(mcDataObj.base[i], i);
                                        const totalPes = getCostSeparation(mcDataObj.pesimista[i], i).totalCost;
                                        const totalOpt = getCostSeparation(mcDataObj.optimista[i], i).totalCost;

                                        sumMcCostOld += sepBase.costOld;
                                        sumMcCostNew += sepBase.costNew;
                                        sumMcTotalPes += totalPes;
                                        sumMcTotalBase += sepBase.totalCost;
                                        sumMcTotalOpt += totalOpt;

                                        costHtml += `<tr>
                                            <td class="font-weight-bold text-dark bg-light">${lbl}</td>
                                            <td class="text-right text-secondary">${formatVal(sepBase.oldPort)}</td>
                                            <td class="text-right text-info">${formatVal(sepBase.newPort)}</td>
                                            <td class="text-right text-secondary">${formatVal(sepBase.costOld)}</td>
                                            <td class="text-right text-info">${formatVal(sepBase.costNew)}</td>
                                            <td class="text-right text-danger">${formatVal(totalPes)}</td>
                                            <td class="text-right font-weight-bold" style="color: #e83e8c;">${formatVal(sepBase.totalCost)}</td>
                                            <td class="text-right text-success">${formatVal(totalOpt)}</td>
                                        </tr>`;
                                    }
                                    
                                    costHtml += `
                                                    <tr style="background-color: #e9ecef;">
                                                        <td class="font-weight-bold text-dark text-right text-uppercase" colspan="3" style="letter-spacing: 0.5px;">Gasto Total del Año (MC):</td>
                                                        <td class="text-right font-weight-bold text-secondary">${formatVal(sumMcCostOld)}</td>
                                                        <td class="text-right font-weight-bold text-info">${formatVal(sumMcCostNew)}</td>
                                                        <td class="text-right font-weight-bold text-danger">${formatVal(sumMcTotalPes)}</td>
                                                        <td class="text-right font-weight-bold" style="font-size: 0.95rem; color: #e83e8c;">${formatVal(sumMcTotalBase)}</td>
                                                        <td class="text-right font-weight-bold text-success">${formatVal(sumMcTotalOpt)}</td>
                                                    </tr>
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>`;
                                }
                                
                                costHtml += `
                                    </div>
                                </div>
                                <div class="col-xl-4">
                                    <div class="alert alert-danger shadow-sm border-0 h-100 mb-0" style="font-size: 0.85rem; border-left: 4px solid #dc3545 !important;">
                                        <h6 class="font-weight-bold text-danger mb-3"><i class="fas fa-info-circle mr-1"></i> Metodología de Cálculo</h6>
                                        <p class="mb-3">El modelo proyecta los gastos financieros por obligaciones separando el saldo proyectado en dos tramos:</p>
                                        <ul class="pl-3 mb-3" style="line-height: 1.5;">
                                            <li class="mb-2"><strong>Tramo Año Base:</strong> Se asume que el saldo de obligaciones al cierre del año anterior se amortiza gradualmente (según el <span class="badge badge-light text-muted border border-secondary">% Retiros Mensual</span>) y cuesta a la <span class="badge badge-light text-muted border border-secondary">Tasa Histórica</span> (derivada de la relación entre sus propios gastos y saldo final).</li>
                                            <li><strong>Tramo Nuevo:</strong> Todo saldo proyectado que <em>exceda</em> las Obligaciones del Año Base se considera nueva captación. Este diferencial genera gastos bajo la <span class="badge badge-light text-muted border border-secondary">Tasa Nuevas Obli.</span></li>
                                        </ul>
                                        <p class="mb-0 text-muted small">
                                            <strong>Nota:</strong> Los gastos se calculan aplicando las tasas anualmente sobre las porciones de saldo correspondientes.
                                        </p>
                                    </div>
                                </div>
                                </div>`;
                                costContainer.html(costHtml);
                                
                            } else {
                                costContainer.hide();
                            }
                            
                            updateLockUI();
                        }
                        
                        currentAgency = selectAgency.val();
                        updateVariablesUI(currentAgency);
                        
                        if (response.ui_state) {
                            $('#chart-mode-group .btn').removeClass('active');
                            $(`#chart-mode-group .btn[data-mode="${chartMode}"]`).addClass('active');
                            
                            $('.trend-period-btn').removeClass('active');
                            $(`.trend-period-btn[data-months="${currentPeriod}"]`).addClass('active');
                        }
                        
                        $('#trend-loading').hide();
                        $('#trend-chart-container').fadeIn();
                        
                        updateDashboard();
                        updateLockUI();
                        
                $('#btn-apply-trend').off('click').on('click', function() {
                    showTrendCols = !showTrendCols;
                    if (showTrendCols) {
                        if (mcDataObj) {
                            showMCCols = true;
                            chartMode = 'ambos';
                            $('#chart-mode-group .btn').removeClass('active');
                            $('#chart-mode-group .btn[data-mode="ambos"]').addClass('active');
                        } else {
                            showMCCols = false;
                            chartMode = 'tendencia';
                            $('#chart-mode-group .btn').removeClass('active');
                            $('#chart-mode-group .btn[data-mode="tendencia"]').addClass('active');
                        }
                    } else {
                        if (mcDataObj) {
                            chartMode = 'montecarlo';
                            $('#chart-mode-group .btn').removeClass('active');
                            $('#chart-mode-group .btn[data-mode="montecarlo"]').addClass('active');
                        }
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
                    
                    // Activate Ambos or Montecarlo Mode automatically for the animation
                    $('#chart-mode-group .btn').removeClass('active');
                    if (showTrendCols) {
                        $('#chart-mode-group .btn[data-mode="ambos"]').addClass('active');
                        chartMode = 'ambos';
                        showMCCols = true;
                    } else {
                        $('#chart-mode-group .btn[data-mode="montecarlo"]').addClass('active');
                        chartMode = 'montecarlo';
                        showMCCols = true;
                    }
                    
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
                            variable_id: v.id,
                            base_rate: v.rates && v.rates.base ? parseFloat(v.rates.base) / 100.0 : null
                        }),
                        headers: {
                            'X-CSRFToken': '{{ csrf_token }}'
                        },
                        success: function(res) {
                            clearInterval(animationInterval);
                            if(res.status === 'success') {
                                mcDataObj = res.data;
                                const vars = trendDatasetsByAgency[currentAgency].variables;
                                const v = vars.find(d => d.id === currentVariable);
                                if (v) v.mc_data = res.data;
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

    let styleBlock = document.getElementById('er-filter-style');
    if (!styleBlock) {
        styleBlock = document.createElement('style');
        styleBlock.id = 'er-filter-style';
        document.head.appendChild(styleBlock);
    }

    if (year === 'all') {
        styleBlock.innerHTML = '';
        return;
    }

    const table = document.getElementById('erTable');
    if (!table) return;

    const ths = table.querySelectorAll('thead th');
    let cssRules = '';

    ths.forEach((th, index) => {
        if (index === 0) return; // Always keep the first column (account names)

        const text = (th.textContent || "").trim();
        const colYear = text.split('-')[0];

        if (colYear !== String(year)) {
            // CSS nth-child is 1-indexed
            cssRules += `#erTable th:nth-child(${index + 1}), #erTable td:nth-child(${index + 1}) { display: none !important; }\n`;
        }
    });

    styleBlock.innerHTML = cssRules;
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

window.handleWizardContinue = function(url) {
    const doContinue = () => {
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                title: 'Guardado exitosamente',
                text: 'Avanzando al siguiente paso...',
                icon: 'success',
                timer: 1500,
                showConfirmButton: false
            }).then(() => {
                window.location.href = url;
            });
        } else {
            alert('Guardado exitosamente');
            window.location.href = url;
        }
    };

    if (window.costParams || window.yieldParams) {
        const payload = {};
        if (window.costParams) {
            payload.costParams = window.costParams;
        }
        if (window.yieldParams) {
            payload.yieldParams = window.yieldParams;
        }
        
        fetch(`{% url 'financial_planning:save_institutional_assumptions' plan.id %}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]') ? document.querySelector('[name=csrfmiddlewaretoken]').value : '{{ csrf_token }}'
            },
            body: JSON.stringify(payload)
        }).then(res => res.json())
          .then(data => {
              if (data.status === 'success') {
                  doContinue();
              } else {
                  console.error('Error saving assumptions:', data.message);
                  doContinue(); // continue anyway
              }
          })
          .catch(err => {
              console.error('Fetch error:', err);
              doContinue(); // continue anyway
          });
    } else {
        doContinue();
    }
};
