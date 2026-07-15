import re

with open('templates/financial_planning/wizard.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Insert let chartMode = 'tendencia';
text = text.replace("let currentPeriod = 12;", "let currentPeriod = 12;\n        let chartMode = 'tendencia';")

# 2. Add event listeners for the chart-mode-group buttons inside the success callback of loadTrendData
# Let's put it right after updateDashboard() near line 1830

listeners_code = """
                        $('#chart-mode-group .btn').on('click', function() {
                            $('#chart-mode-group .btn').removeClass('active');
                            $(this).addClass('active');
                            chartMode = $(this).data('mode');
                            updateDashboard();
                        });
"""

text = text.replace("updateDashboard();\n\n                $('#btn-apply-trend')", "updateDashboard();\n" + listeners_code + "\n                $('#btn-apply-trend')")

# 3. Replace renderTrendChart implementation
new_render_trend_chart = """        function renderTrendChart(agencyId, variableId) {
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
        }"""

# Use regex to replace the old renderTrendChart function
pattern = re.compile(r'        function renderTrendChart\(agencyId, variableId\) \{.*?\n        \}\n', re.DOTALL)
text = pattern.sub(new_render_trend_chart + "\n", text)

with open('templates/financial_planning/wizard.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("Patch applied.")
