
                        document.addEventListener('DOMContentLoaded', function() {
                            const MONTH_NAMES = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'];
                            const historicalDataJson = '{{ historical_data_json|escapejs }}';
                            let histSavedPeriods = [];
                            let histBalanceData = null;
                            let histMode = 'accum';

                            function histGetLevelClass(level){if(level<=1)return'1';if(level===2)return'2';if(level<=4)return'3';if(level<=6)return'4';if(level<=8)return'5';if(level<=10)return'6';return'7';}
                            function histFmtAmt(amount){const rounded=Math.round(amount);if(rounded===0){return amount===0?'<span class="zero-amount" style="color:#adb5bd;">-</span>':'<span>0</span>';}const formatted=Math.abs(rounded).toLocaleString('en-US',{minimumFractionDigits:0,maximumFractionDigits:0});if(rounded<0)return`<span class="negative-amount" style="color:#dc3545;">(${formatted})</span>`;return`<span>${formatted}</span>`;}

                            // Parse saved periods
                            try {
                                const parsed = JSON.parse(historicalDataJson);
                                if (parsed && parsed.selected_periods && parsed.selected_periods.length > 0) {
                                    histSavedPeriods = parsed.selected_periods;
                                }
                            } catch(e) { console.error("Error parsing historical_data", e); }

                            if (!histSavedPeriods.length) {
                                document.getElementById('no-historical-warning').style.display = 'block';
                                document.getElementById('hist-content-wrapper').style.display = 'none';
                                return;
                            }

                            document.getElementById('no-historical-warning').style.display = 'none';
                            document.getElementById('hist-content-wrapper').style.display = 'block';

                            // Render period badges
                            const badgesHtml = histSavedPeriods.map(p => {
                                const [y,m] = p.split('-');
                                return `<span class="badge badge-primary mr-1 mb-1" style="font-size:0.78rem;border-radius:20px;padding:4px 10px;">${MONTH_NAMES[parseInt(m)-1]}-${y}</span>`;
                            }).join('');
                            document.getElementById('hist-period-badges').innerHTML = badgesHtml;

                            // Fetch from API
                            histFetchData();

                            function histFetchData() {
                                $.ajax({
                                    url: "{% url 'financial_planning:api_trial_balance_data' %}",
                                    data: { periods: JSON.stringify(histSavedPeriods), currency: 'MN' },
                                    success: function(resp) {
                                        if (resp.status === 'success') {
                                            histBalanceData = resp;
                                            histRenderAll();
                                        } else {
                                            $('#hist-bs-body').html('<tr><td colspan="99" class="text-center p-4 text-danger">Error: '+resp.msg+'</td></tr>');
                                        }
                                    },
                                    error: function() {
                                        $('#hist-bs-body').html('<tr><td colspan="99" class="text-center p-4 text-danger">Error de conexión.</td></tr>');
                                    }
                                });
                            }

                            window.histSetMode = function(mode) {
                                histMode = mode;
                                document.getElementById('hist-toggleAccum').style.background = mode==='accum'?'#fff':'none';
                                document.getElementById('hist-toggleAccum').style.boxShadow = mode==='accum'?'0 2px 6px rgba(0,0,0,0.1)':'none';
                                document.getElementById('hist-toggleAccum').style.color = mode==='accum'?'#212529':'#6c757d';
                                document.getElementById('hist-toggleMonth').style.background = mode==='month'?'#fff':'none';
                                document.getElementById('hist-toggleMonth').style.boxShadow = mode==='month'?'0 2px 6px rgba(0,0,0,0.1)':'none';
                                document.getElementById('hist-toggleMonth').style.color = mode==='month'?'#212529':'#6c757d';
                                histRenderAll();
                            };

                            function histRenderAll() {
                                if (!histBalanceData) return;
                                const periods = histBalanceData.periods;
                                const numCols = periods.length;
                                const colW = 105; // Adjusted width
                                const pHeaders = periods.map(p=>{const[y,m]=p.split('-');return`<th class="px-2" style="min-width:${colW}px;width:${colW}px;text-align:right;">${MONTH_NAMES[parseInt(m)-1]}-${y}</th>`;}).join('');
                                const theadHtml = `<tr><th style="width:90px;min-width:90px;text-align:left;">Código</th><th class="col-desc" style="width:260px;min-width:260px;text-align:left;">Descripción</th>${pHeaders}</tr>`;
                                
                                $('#hist-bs-thead').html(theadHtml);
                                $('#hist-is-thead').html(theadHtml);
                                $('#hist-mis-thead').html(theadHtml);

                                $('#hist-bs-body').html(histBuildRows(histBalanceData.balance_sheet, periods, 'bs') || '<tr><td colspan="99" class="text-center text-muted p-4">Sin datos.</td></tr>');
                                $('#hist-is-body').html(histBuildRows(histBalanceData.income_statement, periods, 'bis') || '<tr><td colspan="99" class="text-center text-muted p-4">Sin datos.</td></tr>');
                                $('#hist-mis-body').html(histBuildRows(histBalanceData.income_statement, periods, 'bmis') || '<tr><td colspan="99" class="text-center text-muted p-4">Sin datos.</td></tr>');

                                if (histBalanceData.totals) histRenderSummary(histBalanceData.totals, periods);
                            }

                            function histBuildRows(items, periods, prefix) {
                                let sortedItems = items;
                                if (prefix === 'bis' || prefix === 'bmis') {
                                    sortedItems = [
                                        ...items.filter(a => a.code.toString().startsWith('5')),
                                        ...items.filter(a => a.code.toString().startsWith('4')),
                                        ...items.filter(a => !a.code.toString().startsWith('5') && !a.code.toString().startsWith('4'))
                                    ];
                                }
                                let html = '';
                                sortedItems.forEach(item => {
                                    const hasChildren = item.children_codes && item.children_codes.length > 0;
                                    const lvl = histGetLevelClass(item.level);
                                    const isRoot = !item.parent_code;
                                    const bDict = (prefix==='bmis') ? item.monthly_balances : item.balances;
                                    const cells = periods.map(p => {
                                        const val = (bDict && bDict[p]!=null) ? bDict[p] : 0;
                                        return `<td class="text-right text-monospace px-2">${histFmtAmt(val)}</td>`;
                                    }).join('');
                                    html += `<tr class="accounting-row level-${lvl} ${hasChildren?'':'level-leaf'} node-collapsed" style="${isRoot?'':'display:none;'}" data-code="${item.code}" data-parent="${item.parent_code||''}" data-prefix="${prefix}" data-depth="${item.depth}" id="${prefix}-row-${item.code}" onclick="histToggleRow('${item.code}','${prefix}')">
                                        <td style="padding-left:${item.depth*14}px;">${hasChildren?'<span class="node-expander"><i class="fas fa-chevron-down"></i></span>':'<span style="display:inline-block;width:26px;"></span>'}<span class="badge badge-light border text-monospace text-dark">${item.code}</span></td>
                                        <td class="col-desc">${item.name}${item.has_discrepancy?'<i class="fas fa-exclamation-triangle text-warning ml-1" title="Discrepancia"></i>':''}</td>
                                        ${cells}</tr>`;
                                });
                                return html;
                            }

                            function histRenderSummary(totals, periods) {
                                const numCols=periods.length;const colW=105;
                                const fmt=v=>histFmtAmt(v);
                                const mn=name=>`<th class="text-left font-weight-bold px-2" style="width:350px;min-width:350px;white-space:nowrap">${name}</th>`;
                                const pH=p=>{const[y,m]=p.split('-');return`<th class="text-right px-2" style="min-width:${colW}px;width:${colW}px;">${MONTH_NAMES[parseInt(m)-1]}-${y}</th>`;};
                                const theadRow=`<tr>${mn('Concepto')}${periods.map(pH).join('')}</tr>`;

                                // Balance General
                                const bsRows=[{label:'Total Activos (1)',key:'total_activo',cls:'text-primary'},{label:'Total Pasivos (2)',key:'total_pasivo',cls:'text-danger'},{label:'Total Patrimonio (3)',key:'total_patrimonio',cls:'text-info'},{label:'Pasivo + Patrimonio',key:'total_pasivo_patrimonio',cls:'font-weight-bold text-dark'},{label:'Diferencia',key:'diferencia',cls:'font-italic text-secondary'}];
                                let bsTbody=bsRows.map(row=>{const cells=periods.map(p=>{const val=totals[p]?totals[p][row.key]:0;return`<td class="text-right px-2 ${row.cls}">${fmt(val)}</td>`;}).join('');return`<tr><td class="font-weight-bold px-2" style="white-space:nowrap">${row.label}</td>${cells}</tr>`;}).join('');
                                $('#hist-sum-bs-thead').html(theadRow);$('#hist-sum-bs-tbody').html(bsTbody);

                                // Estado de Resultados (Acumulado)
                                const isRows=[{label:'Total Ingresos (5)',key:'total_ingresos',cls:'text-success'},{label:'Total Gastos (4)',key:'total_gastos',cls:'text-danger'},{label:'Utilidad / Pérdida Neta',key:'utilidad_neta',cls:'table-warning font-weight-bold'}];
                                let isTbody=isRows.map(row=>{const cells=periods.map(p=>{const val=totals[p]?totals[p][row.key]:0;return`<td class="text-right px-2 ${row.cls}">${fmt(val)}</td>`;}).join('');return`<tr class="${row.cls.includes('table')?row.cls:''}"><td class="font-weight-bold px-2" style="white-space:nowrap">${row.label}</td>${cells}</tr>`;}).join('');
                                $('#hist-sum-is-thead').html(theadRow);$('#hist-sum-is-tbody').html(isTbody);

                                // Estado de Resultados (Mensual)
                                const misRows=[{label:'Total Ingresos (5)',key:'total_ingresos_monthly',cls:'text-success'},{label:'Total Gastos (4)',key:'total_gastos_monthly',cls:'text-danger'},{label:'Utilidad / Pérdida Neta',key:'utilidad_neta_monthly',cls:'table-warning font-weight-bold'}];
                                let misTbody=misRows.map(row=>{const cells=periods.map(p=>{const val=totals[p]?totals[p][row.key]:0;return`<td class="text-right px-2 ${row.cls}">${fmt(val)}</td>`;}).join('');return`<tr class="${row.cls.includes('table')?row.cls:''}"><td class="font-weight-bold px-2" style="white-space:nowrap">${row.label}</td>${cells}</tr>`;}).join('');
                                $('#hist-sum-mis-thead').html(theadRow);$('#hist-sum-mis-tbody').html(misTbody);

                                // Update cuadratura badge
                                const allSquared=periods.every(p=>totals[p]&&totals[p].es_cuadrado);
                                if(allSquared){$('#hist-squareBadge').removeClass('badge-danger').addClass('badge-success').html('<i class="fas fa-check-circle mr-1"></i>Balance Cuadrado');}
                                else{$('#hist-squareBadge').removeClass('badge-success').addClass('badge-danger').html('<i class="fas fa-exclamation-triangle mr-1"></i>Descuadrado');}
                            }

                            // Tree interaction
                            window.histToggleRow = function(code, prefix) {
                                const row = $(`#${prefix}-row-${code}`);
                                if (row.hasClass('node-collapsed')) { row.removeClass('node-collapsed'); histShowChildren(code, prefix); }
                                else { row.addClass('node-collapsed'); histHideChildren(code, prefix); }
                            };
                            function histShowChildren(pc, prefix) {
                                $(`tr[data-parent="${pc}"][data-prefix="${prefix}"]`).each(function(){const r=$(this);r.show();if(!r.hasClass('node-collapsed'))histShowChildren(r.data('code'),prefix);});
                            }
                            function histHideChildren(pc, prefix) {
                                $(`tr[data-parent="${pc}"][data-prefix="${prefix}"]`).each(function(){$(this).hide();histHideChildren($(this).data('code'),prefix);});
                            }
                            window.histExpandAll = function() { $('#hist-content-wrapper .accounting-row').removeClass('node-collapsed').show(); };
                            window.histCollapseAll = function() {
                                $('#hist-content-wrapper .accounting-row').each(function(){const r=$(this);r.data('parent')!==''?r.hide():r.show();r.addClass('node-collapsed');});
                            };
                            let filterTimer;
                            window.histFilterAccounts = function() {
                                clearTimeout(filterTimer);
                                filterTimer = setTimeout(function() {
                                    const q=$('#hist-accountSearch').val().toLowerCase().trim();
                                    if(!q){histCollapseAll();return;}
                                    $('#hist-content-wrapper .accounting-row').each(function(){const r=$(this);const code=r.data('code').toString();const name=r.find('td:nth-child(2)').text().toLowerCase();const prefix=r.data('prefix');if(code.includes(q)||name.includes(q)){r.show();histRevealParents(r.data('parent'),prefix);}else{r.hide();}});
                                }, 300);
                            };
                            function histRevealParents(pc, prefix) {
                                if(!pc)return;const p=$(`#${prefix}-row-${pc}`);p.removeClass('node-collapsed').show();histRevealParents(p.data('parent'),prefix);
                            }
                        });
                        