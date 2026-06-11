import re

with open('c:/Users/VICTUS/Desktop/A.RISK ERM - V2/templates/strategic_risk/controls.html', 'r', encoding='utf-8') as f:
    content = f.read()

start_marker = '<!-- Objetivos Estratégicos (BSC Perspectives) -->'
end_marker = '</script>\n{% endblock %}'

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx == -1 or end_idx == -1:
    print('Markers not found')
    exit(1)

units_data = [
    {
        'id': 1,
        'unidad': 'Unidad de Negocio: Créditos (Colocaciones)',
        'opcion': 'CRECIMIENTO CON CALIDAD',
        'objetivo': 'Incrementar la colocación de créditos manteniendo controlada la morosidad.',
        'estrategias': [
            {
                'text': '• Colocar microcréditos a PYMES.<br>• Implementar campañas de crédito escolar/festivos.<br>• Optimizar los tiempos de evaluación.',
                'indicador': '% Incremento de la Cartera Bruta',
                'min': '5%', 'med': '8%', 'opt': '12%'
            },
            {
                'text': '• Mejorar los filtros de evaluación (fórmula ARISK).<br>• Reforzar la gestión de cobranza preventiva.<br>• Recuperación de cartera castigada.',
                'indicador': '% Ratio de Morosidad (Mora > 30 días)',
                'min': '6.5%', 'med': '5.0%', 'opt': '3.5%'
            }
        ]
    },
    {
        'id': 2,
        'unidad': 'Unidad de Negocio: Captaciones (Ahorros y Finanzas)',
        'opcion': 'FORTALECER LIQUIDEZ Y FONDEO',
        'objetivo': 'Optimizar la estructura de fondeo mediante captación de Depósitos a Plazo Fijo (DPF).',
        'estrategias': [
            {
                'text': '• Lanzar campañas de DPF con tasas competitivas.<br>• Fidelizar a los socios con saldos altos.<br>• Promover el ahorro programado en socios nuevos.',
                'indicador': '% Crecimiento de Depósitos Totales',
                'min': '4%', 'med': '7%', 'opt': '10%'
            },
            {
                'text': '• Negociar mejores tasas para montos institucionales.<br>• Monitorear el costo de fondeo global.<br>• Diversificar los plazos de captación.',
                'indicador': '% Reducción del Gasto Financiero (Tasa Pasiva Promedio)',
                'min': '-0.2%', 'med': '-0.5%', 'opt': '-1.0%'
            }
        ]
    },
    {
        'id': 3,
        'unidad': 'Unidad de Negocio: Gestión de Riesgos y Cumplimiento',
        'opcion': 'MITIGACIÓN Y COMPLIANCE REGULATORIO',
        'objetivo': 'Garantizar la solvencia institucional ante las normativas regulatorias (p. ej., SBS).',
        'estrategias': [
            {
                'text': '• Evaluar continuamente el ALM (Activos y Pasivos).<br>• Mantener niveles óptimos de fondos disponibles.<br>• Automatizar alertas de descalce de plazos.',
                'indicador': 'Ratio de Liquidez (Moneda Nacional)',
                'min': '10%', 'med': '12%', 'opt': '15%'
            },
            {
                'text': '• Realizar talleres de capacitación en prevención de LA/FT.<br>• Atender las observaciones de auditoría interna/externa.<br>• Actualizar los manuales de riesgos de crédito.',
                'indicador': '% de Cumplimiento del Plan de Mitigación de Riesgos',
                'min': '90%', 'med': '95%', 'opt': '100%'
            }
        ]
    },
    {
        'id': 4,
        'unidad': 'Unidad de Negocio: Desarrollo Social y Membresía',
        'opcion': 'FIDELIZACIÓN Y VALOR COMPARTIDO',
        'objetivo': 'Incrementar la base de socios activos y fortalecer el impacto social.',
        'estrategias': [
            {
                'text': '• Campañas de afiliación orientadas a familiares de socios.<br>• Alianzas estratégicas con comercios locales.<br>• Simplificar el proceso de afiliación digital.',
                'indicador': '% Incremento de Socios Nuevos Hábiles',
                'min': '3%', 'med': '5%', 'opt': '8%'
            },
            {
                'text': '• Organización eficiente de la Asamblea General.<br>• Entrega oportuna de previsión social y canastas/incentivos.<br>• Programas de educación cooperativa y financiera.',
                'indicador': '',
                'min': '', 'med': '', 'opt': ''
            }
        ]
    }
]

