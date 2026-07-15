import sys
wizard = open(r'templates\financial_planning\wizard.html', encoding='utf-8').read()

original_step_7 = """                {% if step == 7 %}
                <div class="text-center mb-4">
                    <h4 class="font-weight-bold">Estado de Resultados Proyectado</h4>
                    <p class="text-muted">Vista del Estado de Resultados resultante de las proyecciones.</p>
                </div>
                <div class="row">
                    <div class="col-12">
                        {% if not has_projections %}
                        <div class="alert alert-warning text-center shadow-sm">
                            <i class="fas fa-exclamation-triangle mr-2"></i> No hay datos proyectados para este plan. Asegúrate de ejecutar el motor de proyecciones.
                        </div>
                        <div class="text-center mt-4">
                            <form action="{% url 'financial_planning:generate_projections' %}" method="POST" class="d-inline-block mr-2">
                                {% csrf_token %}
                                <input type="hidden" name="plan_id" value="{{ plan.id }}">
                                <input type="hidden" name="wizard" value="7">
                                <button type="submit" class="btn btn-warning px-4 rounded-pill font-weight-bold shadow-sm">
                                    <i class="fas fa-cogs mr-2"></i> Ejecutar Motor de Proyecciones
                                </button>
                            </form>
                            <a href="?step=8" class="btn btn-outline-indigo px-5 rounded-pill">Siguiente Paso <i class="fas fa-arrow-right ml-2"></i></a>
                        </div>
                        {% else %}
                        <div class="card shadow-sm border-0 mb-4" style="border-radius: 12px;">
                            <div class="card-header bg-white border-bottom-0 pt-4 pb-0">
                                <h6 class="font-weight-bold text-uppercase mb-0" style="color: #1e293b;"><i class="fas fa-chart-bar mr-2 text-primary"></i> Resumen de P&L Mensual</h6>
                                <p class="text-muted small mt-1 mb-0">Valores expresados en Moneda Nacional (S/)</p>
                            </div>
                            <div class="card-body px-0">
                                <div class="table-responsive px-4 pb-2">
                                    <table class="table table-hover table-sm mb-0" style="font-size: 0.85rem; min-width: 1500px;">
                                        <thead class="bg-light">
                                            <tr>
                                                <th class="text-secondary border-top-0 align-middle" style="min-width: 200px; position: sticky; left: 0; background-color: #f8f9fa; z-index: 2; border-right: 2px solid #e2e8f0;">Concepto</th>
                                                {% for row in table_rows %}
                                                <th class="text-center text-secondary border-top-0" style="min-width: 90px;">{{ row.month }}</th>
                                                {% endfor %}
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <!-- Ingresos Financieros -->
                                            <tr>
                                                <td class="font-weight-bold text-success" style="position: sticky; left: 0; background-color: #fff; z-index: 1; border-right: 2px solid #e2e8f0;">Ingresos Financieros (+)</td>
                                                {% for row in table_rows %}
                                                <td class="text-right text-success">{{ row.fin_income|floatformat:2|intcomma }}</td>
                                                {% endfor %}
                                            </tr>
                                            {% for account in detailed_accounts.fin_income %}
                                            <tr style="background-color: #fcfcfc; font-size: 0.8rem;">
                                                <td class="text-muted" style="position: sticky; left: 0; background-color: #fcfcfc; z-index: 1; border-right: 2px solid #e2e8f0; padding-left: 2rem !important;">
                                                    <i class="fas fa-angle-right mr-1 opacity-50"></i> {{ account.name }}
                                                </td>
                                                {% for val in account.values %}
                                                <td class="text-right text-muted">{{ val|floatformat:2|intcomma }}</td>
                                                {% endfor %}
                                            </tr>
                                            {% endfor %}
                                            <!-- Gastos Financieros -->
                                            <tr>
                                                <td class="font-weight-bold text-danger" style="position: sticky; left: 0; background-color: #fff; z-index: 1; border-right: 2px solid #e2e8f0;">Gastos Financieros (-)</td>
                                                {% for row in table_rows %}
                                                <td class="text-right text-danger">{{ row.fin_expense|floatformat:2|intcomma }}</td>
                                                {% endfor %}
                                            </tr>
                                            {% for account in detailed_accounts.fin_expense %}
                                            <tr style="background-color: #fcfcfc; font-size: 0.8rem;">
                                                <td class="text-muted" style="position: sticky; left: 0; background-color: #fcfcfc; z-index: 1; border-right: 2px solid #e2e8f0; padding-left: 2rem !important;">
                                                    <i class="fas fa-angle-right mr-1 opacity-50"></i> {{ account.name }}
                                                </td>
                                                {% for val in account.values %}
                                                <td class="text-right text-muted">{{ val|floatformat:2|intcomma }}</td>
                                                {% endfor %}
                                            </tr>
                                            {% endfor %}
                                            <!-- Margen Bruto -->
                                            <tr style="background-color: #f8fafc;">
                                                <td class="font-weight-bold text-dark" style="position: sticky; left: 0; background-color: #f8fafc; z-index: 1; border-right: 2px solid #e2e8f0;">MARGEN BRUTO (=)</td>
                                                {% for row in table_rows %}
                                                <td class="text-right font-weight-bold">{{ row.gross_margin|floatformat:2|intcomma }}</td>
                                                {% endfor %}
                                            </tr>
                                            <!-- Provisiones -->
                                            <tr>
                                                <td class="font-weight-bold text-warning" style="position: sticky; left: 0; background-color: #fff; z-index: 1; border-right: 2px solid #e2e8f0;">Provisiones (-)</td>
                                                {% for row in table_rows %}
                                                <td class="text-right text-warning">{{ row.provisions|floatformat:2|intcomma }}</td>
                                                {% endfor %}
                                            </tr>
                                            {% for account in detailed_accounts.provisions %}
                                            <tr style="background-color: #fcfcfc; font-size: 0.8rem;">
                                                <td class="text-muted" style="position: sticky; left: 0; background-color: #fcfcfc; z-index: 1; border-right: 2px solid #e2e8f0; padding-left: 2rem !important;">
                                                    <i class="fas fa-angle-right mr-1 opacity-50"></i> {{ account.name }}
                                                </td>
                                                {% for val in account.values %}
                                                <td class="text-right text-muted">{{ val|floatformat:2|intcomma }}</td>
                                                {% endfor %}
                                            </tr>
                                            {% endfor %}
                                            <!-- Margen Neto -->
                                            <tr style="background-color: #f8fafc;">
                                                <td class="font-weight-bold text-dark" style="position: sticky; left: 0; background-color: #f8fafc; z-index: 1; border-right: 2px solid #e2e8f0;">MARGEN NETO (=)</td>
                                                {% for row in table_rows %}
                                                <td class="text-right font-weight-bold">{{ row.net_margin|floatformat:2|intcomma }}</td>
                                                {% endfor %}
                                            </tr>
                                            <!-- Gastos Operativos -->
                                            <tr>
                                                <td class="font-weight-bold text-danger" style="position: sticky; left: 0; background-color: #fff; z-index: 1; border-right: 2px solid #e2e8f0;">Gastos Operativos (-)</td>
                                                {% for row in table_rows %}
                                                <td class="text-right text-danger">{{ row.op_expense|floatformat:2|intcomma }}</td>
                                                {% endfor %}
                                            </tr>
                                            {% for account in detailed_accounts.op_expense %}
                                            <tr style="background-color: #fcfcfc; font-size: 0.8rem;">
                                                <td class="text-muted" style="position: sticky; left: 0; background-color: #fcfcfc; z-index: 1; border-right: 2px solid #e2e8f0; padding-left: 2rem !important;">
                                                    <i class="fas fa-angle-right mr-1 opacity-50"></i> {{ account.name }}
                                                </td>
                                                {% for val in account.values %}
                                                <td class="text-right text-muted">{{ val|floatformat:2|intcomma }}</td>
                                                {% endfor %}
                                            </tr>
                                            {% endfor %}
                                            <!-- Excedente Neto -->
                                            <tr style="background-color: #f1f5f9; border-top: 2px solid #cbd5e1;">
                                                <td class="font-weight-bold" style="position: sticky; left: 0; background-color: #f1f5f9; z-index: 1; border-right: 2px solid #e2e8f0; color: #0f172a;">RESULTADO DEL EJERCICIO (=)</td>
                                                {% for row in table_rows %}
                                                <td class="text-right font-weight-bold {% if row.net_remanent < 0 %}text-danger{% else %}text-primary{% endif %}">
                                                    {{ row.net_remanent|floatformat:2|intcomma }}
                                                </td>
                                                {% endfor %}
                                            </tr>
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                        <div class="text-center mt-4">
                            <a href="?step=8" class="btn btn-primary px-5 py-2 shadow-sm font-weight-bold rounded-pill">Siguiente: BG Proyectado <i class="fas fa-arrow-right ml-2"></i></a>
                        </div>
                        {% endif %}
                    </div>
                </div>
                {% endif %}"""

part1 = wizard.split('{% if step == 7 %}')[0]
part2 = wizard.split('<!-- STEP 8: Balance General Proyectado -->')[1]

wizard_new = part1 + original_step_7 + '\n\n                <!-- STEP 8: Balance General Proyectado -->' + part2
open(r'templates\financial_planning\wizard.html', 'w', encoding='utf-8').write(wizard_new)
print('Done reverting')
