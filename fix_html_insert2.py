import re

with open(r'c:\Users\VICTUS\Desktop\A.RISK ERM\templates\financial_planning\wizard.html', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.rfind('Guardar Supuestos')
if idx != -1:
    start = text.rfind('<div class="d-flex justify-content-center', 0, idx)
    if start != -1:
        html_section = '''
                        <!-- Montecarlo Comparative Section -->
                        <div class="card shadow-sm mb-4 border-warning mt-4" id="montecarlo-section" style="display: none;">
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
        text = text[:start] + html_section + '\n' + text[start:]
        with open(r'c:\Users\VICTUS\Desktop\A.RISK ERM\templates\financial_planning\wizard.html', 'w', encoding='utf-8') as f:
            f.write(text)
        print('Inserted successfully via python file')
    else:
        print('Div not found')
else:
    print('Guardar supuestos not found')
