import re

with open(r'c:\Users\VICTUS\Desktop\A.RISK ERM\templates\financial_planning\wizard.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Inject the HTML section before the <script> tag (or just before step-7 ends)
html_section = '''
                        <!-- Montecarlo Comparative Section -->
                        <div class="card shadow-sm mb-4 border-warning" id="montecarlo-section" style="display: none;">
                            <div class="card-header bg-warning text-dark d-flex justify-content-between align-items-center">
                                <h5 class="m-0 font-weight-bold"><i class="fas fa-chart-line mr-2"></i> An&aacute;lisis Comparativo: Simulaci&oacute;n Montecarlo (2026)</h5>
                                <div>
                                    <button type="button" class="btn btn-sm btn-dark" onclick="$('#montecarlo-section').slideUp();">Ocultar</button>
                                </div>
                            </div>
                            <div class="card-body p-0">
                                <div class="table-responsive">
                                    <table class="table table-sm table-hover mb-0" style="font-size: 0.85rem;" id="montecarlo-summary-table">
                                        <thead class="bg-light text-dark">
                                            <tr>
                                                <th style="width: 300px;">Cuenta / Rubro</th>
                                                <th class="text-right">Variaci&oacute;n Tendencia</th>
                                                <th class="text-right text-danger">Var. Montecarlo (Pesimista)</th>
                                                <th class="text-right text-primary">Var. Montecarlo (Base)</th>
                                                <th class="text-right text-success">Var. Montecarlo (Optimista)</th>
                                                <th class="text-center">Acci&oacute;n</th>
                                            </tr>
                                        </thead>
                                        <tbody id="montecarlo-summary-tbody">
                                            <tr><td colspan="6" class="text-center p-3 text-muted">Ejecute la Simulaci&oacute;n Montecarlo para ver los resultados...</td></tr>
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
'''

if 'id="montecarlo-section"' not in text:
    # insert before <script>
    match_script = re.search(r'<script>', text)
    if match_script:
        text = text[:match_script.start()] + html_section + text[match_script.start():]

# 2. Modify applyMontecarloTrend javascript function
js_code_new = '''
    function applyMontecarloTrend() {
        const btn = $('#btn-apply-montecarlo');
        const originalText = '<i class="fas fa-chart-line mr-1"></i> Simulaci&oacute;n Montecarlo';
        
        btn.html('<i class="fas fa-spinner fa-spin mr-1"></i> Procesando...').prop('disabled', true);
        
        const planId = '{{ plan.id }}';
        
        fetch(`/financial-planning/plan/${planId}/api/ml-montecarlo-projection/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'Content-Type': 'application/json'
            }
        })
        .then(async response => {
            if (!response.ok) {
                let errorMsg = 'Error en el servidor al calcular proyecciones Montecarlo';
                try {
                    const errData = await response.json();
                    if (errData.msg) errorMsg = errData.msg;
                } catch(e) {}
                throw new Error(errorMsg);
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'success') {
                const trends = data.trends;
                const tbody = $('#montecarlo-summary-tbody');
                tbody.empty();
                
                let count = 0;
                
                for (const code in window.accMap7) {
                    if (trends[code]) {
                        const node = window.accMap7[code];
                        const name = node.name;
                        // get current base variation for 2026
                        let currentVar = 0;
                        if(node.years && node.years['2026'] && node.years['2026'].scenarios && node.years['2026'].scenarios['base']) {
                            currentVar = node.years['2026'].scenarios['base'].val || 0;
                        }
                        
                        const m_pes = trends[code]['pesimista'].toFixed(2);
                        const m_base = trends[code]['base'].toFixed(2);
                        const m_opt = trends[code]['optimista'].toFixed(2);
                        
                        const rowHtml = `
                            <tr>
                                <td class="font-weight-bold">${code} - ${name}</td>
                                <td class="text-right">${Number(currentVar).toFixed(2)}%</td>
                                <td class="text-right text-danger font-weight-bold">${m_pes}%</td>
                                <td class="text-right text-primary font-weight-bold">${m_base}%</td>
                                <td class="text-right text-success font-weight-bold">${m_opt}%</td>
                                <td class="text-center">
                                    <button class="btn btn-xs btn-outline-primary" onclick="applyMontecarloToAccount('${code}', ${m_pes}, ${m_base}, ${m_opt})">
                                        Aplicar a Modelo Principal
                                    </button>
                                </td>
                            </tr>
                        `;
                        tbody.append(rowHtml);
                        count++;
                    }
                }
                
                if (count === 0) {
                    tbody.html('<tr><td colspan="6" class="text-center p-3 text-muted">No se pudieron generar simulaciones para las cuentas actuales.</td></tr>');
                }
                
                $('#montecarlo-section').slideDown();
                
                Swal.fire({
                    icon: 'success',
                    title: 'Simulaci&oacute;n Completada',
                    text: `Se calcularon ${count} cuentas usando Montecarlo. Revise la secci&oacute;n inferior para comparar.`,
                    timer: 3000,
                    showConfirmButton: false
                });
                
            } else {
                throw new Error(data.msg || 'Error al calcular');
            }
        })
        .catch(err => {
            console.error(err);
            Swal.fire('Error', err.message, 'error');
        })
        .finally(() => {
            btn.html(originalText).prop('disabled', false);
        });
    }

    window.applyMontecarloToAccount = function(code, pes, base, opt) {
        if(window.accMap7 && window.accMap7[code]) {
            let node = window.accMap7[code];
            if(!node.years['2026']) node.years['2026'] = {};
            if(!node.years['2026'].scenarios) node.years['2026'].scenarios = {};
            
            node.years['2026'].scenarios['pesimista'] = { type: 'pct', val: pes };
            node.years['2026'].scenarios['base'] = { type: 'pct', val: base };
            node.years['2026'].scenarios['optimista'] = { type: 'pct', val: opt };
            
            recalculateStep7();
            Swal.fire({
                icon: 'success',
                title: 'Aplicado',
                text: 'Los valores de Montecarlo han sido aplicados a la cuenta ' + code,
                timer: 2000,
                showConfirmButton: false
            });
            if(typeof window.saveAssumptionsFromStep7 === 'function'){
                window.saveAssumptionsFromStep7(document.getElementById('btnSaveAssumptionsTop'));
            }
        }
    };
'''

# Replace the existing function
match_js = re.search(r'function applyMontecarloTrend\(\) \{[\s\S]*?(?=function|</script>)', text)
if match_js:
    text = text[:match_js.start()] + js_code_new + text[match_js.end():]

with open(r'c:\Users\VICTUS\Desktop\A.RISK ERM\templates\financial_planning\wizard.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("Wizard.html patched with Montecarlo section!")
