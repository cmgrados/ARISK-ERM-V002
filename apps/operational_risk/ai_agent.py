import json
from django.db.models import Sum, Avg, Count
from django.utils import timezone
from .models import COSOAssessment, OpRiskIncident, PotentialLoss, RiskManagementStep
from risks.models import Risk, RiskAssessment
from action_plans.models import ActionPlan

class OperationalRiskAIAgent:
    """
    AI Agent specialized in Operational Risk for Financial Institutions.
    Knowledge base: COSO II/III, Basel III, SBS (Peru) equivalent standards.
    """

    def __init__(self):
        self.context = {}
        self.knowledge_base = {
            "financial_benchmarks": {
                "max_gross_loss_pct_equity": 0.05,  # 5% of regulatory capital
                "min_plan_compliance": 80.0,      # Minimum healthy compliance
                "high_risk_threshold": 15,         # Residual score threshold
            },
            "coso_principles": {
                "Control Environment": "Base of all other components. If maturity < 60%, RCSA is unreliable.",
                "Risk Assessment": "Must identify external and internal factors.",
                "Control Activities": "Must include segregation of duties and dual control in financial transactions.",
                "Information & Communication": "Timely reporting of incidents to the Board.",
                "Monitoring": "Continuous evaluation of control effectiveness."
            }
        }

    def get_institutional_status(self):
        """Analyze the current state of the institution's risk cycle."""
        # 1. Maturity Analysis
        avg_coso = COSOAssessment.objects.aggregate(Avg('score'))['score__avg'] or 1
        maturity_pct = (avg_coso / 4) * 100
        
        # 2. Risk Matrix Health
        op_risks = Risk.objects.filter(risk_type__code='OP')
        evaluated_risks = RiskAssessment.objects.filter(risk__in=op_risks).count()
        total_op_risks = op_risks.count()
        coverage_pct = (evaluated_risks / total_op_risks * 100) if total_op_risks > 0 else 0
        
        # 3. Incident Performance
        total_loss = OpRiskIncident.objects.aggregate(Sum('net_loss'))['net_loss__sum'] or 0
        
        # 4. Action Plan Compliance
        plans = ActionPlan.objects.filter(risk__risk_type__code='OP')
        compliance = (plans.filter(status='completed').count() / plans.count() * 100) if plans.exists() else 0

        return {
            "maturity_pct": maturity_pct,
            "coverage_pct": coverage_pct,
            "total_loss": total_loss,
            "compliance": compliance,
            "risk_inventory": total_op_risks
        }

    def generate_recommendations(self):
        """Generate expert recommendations based on the data."""
        stats = self.get_institutional_status()
        recommendations = []

        # Rule 1: COSO Foundation
        if stats['maturity_pct'] < 70:
            recommendations.append({
                "level": "CRITICAL",
                "area": "COSO - Entorno de Control",
                "insight": "La madurez de control es baja ({}%). Según COSO III, un entorno de control débil invalida la confianza en los autocontroles declarados en el RCSA.".format(round(stats['maturity_pct'], 1)),
                "action": "Priorizar la capacitación en cultura de riesgo para la Alta Gerencia y mandos medios."
            })

        # Rule 2: Risk Inventory Integrity
        if stats['coverage_pct'] < 90:
            recommendations.append({
                "level": "WARNING",
                "area": "Identificación RCSA",
                "insight": "Existen {} riesgos operativos sin evaluación RCSA vigente.".format(stats['risk_inventory'] - stats['coverage_pct']),
                "action": "Completar la evaluación de riesgos inherentes y controles para el inventario completo antes del próximo cierre trimestral."
            })

        # Rule 3: Incident correlation
        critical_incidents = OpRiskIncident.objects.filter(severity='CRITICAL', status='open').count()
        if critical_incidents > 0:
            recommendations.append({
                "level": "DANGER",
                "area": "Eventos de Pérdida",
                "insight": "Se detectaron {} incidentes CRÍTICOS abiertos. Esto indica una posible falla sistemática en los controles preventivos.".format(critical_incidents),
                "action": "Realizar un análisis de Causa Raíz (Root Cause Analysis) y actualizar la matriz de riesgos en los procesos afectados."
            })

        # Rule 4: Financial Industry Specific (Action Plans)
        overdue_plans = ActionPlan.objects.filter(risk__risk_type__code='OP', status='overdue').count()
        if overdue_plans > 3:
            recommendations.append({
                "level": "WARNING",
                "area": "Mitigación y Planes",
                "insight": "El retraso en planes de acción en el sector financiero eleva la probabilidad de sanciones regulatorias y pérdidas operativas recurrentes.",
                "action": "Reasignar recursos o extender plazos justificadamente para los {} planes vencidos.".format(overdue_plans)
            })

        return recommendations

    def chat(self, query):
        """Interactive chat logic to respond to user questions."""
        query = query.lower()
        stats = self.get_institutional_status()
        
        # Responses for Maturity
        if any(word in query for word in ["madurez", "coso", "estado"]):
            return "Su madurez actual es del {}%. Según COSO III, esto nos sitúa en un nivel {}. {}".format(
                round(stats['maturity_pct'], 1),
                "Sólido" if stats['maturity_pct'] > 75 else "Medio/Bajo",
                "He detectado que el componente de 'Entorno de Control' necesita reforzarse." if stats['maturity_pct'] < 70 else "Los controles preventivos están bien estructurados."
            )
            
        # Responses for Incidents/Losses
        if any(word in query for word in ["incidente", "pérdida", "evento", "perdi"]):
            return "Hasta hoy, hemos registrado S/ {} en pérdidas netas. Tenemos {} riesgos operativos identificados. Recomiendo revisar los incidentes con severidad 'Crítica' que aún permanecen abiertos.".format(
                stats['total_loss'],
                stats['risk_inventory']
            )

        # Responses for Action Plans
        if any(word in query for word in ["plan", "acción", "mitigación", "pendiente"]):
            overdue = ActionPlan.objects.filter(risk__risk_type__code='OP', status='overdue').count()
            return "El cumplimiento de planes es del {}%. Actualmente existen {} acciones vencidas. En el sector bancario, esto es una alerta roja para los reguladores.".format(
                round(stats['compliance'], 1),
                overdue
            )

        # Default fallback
        return "Soy su asistente experto en COSO y Riesgo Operacional. Puedo analizar su madurez institucional, el estado de sus planes de acción o el impacto de sus incidentes de pérdida. ¿En qué área específica desea profundizar?"

    def generate_executive_summary(self):
        """Generate a narrative summary for the Board."""
        stats = self.get_institutional_status()
        recs = self.generate_recommendations()
        
        summary = "Basado en el análisis de los 8 pasos del ciclo de gestión, la entidad presenta una madurez del {}%.".format(round(stats['maturity_pct'], 1))
        
        if stats['compliance'] < 50:
            summary += " Se observa una brecha significativa en la ejecución de planes de mitigación."
        else:
            summary += " La gestión de mitigación se mantiene en niveles aceptables."
            
        return {
            "narrative": summary,
            "top_priority": recs[0] if recs else None,
            "all_insights": recs
        }
