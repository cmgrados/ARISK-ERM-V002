with open('templates/financial_planning/projected_balance.html', 'r', encoding='utf-8') as f:
    content = f.read()

new_btn = '''                <div class="dropdown mr-2">
                    <button class="btn btn-sm btn-outline-info font-weight-bold rounded-pill shadow-sm" type="button" onclick="applyOtherTrends()" title="Calcular tendencia de cuentas restantes (12 meses)">
                        <i class="fas fa-magic mr-1"></i> Auto Tendencia Restantes
                    </button>
                </div>
                <div class="dropdown mr-2">
                    <button class="btn btn-sm btn-outline-primary font-weight-bold rounded-pill shadow-sm" type="button" onclick="openBGAdjustmentModal()">
                        <i class="fas fa-edit mr-1"></i> Agregar Ajuste
                    </button>'''

content = content.replace('''                <div class="dropdown mr-2">
                    <button class="btn btn-sm btn-outline-primary font-weight-bold rounded-pill shadow-sm" type="button" onclick="openBGAdjustmentModal()">
                        <i class="fas fa-edit mr-1"></i> Agregar Ajuste
                    </button>''', new_btn)

js_code = '''
// API call to apply trends to remaining accounts
function applyOtherTrends() {
    Swal.fire({
        title: 'Aplicar Tendencia Automática',
        text: '¿Deseas calcular y aplicar la tendencia histórica mensual a todas las cuentas que no están parametrizadas en Montecarlo ni Presupuesto? Esto modificará los Ajustes Manuales de forma automática para los 36 meses en todos los escenarios.',
        icon: 'question',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Sí, aplicar',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        if (result.isConfirmed) {
            Swal.fire({
                title: 'Calculando...',
                text: 'Analizando variaciones de 12 meses, por favor espera.',
                allowOutsideClick: false,
                didOpen: () => { Swal.showLoading(); }
            });
            
            fetch(`/financial-planning/plan/${planId}/api/apply_other_trends/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    Swal.fire('¡Éxito!', data.message, 'success');
                    loadProjectedBalanceData();
                } else {
                    Swal.fire('Error', data.error || 'Ocurrió un error', 'error');
                }
            })
            .catch(error => {
                console.error("Error al aplicar tendencias:", error);
                Swal.fire('Error', 'Problema de conexión al aplicar tendencias', 'error');
            });
        }
    });
}
'''

content = content.replace('function openBGAdjustmentModal() {', js_code + '\nfunction openBGAdjustmentModal() {')

with open('templates/financial_planning/projected_balance.html', 'w', encoding='utf-8') as f:
    f.write(content)
