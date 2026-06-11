import os

filepath = r'c:\Users\VICTUS\Desktop\A.RISK ERM\templates\financial_planning\wizard.html'
with open(filepath, 'r', encoding='utf-8') as f:
    text = f.read()

target_marker = '                        success: function(res) {'
idx = text.rfind(target_marker)
if idx == -1:
    print('marker not found')
else:
    new_text = text[:idx] + '''                        success: function(res) {
                            clearInterval(animationInterval);
                            if(res.status === 'success') {
                                mcDataObj = res.data;
                                updateDashboard(); // updates both chart and table with final data
                            } else {
                                alert("Error en Montecarlo: " + res.msg);
                            }
                        },
                        error: function() {
                            clearInterval(animationInterval);
                            alert("Error de conexión al generar Montecarlo");
                        },
                        complete: function() {
                            btn.html(originalHtml);
                            btn.prop('disabled', false);
                        }
                    });
                });
                
                selectAgency.on('change', function() {
                    currentAgency = $(this).val();
                    updateVariablesUI(currentAgency);
                    updateDashboard();
                });
                
                $('.trend-period-btn').on('click', function() {
                    $('.trend-period-btn').removeClass('active');
                    $(this).addClass('active');
                    currentPeriod = parseInt($(this).data('months'));
                    updateDashboard();
                });
            } else {
                $('#trend-loading').html('<div class="alert alert-danger">Error al cargar datos: ' + response.msg + '</div>');
            }
        },
        error: function() {
            $('#trend-loading').html('<div class="alert alert-danger">Error de conexión al cargar las tendencias.</div>');
        }
    });
}

$(document).ready(function() {
    loadTrendData();
});
{% endif %}

function filterERByYear(year) {
    // update tab styles
    document.querySelectorAll('#erTabs .nav-link').forEach(t => {
        t.classList.remove('active', 'font-weight-bold', 'text-primary');
        t.classList.add('text-muted');
        t.style.backgroundColor = '#f8f9fa';
    });
    const activeTab = document.getElementById('er-' + year + '-tab');
    if(activeTab) {
        activeTab.classList.add('active', 'font-weight-bold', 'text-primary');
        activeTab.classList.remove('text-muted');
        activeTab.style.backgroundColor = '#fff';
    }

    const table = document.getElementById('erTable');
    if (!table) return;

    // get headers
    const ths = table.querySelectorAll('thead th');
    const colsToShow = [];
    ths.forEach((th, index) => {
        if (index === 0) {
            colsToShow.push(index); // Always show Concepto
            return;
        }
        const text = th.innerText.trim();
        const colYear = text.split('-')[0];
        if (year === 'all' || colYear === year) {
            colsToShow.push(index);
            th.style.display = '';
        } else {
            th.style.display = 'none';
        }
    });

    // apply to all rows
    const rows = table.querySelectorAll('tbody tr');
    rows.forEach(row => {
        const tds = row.querySelectorAll('td');
        tds.forEach((td, index) => {
            if (colsToShow.includes(index)) {
                td.style.display = '';
            } else {
                td.style.display = 'none';
            }
        });
    });
}

document.addEventListener('DOMContentLoaded', function() {
    {% if step == 7 and projected_years %}
    filterERByYear('{{ projected_years.0 }}');
    {% endif %}
});
</script>
{% endblock %}
'''
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_text)
    print('File written successfully.')
