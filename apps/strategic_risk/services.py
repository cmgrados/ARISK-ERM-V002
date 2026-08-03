from decimal import Decimal
try:
    from simpleeval import simple_eval
except ImportError:
    # Fallback: use eval (less safe, will be replaced later)
    simple_eval = eval

class BSCCalculationEngine:
    @staticmethod
    def evaluate_formula(formula_str, variables_dict):
        """
        Evalúa una fórmula de texto de forma segura.
        Ejemplo: formula_str = "(resultado_real / meta_programada) * 100"
                 variables_dict = {"resultado_real": 85, "meta_programada": 100}
        """
        try:
            # simple_eval bloquea acceso a funciones del sistema y variables no explícitas
            resultado = simple_eval(formula_str, names=variables_dict)
            return Decimal(str(resultado))
        except Exception as e:
            raise ValueError(f"Error al evaluar la fórmula del indicador: {str(e)}")

    @staticmethod
    def process_meta_periodo(meta_periodo_instance):
        """
        Calcula el porcentaje de cumplimiento y asigna el semáforo a una MetaPeriodo.
        Se debe llamar antes de guardar (pre-save) o desde el API Endpoint.
        """
        if meta_periodo_instance.resultado_real is None:
            return meta_periodo_instance # No se puede calcular sin resultado

        # 1. Preparar las variables para la fórmula
        variables = {
            "resultado_real": float(meta_periodo_instance.resultado_real),
            "meta_programada": float(meta_periodo_instance.meta_programada),
            "linea_base": float(meta_periodo_instance.indicador.linea_base)
        }

        # 2. Calcular % de cumplimiento basado en la fórmula del indicador
        formula = meta_periodo_instance.indicador.formula
        if not formula:
            # Fórmula por defecto si está vacío
            formula = "(resultado_real / meta_programada) * 100"

        porcentaje = BSCCalculationEngine.evaluate_formula(formula, variables)
        meta_periodo_instance.porcentaje_cumplimiento = round(porcentaje, 2)

        # 3. Asignar Semáforo
        if porcentaje < 80:
            meta_periodo_instance.semaforo = 'Rojo'
        elif 80 <= porcentaje <= 95:
            meta_periodo_instance.semaforo = 'Amarillo'
        else:
            meta_periodo_instance.semaforo = 'Verde'

        return meta_periodo_instance

from django.db.models import Avg, Count, Sum, F, Q
from .models import MetaPeriodo, ProyectoIniciativa, EjecucionPresupuestaria
from financial_planning.models import BalanceDetalle, PeriodoFinanciero

class DashboardService:
    @staticmethod
    def get_dashboard_summary(organization):
        # 1. Salud Estratégica: Usar aggregate para evitar N+1
        metas = MetaPeriodo.objects.filter(indicador__organization=organization).exclude(resultado_real__isnull=True)
        promedio_cumplimiento = metas.aggregate(promedio=Avg('porcentaje_cumplimiento'))['promedio'] or 0
        
        semaforos_count = metas.values('semaforo').annotate(total=Count('id'))
        semaforos_dict = {item['semaforo']: item['total'] for item in semaforos_count if item['semaforo']}
        
        # 2. Salud Operativa: Usar consultas eficientes
        proyectos = ProyectoIniciativa.objects.filter(organization=organization).exclude(estado='COMPLETADO')
        total_proyectos = proyectos.count()
        
        proyectos_rojo = proyectos.filter(semaforo_ejecucion='Rojo').values(
            'codigo', 'nombre', 'porcentaje_avance_fisico', 'porcentaje_avance_financiero'
        )
        
        # Desviación global = Suma de (programado - real) de ejecuciones de proyectos no completados
        ejecuciones = EjecucionPresupuestaria.objects.filter(proyecto__in=proyectos)
        desviacion_global = ejecuciones.aggregate(
            desviacion=Sum(F('gasto_programado') - F('gasto_real'))
        )['desviacion'] or 0
        
        # 3. Salud Financiera: Buscar el último periodo definitivo
        ultimo_periodo = PeriodoFinanciero.objects.filter(
            organization=organization, estado='FINAL'
        ).order_by('-anio', '-mes').first()
        
        financiero_resumen = {}
        if ultimo_periodo:
            detalles = BalanceDetalle.objects.filter(periodo=ultimo_periodo).select_related('cuenta')
            activos = detalles.filter(cuenta__tipo='ACTIVO').aggregate(total=Sum('monto'))['total'] or 0
            pasivos = detalles.filter(cuenta__tipo='PASIVO').aggregate(total=Sum('monto'))['total'] or 0
            patrimonio = detalles.filter(cuenta__tipo='PATRIMONIO').aggregate(total=Sum('monto'))['total'] or 0
            
            financiero_resumen = {
                'periodo': f"{ultimo_periodo.mes:02d}/{ultimo_periodo.anio}",
                'activos': float(activos),
                'pasivos': float(pasivos),
                'patrimonio': float(patrimonio),
                'ecuacion_cuadrada': float(activos) == float(pasivos + patrimonio)
            }
            
        return {
            "salud_estrategica": {
                "promedio_cumplimiento_global": float(round(promedio_cumplimiento, 2)),
                "semaforos": semaforos_dict
            },
            "salud_operativa": {
                "proyectos_en_curso": total_proyectos,
                "desviacion_presupuesto_global": float(round(desviacion_global, 2)),
                "proyectos_en_riesgo": list(proyectos_rojo)
            },
            "salud_financiera": financiero_resumen
        }
