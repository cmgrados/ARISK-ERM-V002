import re

with open('templates/financial_planning/institutional_budget_wizard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Step 1: Same. Just rename step titles.
content = content.replace('Información General del Plan', 'Información General del Presupuesto Institucional')

# Extract the old Step 7 (which is Budget Base Viewer)
step7_match = re.search(r'<!-- STEP 7:.*?{% if step == 7 %}(.*?)<!-- STEP 8', content, re.DOTALL)
if step7_match:
    budget_base_content = step7_match.group(1).replace('{% endif %}\n\n                ', '')

# Extract old Step 5 (Supuestos)
step5_match = re.search(r'<!-- STEP 5:.*?{% if step == 5 %}(.*?)<!-- STEP 6', content, re.DOTALL)
if step5_match:
    supuestos_content = step5_match.group(1).replace('{% endif %}\n\n                ', '')
    supuestos_content = supuestos_content.replace('?step=6', '?step=4')

# Rewrite the tab-content completely
start_idx = content.find('<!-- Step Content -->')
end_idx = content.find('</div>\n    </div>\n</div>\n{% endblock %}')

new_content = content[:start_idx] + '''<!-- Step Content -->
            <div class="tab-content px-3">
                
                <!-- STEP 1: Crear Presupuesto -->
                {% if step == 1 %}
                <div class="text-center mb-4">
                    <h4 class="font-weight-bold">Información General del Presupuesto Institucional</h4>
                    <p class="text-muted">Define el nombre, periodo y horizonte de proyección del presupuesto.</p>
                </div>
                <div class="row justify-content-center">
                    <div class="col-lg-10">
                        <form method="POST" id="planForm">
                            {% csrf_token %}
                            <div class="row">
                                <div class="col-md-8 mb-3">
                                    <label class="font-weight-bold">Nombre del Presupuesto</label>
                                    {{ form.name }}
                                </div>
                                <div class="col-md-4 mb-3">
                                    <label class="font-weight-bold">Tipo de Versión</label>
                                    {{ form.version_type }}
                                </div>
                                <div class="col-md-12 mb-3">
                                    <label class="font-weight-bold">Descripción</label>
                                    {{ form.description }}
                                </div>
                                
                                <div class="col-md-6 mb-3">
                                    <label class="font-weight-bold">Año de Inicio de Proyección</label>
                                    {{ form.projection_start_year }}
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="font-weight-bold">Años a Proyectar</label>
                                    {{ form.projection_years }}
                                </div>
                                
                                <div class="col-md-12 mb-3 d-flex align-items-center mt-2">
                                    <div class="custom-control custom-switch">
                                        {{ form.is_active }}
                                        <label class="custom-control-label font-weight-bold" for="{{ form.is_active.id_for_label }}">Presupuesto Activo</label>
                                    </div>
                                </div>
                            </div>
                            <div class="text-right mt-4">
                                <button type="submit" class="btn btn-indigo px-5 rounded-pill">Guardar y Continuar <i class="fas fa-arrow-right ml-2"></i></button>
                            </div>
                        </form>
                    </div>
                </div>
                {% endif %}

                <!-- STEP 2: Base Historica -->
                {% if step == 2 %}
''' + budget_base_content.replace('?step=8', '?step=3') + '''
                {% endif %}

                <!-- STEP 3: Supuestos -->
                {% if step == 3 %}
''' + supuestos_content + '''
                {% endif %}

                <!-- STEP 4: Presupuesto Institucional -->
                {% if step == 4 %}
                <div class="text-center mb-4">
                    <h4 class="font-weight-bold">Presupuesto Institucional Generado</h4>
                    <p class="text-muted">Proyecciones y presupuesto basado en la base histórica y los supuestos.</p>
                </div>
                <div class="row justify-content-center">
                    <div class="col-lg-8 text-center">
                        <i class="fas fa-calculator fa-5x text-secondary mb-4 opacity-50"></i>
                        <p class="mb-4">Módulo en construcción. Aquí se visualizarán los estados financieros proyectados del presupuesto institucional.</p>
                        <a href="?step=5" class="btn btn-outline-indigo px-5 rounded-pill">Siguiente Paso <i class="fas fa-arrow-right ml-2"></i></a>
                    </div>
                </div>
                {% endif %}

                <!-- STEP 5: Grado de avance Presupuesto vs Ejecutado -->
                {% if step == 5 %}
                <div class="text-center mb-4">
                    <h4 class="font-weight-bold">Grado de Avance: Presupuesto vs Ejecutado</h4>
                    <p class="text-muted">Comparativa del presupuesto proyectado contra la ejecución real.</p>
                </div>
                <div class="row justify-content-center">
                    <div class="col-lg-8 text-center">
                        <i class="fas fa-chart-pie fa-5x text-secondary mb-4 opacity-50"></i>
                        <p class="mb-4">Módulo en construcción. Aquí se visualizará la comparativa de avance.</p>
                        <a href="?step=6" class="btn btn-outline-indigo px-5 rounded-pill">Siguiente Paso <i class="fas fa-arrow-right ml-2"></i></a>
                    </div>
                </div>
                {% endif %}

                <!-- STEP 6: Informe Final -->
                {% if step == 6 %}
                <div class="text-center mb-4">
                    <h4 class="font-weight-bold">Informe Final de Presupuesto Institucional</h4>
                    <p class="text-muted">Reportes detallados y resumen general del grado de avance.</p>
                </div>
                <div class="row justify-content-center">
                    <div class="col-lg-8 text-center">
                        <i class="fas fa-file-pdf fa-5x text-secondary mb-4 opacity-50"></i>
                        <p class="mb-4">Módulo en construcción. Aquí se visualizará el informe final ejecutivo.</p>
                    </div>
                </div>
                {% endif %}
            </div>
        </div>
    </div>
</div>
{% endblock %}
'''

with open('templates/financial_planning/institutional_budget_wizard.html', 'w', encoding='utf-8') as f:
    f.write(new_content)
