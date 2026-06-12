
    function updateIndexes() {
        $('#metas-table tbody tr').each(function(index) {
            $(this).find('.index-cell').text(index + 1);
        });
    }

    function addMetaRow() {
        const tr = `
            <tr>
                <td class="align-middle index-cell"></td>
                <td>
                    <select class="form-control form-control-sm meta-perspectiva">
                        {% for p in perspectivas %}
                        <option value="{{ p.nombre }}">{{ p.nombre }}</option>
                        {% endfor %}
                    </select>
                </td>
                <td><input type="text" class="form-control form-control-sm meta-objetivo" placeholder="Nuevo objetivo"></td>
                <td>
                    <select class="form-control form-control-sm meta-tipo">
                        {% for t in tipos_objetivo %}
                        <option value="{{ t.nombre }}">{{ t.nombre }}</option>
                        {% endfor %}
                    </select>
                </td>
                <td>
                    <select class="form-control form-control-sm meta-area">
                        {% for a in areas_responsables %}
                        <option value="{{ a.nombre }}">{{ a.nombre }}</option>
                        {% endfor %}
                    </select>
                </td>
                <td>
                    <select class="form-control form-control-sm meta-responsable">
                        {% for r in responsables %}
                        <option value="{{ r.nombre }}">{{ r.nombre }}</option>
                        {% endfor %}
                    </select>
                </td>
                <td><input type="text" class="form-control form-control-sm meta-indicador" placeholder="KPI"></td>
                <td><input type="text" class="form-control form-control-sm meta-base" placeholder="Base"></td>
                <td><input type="text" class="form-control form-control-sm meta-1" placeholder="Meta 1"></td>
                <td><input type="text" class="form-control form-control-sm meta-2" placeholder="Meta 2"></td>
                <td><input type="text" class="form-control form-control-sm meta-3" placeholder="Meta 3"></td>
                <td class="align-middle">
                    <button class="btn btn-sm btn-outline-danger" onclick="removeRow(this)"><i class="fas fa-trash"></i></button>
                </td>
            </tr>
        `;
        $('#metas-table tbody').append(tr);
        updateIndexes();
    }

    function removeRow(btn) {
        $(btn).closest('tr').remove();
        updateIndexes();
    }

    function saveBscSection() {
        const metas = [];
        $('#metas-table tbody tr').each(function() {
            metas.push({
                perspectiva: $(this).find('.meta-perspectiva').val(),
                objetivo: $(this).find('.meta-objetivo').val(),
                tipo: $(this).find('.meta-tipo').val(),
                area: $(this).find('.meta-area').val(),
                responsable: $(this).find('.meta-responsable').val(),
                indicador: $(this).find('.meta-indicador').val(),
                base: $(this).find('.meta-base').val(),
                meta1: $(this).find('.meta-1').val(),
                meta2: $(this).find('.meta-2').val(),
                meta3: $(this).find('.meta-3').val()
            });
        });

        // Add loading state
        Swal.fire({
            title: 'Guardando...',
            text: 'Estamos procesando tu información.',
            allowOutsideClick: false,
            didOpen: () => {
                Swal.showLoading();
            }
        });

        const plan_id = "{{ plan.id|default_if_none:'' }}";
        if (!plan_id) {
            Swal.fire('Error', 'No hay un plan activo seleccionado.', 'error');
            return;
        }

        fetch("{% url 'strategic_risk:save_metas_planeadas' %}", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': '{{ csrf_token }}'
            },
            body: JSON.stringify({
                plan_id: plan_id,
                data: metas
            })
        })
        .then(response => response.json())
        .then(data => {
            if(data.status === 'success') {
                Swal.fire({
                    icon: 'success',
                    title: '¡Guardado!',
                    text: 'Las Metas Planeadas se guardaron con éxito.',
                    confirmButtonColor: '#10b981'
                });
            } else {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: data.message || 'Hubo un error al guardar las metas.',
                    confirmButtonColor: '#ef4444'
                });
            }
        })
        .catch(error => {
            console.error('Error:', error);
            Swal.fire({
                icon: 'error',
                title: 'Error de Red',
                text: 'No se pudo contactar al servidor. Revisa tu conexión.',
                confirmButtonColor: '#ef4444'
            });
        });
    }

    function saveDesarrolloObjetivo() {
        const data = {
            objective_id: $('#objective_id_hidden').val() || null,
            perspective_id: $('select[name="desarrollo_perspectiva"]').val(),
            name: $('input[name="desarrollo_nombre"]').val(),
            description: $('textarea[name="desarrollo_descripcion"]').val(),
            propuesta_valor: $('textarea[name="desarrollo_propuesta_valor"]').val(),
            tipo_objetivo: $('select[name="desarrollo_tipo"]').val(),
            area_responsable: $('select[name="desarrollo_area"]').val(),
            responsable: $('select[name="desarrollo_responsable"]').val()
        };

        if (!data.perspective_id || !data.name || !data.tipo_objetivo) {
            Swal.fire('Atención', 'Por favor complete los campos obligatorios: Perspectiva, Tipo y Nombre.', 'warning');
            return;
        }

        Swal.fire({
            title: 'Guardando...',
            text: 'Estamos procesando tu información.',
            allowOutsideClick: false,
            didOpen: () => {
                Swal.showLoading();
            }
        });

        fetch("{% url 'strategic_risk:add_objective' %}", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': '{{ csrf_token }}'
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(res => {
            if (res.status === 'success') {
                // Agregar a la tabla de Objetivos Ingresados
                const tbody = $('#tabla-objetivos-ingresados tbody');
                $('#no-data-row').remove();
                
                let fullDesc = data.description;
                if(data.propuesta_valor) {
                    fullDesc += '\n\nPropuesta de Valor:\n' + data.propuesta_valor;
                }

                let persText = $('select[name="desarrollo_perspectiva"] option:selected').text();
                let tipoText = $('select[name="desarrollo_tipo"] option:selected').text();
                
                const escapeHtmlAttr = (str) => {
                    if (!str) return '';
                    return str.replace(/'/g, "\\'").replace(/"/g, '&quot;').replace(/\n/g, "\\n");
                };
                
                const trHtml = `
                    <td class="align-middle"><span class="badge badge-info">${persText}</span></td>
                    <td class="align-middle">${tipoText}</td>
                    <td class="align-middle">${data.name}</td>
                    <td class="text-center align-middle">
                        <button class="btn btn-sm btn-light text-primary" title="Editar" onclick="editObjective(${res.id}, '${data.perspective_id}', '${escapeHtmlAttr(data.tipo_objetivo)}', '${escapeHtmlAttr(data.name)}', '${escapeHtmlAttr(fullDesc)}', '${escapeHtmlAttr(data.area_responsable)}', '${escapeHtmlAttr(data.responsable)}')"><i class="fas fa-edit"></i></button>
                        <button class="btn btn-sm btn-light text-danger" title="Eliminar" onclick="deleteObjective(${res.id})"><i class="fas fa-times"></i></button>
                    </td>
                `;

                if (data.objective_id) {
                    $('#obj-row-' + res.id).html(trHtml);
                } else {
                    const tr = `<tr id="obj-row-${res.id}">${trHtml}</tr>`;
                    tbody.append(tr);
                }
                
                // Limpiar formulario
                $('#form-desarrollo-objetivo')[0].reset();
                $('#objective_id_hidden').remove();
                
                Swal.fire({
                    icon: 'success',
                    title: '¡Guardado!',
                    text: res.message,
                    timer: 1500,
                    showConfirmButton: false
                });
            } else {
                Swal.fire('Error', res.message || 'Hubo un error al guardar.', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            Swal.fire('Error de Red', 'No se pudo contactar al servidor. Revisa tu conexión.', 'error');
        });
    }

    function clearFormAndScrollToTop() {
        $('#form-desarrollo-objetivo')[0].reset();
        $('#objective_id_hidden').remove();
        
        $('html, body').animate({ scrollTop: $('#form-desarrollo-objetivo').offset().top - 100 }, 500);
    }

    // --- LOGICA DE PONDERACION ---
    function updateTotalPonderacion() {
        let total = 0;
        $('.peso-input').each(function() {
            let val = parseFloat($(this).val()) || 0;
            total += val;
        });
        
        const totalEl = $('#total-ponderacion');
        totalEl.text(total.toFixed(2) + '%');
        
        if (total === 100) {
            totalEl.removeClass('text-danger text-warning').addClass('text-success');
        } else if (total > 100) {
            totalEl.removeClass('text-success text-warning').addClass('text-danger');
        } else {
            totalEl.removeClass('text-success text-danger').addClass('text-warning');
        }
    }

    $(document).on('input', '.peso-input', updateTotalPonderacion);

    // Initial update
    $(document).ready(function() {
        updateTotalPonderacion();
    });

    function savePonderaciones() {
        let total = 0;
        const data = [];
        $('.peso-input').each(function() {
            let val = parseFloat($(this).val()) || 0;
            total += val;
            data.push({
                id: $(this).data('obj-id'),
                peso: val
            });
        });

        if (total !== 100) {
            Swal.fire('Atención', `La suma total de la ponderación debe ser exactamente 100%. Actualmente es ${total.toFixed(2)}%.`, 'warning');
            return;
        }

        Swal.fire({
            title: 'Guardando ponderaciones...',
            allowOutsideClick: false,
            didOpen: () => { Swal.showLoading(); }
        });

        fetch("{% url 'strategic_risk:save_ponderaciones' %}", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': '{{ csrf_token }}'
            },
            body: JSON.stringify({ ponderaciones: data })
        })
        .then(response => response.json())
        .then(res => {
            if (res.status === 'success') {
                Swal.fire({
                    icon: 'success',
                    title: '¡Guardado!',
                    text: 'Las ponderaciones se han actualizado correctamente.',
                    timer: 1500,
                    showConfirmButton: false
                });
            } else {
                Swal.fire('Error', res.message || 'Error al guardar.', 'error');
            }
        })
        .catch(err => {
            console.error(err);
            Swal.fire('Error', 'No se pudo conectar con el servidor.', 'error');
        });
    }

    // Funciones de edicion y eliminacion
    function editObjective(id, pers_id, tipo, nombre, desc, area, resp) {
        let textDesc = desc || '';
        let pv = '';
        if (textDesc.includes('\n\nPropuesta de Valor:\n')) {
            let parts = textDesc.split('\n\nPropuesta de Valor:\n');
            textDesc = parts[0];
            pv = parts[1] || '';
        }
        
        $('#objective_id_hidden').remove();
        $('#form-desarrollo-objetivo').append(`<input type="hidden" id="objective_id_hidden" name="objective_id" value="${id}">`);
        
        $('select[name="desarrollo_perspectiva"]').val(pers_id);
        $('select[name="desarrollo_tipo"]').val(tipo);
        $('input[name="desarrollo_nombre"]').val(nombre);
        $('textarea[name="desarrollo_descripcion"]').val(textDesc);
        $('textarea[name="desarrollo_propuesta_valor"]').val(pv);
        $('select[name="desarrollo_area"]').val(area);
        $('select[name="desarrollo_responsable"]').val(resp);
        
        $('#tab-desarrollo').tab('show');
        $('html, body').animate({ scrollTop: $('#form-desarrollo-objetivo').offset().top - 100 }, 500);
    }

    function deleteObjective(id) {
        Swal.fire({
            title: '¿Estás seguro?',
            text: "Se eliminará este objetivo y sus indicadores asociados.",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonColor: '#3085d6',
            confirmButtonText: 'Sí, eliminar',
            cancelButtonText: 'Cancelar'
        }).then((result) => {
            if (result.isConfirmed) {
                fetch('/estrategico/ajax/delete-objective/' + id + '/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': '{{ csrf_token }}'
                    }
                })
                .then(response => response.json())
                .then(res => {
                    if(res.status === 'success') {
                        $('#obj-row-' + id).remove();
                        if($('#tabla-objetivos-ingresados tbody tr').length === 0) {
                            $('#tabla-objetivos-ingresados tbody').append(`
                                <tr id="no-data-row">
                                    <td colspan="4" class="text-center text-muted py-4">
                                        <i class="fas fa-folder-open fa-2x mb-2 text-black-50"></i><br>
                                        No se han registrado objetivos para esta planificación.
                                    </td>
                                </tr>
                            `);
                        }
                        Swal.fire('Eliminado!', 'El objetivo ha sido eliminado.', 'success');
                    } else {
                        Swal.fire('Error!', res.message, 'error');
                    }
                });
            }
        });
    }

    // Inicializar índices al cargar
    $(document).ready(function() {
        updateIndexes();
    });