def generate_table_obj(unit):
    uid = unit['id']
    html = f'''
                                <div class="table-responsive mt-4 bsc-unit" data-unit="{uid}">
                                    <table class="table table-bordered table-sm align-middle mb-2" style="border-color: #A9A48C;">
                                        <thead style="background-color: #C1BC9E; color: black; text-align: center;">
                                            <tr>
                                                <th colspan="4" class="text-left text-white" style="background-color: #5A5446;" contenteditable="true" data-sync="unidad-{uid}">{unit['unidad']}</th>
                                                <th colspan="4" class="text-left" style="background-color: #D6D2BD;">Opción estratégica: <span contenteditable="true" class="bg-white px-1" data-sync="opcion-{uid}">{unit['opcion']}</span></th>
                                            </tr>
                                            <tr>
                                                <th style="width: 3%;" rowspan="2" class="align-middle"></th>
                                                <th style="width: 25%;" rowspan="2" class="align-middle">Objetivo estratégico</th>
                                                <th style="width: 20%;" rowspan="2" class="align-middle">Estrategias</th>
                                                <th style="width: 15%;" rowspan="2" class="align-middle">Indicadores<br>seguimiento</th>
                                                <th style="width: 37%;" colspan="3" class="align-middle border-bottom-0">METAS / Objetivos concretos</th>
                                            </tr>
                                            <tr>
                                                <th style="width: 12%;" class="border-top-0">mínimo</th>
                                                <th style="width: 12%;" class="border-top-0">medio</th>
                                                <th style="width: 13%;" class="border-top-0">óptimo</th>
                                            </tr>
                                        </thead>
                                        <tbody id="objetivos-tbody-{uid}">
'''
    html += f'''
                                            <tr>
                                                <td rowspan="2" class="text-center font-weight-bold text-white align-middle" style="background-color: #A9A48C;">1</td>
                                                <td rowspan="2" contenteditable="true" class="bg-white align-middle font-weight-bold" data-sync="objetivo-{uid}-1">{unit['objetivo']}</td>
                                                <td contenteditable="true" class="bg-white" data-sync="estrategia-{uid}-1-1">{unit['estrategias'][0]['text']}</td>
                                                <td contenteditable="true" class="bg-white align-middle text-center font-weight-bold">{unit['estrategias'][0]['indicador']}</td>
                                                <td contenteditable="true" class="bg-white align-middle text-center">{unit['estrategias'][0]['min']}</td>
                                                <td contenteditable="true" class="bg-white align-middle text-center">{unit['estrategias'][0]['med']}</td>
                                                <td contenteditable="true" class="bg-white align-middle text-center">{unit['estrategias'][0]['opt']}</td>
                                            </tr>
                                            <tr>
                                                <td contenteditable="true" class="bg-white" data-sync="estrategia-{uid}-1-2">{unit['estrategias'][1]['text']}</td>
                                                <td contenteditable="true" class="bg-white align-middle text-center font-weight-bold">{unit['estrategias'][1]['indicador']}</td>
                                                <td contenteditable="true" class="bg-white align-middle text-center">{unit['estrategias'][1]['min']}</td>
                                                <td contenteditable="true" class="bg-white align-middle text-center">{unit['estrategias'][1]['med']}</td>
                                                <td contenteditable="true" class="bg-white align-middle text-center">{unit['estrategias'][1]['opt']}</td>
                                            </tr>
'''
    html += f'''
                                        </tbody>
                                    </table>
                                    <div class="text-right mb-5">
                                        <button class="btn btn-sm btn-outline-success" onclick="addBloqueEstrategia({uid})"><i class="fas fa-plus"></i> Añadir bloque a esta unidad</button>
                                    </div>
                                </div>
'''
    return html

