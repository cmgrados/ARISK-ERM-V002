with open('templates/financial_planning/wizard.html', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

replacement = '''                                    <button type="button" class="btn btn-sm btn-outline-info rounded-pill px-3 font-weight-bold shadow-sm mr-2 mb-2 mb-md-0" id="btn-apply-trend">
                                        <i class="fas fa-history mr-1"></i> Aplicar Tendencia Año Anterior
                                    </button>
                                    <div class="d-inline-flex align-items-center mr-2 mb-2 mb-md-0">
                                        <input type="number" id="mc-iterations" class="form-control form-control-sm border-secondary text-center mr-1" value="1000" style="width: 70px; border-radius: 20px;" title="Nº Iteraciones">
                                        <button type="button" class="btn btn-sm btn-outline-warning rounded-pill px-3 font-weight-bold shadow-sm" id="btn-run-mc">
                                            <i class="fas fa-random mr-1"></i> Montecarlo
                                        </button>
                                    </div>
                                    <a href="{% url 'financial_planning:export_trend_analysis_excel' plan.id %}" class="btn btn-sm btn-outline-success rounded-pill px-3 font-weight-bold shadow-sm" id="btn-export-trends">
                                        <i class="fas fa-file-excel mr-1"></i> Exportar
                                    </a>'''

if "btn-run-mc" not in text:
    import re
    text = re.sub(r'<button[^>]*id="btn-apply-trend".*?</button>\s*<a[^>]*id="btn-export-trends".*?</a>', replacement, text, flags=re.DOTALL)
    
    with open('templates/financial_planning/wizard.html', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Replaced")
else:
    print("Already modified")
