import re

with open('templates/financial_planning/institutional_budget_wizard.html', 'r', encoding='utf-8') as f:
    content = f.read()

table_html = '''
                {% if not plan %}
                {% if existing_budgets %}
                <hr class="mt-5 mb-5 border-indigo" style="opacity: 0.2;">
                <div class="row justify-content-center">
                    <div class="col-lg-10">
                        <h5 class="font-weight-bold mb-4 text-indigo"><i class="fas fa-list-alt mr-2"></i>Presupuestos Institucionales Guardados</h5>
                        <div class="card shadow-sm border-0 rounded-lg">
                            <div class="card-body p-0">
                                <div class="table-responsive">
                                    <table class="table table-hover table-striped mb-0">
                                        <thead class="bg-indigo text-white">
                                            <tr>
                                                <th class="border-0">Nombre</th>
                                                <th class="border-0">Versión</th>
                                                <th class="border-0">Horizonte</th>
                                                <th class="border-0">Última Actualización</th>
                                                <th class="border-0 text-center">Acciones</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {% for b in existing_budgets %}
                                            <tr>
                                                <td class="align-middle font-weight-bold">{{ b.name }}</td>
                                                <td class="align-middle">
                                                    <span class="badge {% if b.version_type == 'BASE' %}badge-primary{% elif b.version_type == 'OPTIMISTIC' %}badge-success{% else %}badge-warning{% endif %}">
                                                        {{ b.get_version_type_display }}
                                                    </span>
                                                </td>
                                                <td class="align-middle">{{ b.projection_start_year }} - {{ b.projection_start_year|add:b.projection_years }}</td>
                                                <td class="align-middle text-muted small"><i class="far fa-clock mr-1"></i>{{ b.updated_at|date:"d/m/Y H:i" }}</td>
                                                <td class="text-center align-middle">
                                                    <a href="{% url 'financial_planning:budget_wizard' b.id %}" class="btn btn-sm btn-indigo rounded-pill px-3 shadow-sm">
                                                        <i class="fas fa-play mr-1"></i> Continuar
                                                    </a>
                                                </td>
                                            </tr>
                                            {% endfor %}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                {% endif %}
                {% endif %}
'''

step1_end_str = '''                            <div class="text-right mt-4">
                                <button type="submit" class="btn btn-indigo px-5 rounded-pill">Guardar y Continuar <i class="fas fa-arrow-right ml-2"></i></button>
                            </div>
                        </form>
                    </div>
                </div>'''

new_content = content.replace(step1_end_str, step1_end_str + '\n' + table_html)

with open('templates/financial_planning/institutional_budget_wizard.html', 'w', encoding='utf-8') as f:
    f.write(new_content)