def generate_table_pol(unit):
    uid = unit['id']
    html = f'''
                                <div class="table-responsive mt-4 bsc-unit-pol" data-unit="{uid}">
                                    <table class="table table-bordered table-sm align-middle mb-2" style="border-color: #A9A48C;">
                                        <thead style="background-color: #C1BC9E; color: black; text-align: center;">
                                            <tr>
                                                <th colspan="2" class="text-left text-white" style="background-color: #5A5446;" contenteditable="true" data-sync="unidad-{uid}">{unit['unidad']}</th>
                                                <th colspan="2" class="text-left" style="background-color: #D6D2BD;">Opción estratégica: <span contenteditable="true" class="bg-white px-1" data-sync="opcion-{uid}">{unit['opcion']}</span></th>
                                            </tr>
                                            <tr>
                                                <th style="width: 3%;" class="align-middle"></th>
                                                <th style="width: 25%;" class="align-middle">Objetivo estratégico</th>
                                                <th style="width: 25%;" class="align-middle">Estrategias</th>
                                                <th style="width: 47%;" class="align-middle">Políticas</th>
                                            </tr>
                                        </thead>
                                        <tbody id="politicas-tbody-{uid}">
'''
    html += f'''
                                            <tr>
                                                <td rowspan="2" class="text-center font-weight-bold text-white align-middle" style="background-color: #A9A48C;">1</td>
                                                <td rowspan="2" contenteditable="true" class="bg-white align-middle font-weight-bold" data-sync="objetivo-{uid}-1">{unit['objetivo']}</td>
                                                <td contenteditable="true" class="bg-white" data-sync="estrategia-{uid}-1-1">{unit['estrategias'][0]['text']}</td>
                                                <td contenteditable="true" class="bg-white"></td>
                                            </tr>
                                            <tr>
                                                <td contenteditable="true" class="bg-white" data-sync="estrategia-{uid}-1-2">{unit['estrategias'][1]['text']}</td>
                                                <td contenteditable="true" class="bg-white"></td>
                                            </tr>
'''
    html += f'''
                                        </tbody>
                                    </table>
                                </div>
'''
    return html

obj_html = '''<!-- Objetivos Estratégicos (BSC Perspectives) -->
                            <div class="tab-pane fade" id="v-pills-objetivos" role="tabpanel">
                                <div class="d-flex justify-content-between align-items-center mb-3">
                                    <h5 class="text-secondary font-weight-bold mb-0">Objetivos Estratégicos</h5>
                                    <button class="btn btn-sm btn-success" onclick="saveBscSection('objetivos')"><i class="fas fa-save"></i> Guardar Objetivos</button>
                                </div>
                                <div class="d-flex justify-content-center align-items-end mb-2 mt-4">
                                    <h5 class="font-weight-bold text-center mb-0">Objetivos estratégicos <span contenteditable="true" class="sync-year bg-light px-2 border rounded">202X</span></h5>
                                </div>
                                <div id="objetivos-container">
'''
for u in units_data:
    obj_html += generate_table_obj(u)

obj_html += '''
                                </div>
                                <div class="text-center mt-4">
                                    <button class="btn btn-primary" onclick="addUnidadNegocio()"><i class="fas fa-plus"></i> Añadir Nueva Unidad de Negocio</button>
                                </div>
                            </div>
'''

pol_html = '''<!-- Políticas para el periodo -->
                            <div class="tab-pane fade" id="v-pills-politicas" role="tabpanel">
                                <div class="d-flex justify-content-between align-items-center mb-3">
                                    <h5 class="text-secondary font-weight-bold mb-0">Políticas para el periodo</h5>
                                    <button class="btn btn-sm btn-success" onclick="saveBscSection('politicas')"><i class="fas fa-save"></i> Guardar Políticas</button>
                                </div>
                                <div class="d-flex justify-content-center align-items-end mb-2 mt-4">
                                    <h5 class="font-weight-bold text-center mb-0">Políticas para el período <span contenteditable="true" class="sync-year bg-light px-2 border rounded">202X</span></h5>
                                </div>
                                <div id="politicas-container">
'''
for u in units_data:
    pol_html += generate_table_pol(u)

pol_html += '''
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Modal Añadir Objetivo -->
<div class="modal fade" id="modalAddObjective" tabindex="-1" role="dialog">
    <div class="modal-dialog" role="document">
        <div class="modal-content">
            <div class="modal-header bg-success text-white">
                <h5 class="modal-title">Añadir Objetivo: <span id="objPerspectiveName"></span></h5>
                <button type="button" class="close text-white" data-dismiss="modal" aria-label="Close">
                    <span aria-hidden="true">&times;</span>
                </button>
            </div>
            <div class="modal-body">
                <form id="formAddObjective">
                    <input type="hidden" id="objectivePerspectiveId" name="perspective_id">
                    <div class="form-group">
                        <label>Nombre del Objetivo</label>
                        <input type="text" class="form-control" name="name" required>
                    </div>
                    <div class="form-group">
                        <label>Descripción</label>
                        <textarea class="form-control" name="description" rows="3"></textarea>
                    </div>
                    <button type="submit" class="btn btn-success btn-block">Guardar Objetivo</button>
                </form>
            </div>
        </div>
    </div>
</div>

<!-- Modal Añadir KPI -->
<div class="modal fade" id="modalAddKPI" tabindex="-1" role="dialog">
    <div class="modal-dialog" role="document">
        <div class="modal-content">
            <div class="modal-header bg-primary text-white">
                <h5 class="modal-title">Añadir Indicador (KPI): <span id="kpiObjectiveName"></span></h5>
                <button type="button" class="close text-white" data-dismiss="modal" aria-label="Close">
                    <span aria-hidden="true">&times;</span>
                </button>
            </div>
            <div class="modal-body">
                <form id="formAddKPI">
                    <input type="hidden" id="kpiObjectiveId" name="objective_id">
                    <div class="form-group">
                        <label>Nombre del KPI</label>
                        <input type="text" class="form-control" name="name" required>
                    </div>
                    <div class="form-row">
                        <div class="form-group col-md-6">
                            <label>Meta (Target)</label>
                            <input type="text" class="form-control" name="target" required placeholder="Ej: 15%">
                        </div>
                        <div class="form-group col-md-6">
                            <label>Frecuencia</label>
                            <select class="form-control" name="frequency">
                                <option value="Mensual">Mensual</option>
                                <option value="Trimestral">Trimestral</option>
                                <option value="Semestral">Semestral</option>
                                <option value="Anual">Anual</option>
                            </select>
                        </div>
                    </div>
                    <button type="submit" class="btn btn-primary btn-block">Guardar KPI</button>
                </form>
            </div>
        </div>
    </div>
</div>

{% endblock %}

{% block extra_js %}
<script>
    $('#modalAddObjective').on('show.bs.modal', function (event) {
        var button = $(event.relatedTarget);
        var perspectiveId = button.data('perspective');
        var perspectiveName = button.data('perspective-name');
        var modal = $(this);
        modal.find('#objPerspectiveName').text(perspectiveName);
        modal.find('#objectivePerspectiveId').val(perspectiveId);
    });

    $('#modalAddKPI').on('show.bs.modal', function (event) {
        var button = $(event.relatedTarget);
        var objectiveId = button.data('objective');
        var objectiveName = button.data('objective-name');
        var modal = $(this);
        modal.find('#kpiObjectiveName').text(objectiveName);
        modal.find('#kpiObjectiveId').val(objectiveId);
    });

    function saveBscSection(section) {
        toastr.success('Sección ' + section + ' guardada exitosamente (Simulación).');
    }

    function addFactorRow(btn) {
        let tbody = $(btn).closest('.card-body').find('tbody');
        let currentRows = tbody.find('tr').length;
        
        let headerCell = tbody.find('tr:first td:first');
        if(headerCell.attr('rowspan')) {
            headerCell.attr('rowspan', currentRows + 1);
        }

        let newRow = `
            <tr>
                <td contenteditable="true" class="bg-white"></td>
                <td contenteditable="true" class="bg-white"></td>
                <td contenteditable="true" class="bg-white text-center"></td>
                <td contenteditable="true" class="bg-white"></td>
                <td contenteditable="true" class="bg-white text-right"></td>
            </tr>
        `;
        tbody.append(newRow);
    }

    function removeLastFactorRow(btn) {
        let tbody = $(btn).closest('.card-body').find('tbody');
        let currentRows = tbody.find('tr').length;
        
        if (currentRows > 1) {
            tbody.find('tr:last').remove();
            
            let headerCell = tbody.find('tr:first td:first');
            if(headerCell.attr('rowspan')) {
                headerCell.attr('rowspan', currentRows - 1);
            }
        } else {
            toastr.info('La fila ha sido limpiada. Debe quedar al menos una fila por factor.');
        }
    }
    
    // Sync editable headers between Objetivos and Politicas
    $(document).ready(function() {
        // Generic sync function based on data-sync attribute
        $(document).on('input', '[data-sync]', function() {
            let syncId = $(this).attr('data-sync');
            let val = $(this).html(); // use html to preserve formatting like <br>
            $(`[data-sync="${syncId}"]`).not(this).html(val);
        });

        // Year sync
        $(document).on('input', '.sync-year', function() {
            let val = $(this).text();
            $('.sync-year').not(this).text(val);
        });
    });

    // Dynamic generation
    let unitCount = 4;
    function addUnidadNegocio() {
        unitCount++;
        let uid = unitCount;
        
        let objHtml = `
            <div class="table-responsive mt-4 bsc-unit" data-unit="${uid}">
                <table class="table table-bordered table-sm align-middle mb-2" style="border-color: #A9A48C;">
                    <thead style="background-color: #C1BC9E; color: black; text-align: center;">
                        <tr>
                            <th colspan="4" class="text-left text-white" style="background-color: #5A5446;" contenteditable="true" data-sync="unidad-${uid}">Unidad de Negocio Nueva</th>
                            <th colspan="4" class="text-left" style="background-color: #D6D2BD;">Opción estratégica: <span contenteditable="true" class="bg-white px-1" data-sync="opcion-${uid}">NUEVA OPCIÓN</span></th>
                        </tr>
                        <tr>
                            <th style="width: 3%;" rowspan="2" class="align-middle"></th>
                            <th style="width: 25%;" rowspan="2" class="align-middle">Objetivo estratégico</th>
                            <th style="width: 20%;" rowspan="2" class="align-middle">Estrategias</th>
                            <th style="width: 15%;" rowspan="2" class="align-middle">Indicadores<br>seguimiento</th>
                            <th style="width: 37%;" colspan="3" class="align-middle border-bottom-0">METAS / Objetivos concretos</th>
                        </tr>
                        <tr>
                            <th style="width: 12%;" class="border-top-0">mínimo</th>
                            <th style="width: 12%;" class="border-top-0">medio</th>
                            <th style="width: 13%;" class="border-top-0">óptimo</th>
                        </tr>
                    </thead>
                    <tbody id="objetivos-tbody-${uid}">
                        <tr>
                            <td rowspan="1" class="text-center font-weight-bold text-white align-middle" style="background-color: #A9A48C;">1</td>
                            <td rowspan="1" contenteditable="true" class="bg-white align-middle font-weight-bold" data-sync="objetivo-${uid}-1">Nuevo Objetivo</td>
                            <td contenteditable="true" class="bg-white" data-sync="estrategia-${uid}-1-1">Nueva Estrategia</td>
                            <td contenteditable="true" class="bg-white align-middle text-center font-weight-bold"></td>
                            <td contenteditable="true" class="bg-white align-middle text-center"></td>
                            <td contenteditable="true" class="bg-white align-middle text-center"></td>
                            <td contenteditable="true" class="bg-white align-middle text-center"></td>
                        </tr>
                    </tbody>
                </table>
                <div class="text-right mb-5">
                    <button class="btn btn-sm btn-outline-success" onclick="addBloqueEstrategia(${uid})"><i class="fas fa-plus"></i> Añadir bloque a esta unidad</button>
                </div>
            </div>
        `;
        
        let polHtml = `
            <div class="table-responsive mt-4 bsc-unit-pol" data-unit="${uid}">
                <table class="table table-bordered table-sm align-middle mb-2" style="border-color: #A9A48C;">
                    <thead style="background-color: #C1BC9E; color: black; text-align: center;">
                        <tr>
                            <th colspan="2" class="text-left text-white" style="background-color: #5A5446;" contenteditable="true" data-sync="unidad-${uid}">Unidad de Negocio Nueva</th>
                            <th colspan="2" class="text-left" style="background-color: #D6D2BD;">Opción estratégica: <span contenteditable="true" class="bg-white px-1" data-sync="opcion-${uid}">NUEVA OPCIÓN</span></th>
                        </tr>
                        <tr>
                            <th style="width: 3%;" class="align-middle"></th>
                            <th style="width: 25%;" class="align-middle">Objetivo estratégico</th>
                            <th style="width: 25%;" class="align-middle">Estrategias</th>
                            <th style="width: 47%;" class="align-middle">Políticas</th>
                        </tr>
                    </thead>
                    <tbody id="politicas-tbody-${uid}">
                        <tr>
                            <td rowspan="1" class="text-center font-weight-bold text-white align-middle" style="background-color: #A9A48C;">1</td>
                            <td rowspan="1" contenteditable="true" class="bg-white align-middle font-weight-bold" data-sync="objetivo-${uid}-1">Nuevo Objetivo</td>
                            <td contenteditable="true" class="bg-white" data-sync="estrategia-${uid}-1-1">Nueva Estrategia</td>
                            <td contenteditable="true" class="bg-white"></td>
                        </tr>
                    </tbody>
                </table>
            </div>
        `;
        
        $('#objetivos-container').append(objHtml);
        $('#politicas-container').append(polHtml);
    }

    function addBloqueEstrategia(uid) {
        let objTbody = $(`#objetivos-tbody-${uid}`);
        let polTbody = $(`#politicas-tbody-${uid}`);
        
        // Find last block ID
        let lastId = 0;
        objTbody.find('> tr > td:first-child').each(function() {
            if($(this).attr('rowspan')) {
                let val = parseInt($(this).text());
                if(!isNaN(val) && val > lastId) lastId = val;
            }
        });
        
        let bid = lastId + 1; // Block ID
        
        let objRow = `
            <tr>
                <td rowspan="1" class="text-center font-weight-bold text-white align-middle" style="background-color: #A9A48C;">${bid}</td>
                <td rowspan="1" contenteditable="true" class="bg-white align-middle font-weight-bold" data-sync="objetivo-${uid}-${bid}"></td>
                <td contenteditable="true" class="bg-white" data-sync="estrategia-${uid}-${bid}-1"></td>
                <td contenteditable="true" class="bg-white align-middle text-center font-weight-bold"></td>
                <td contenteditable="true" class="bg-white align-middle text-center"></td>
                <td contenteditable="true" class="bg-white align-middle text-center"></td>
                <td contenteditable="true" class="bg-white align-middle text-center"></td>
            </tr>
        `;
        
        let polRow = `
            <tr>
                <td rowspan="1" class="text-center font-weight-bold text-white align-middle" style="background-color: #A9A48C;">${bid}</td>
                <td rowspan="1" contenteditable="true" class="bg-white align-middle font-weight-bold" data-sync="objetivo-${uid}-${bid}"></td>
                <td contenteditable="true" class="bg-white" data-sync="estrategia-${uid}-${bid}-1"></td>
                <td contenteditable="true" class="bg-white"></td>
            </tr>
        `;
        
        objTbody.append(objRow);
        polTbody.append(polRow);
    }
'''

new_content = content[:start_idx] + obj_html + pol_html + end_marker

with open('c:/Users/VICTUS/Desktop/A.RISK ERM - V2/templates/strategic_risk/controls.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('Success!')
