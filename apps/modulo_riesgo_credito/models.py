from django.db import models
from credit_risk.models import CreditOperation
from users.models import User

class RiskClassification(models.Model):
    operation = models.ForeignKey(CreditOperation, on_delete=models.CASCADE, related_name='historical_classifications')
    cut_off_date = models.DateField("Fecha de Corte", db_index=True)
    
    # Bucket y Clasificación de la SBS
    bucket = models.CharField("Bucket de Mora", max_length=50)
    days_past_due = models.IntegerField("Días de Mora", default=0)
    sbs_classification = models.CharField("Clasificación SBS", max_length=50)
    
    # Resultados Analíticos de ese mes
    pd = models.DecimalField("PD (%)", max_digits=7, decimal_places=4, default=0)
    lgd = models.DecimalField("LGD (%)", max_digits=7, decimal_places=4, default=0)
    ead = models.DecimalField("EAD", max_digits=15, decimal_places=2, default=0)
    expected_loss = models.DecimalField("Pérdida Esperada", max_digits=15, decimal_places=2, default=0)
    
    # Provisiones Constituidas/Calculadas
    required_provision = models.DecimalField("Provisión Requerida", max_digits=15, decimal_places=2, default=0)
    
    # Snapshot properties para trazabilidad estática
    snapshot_data = models.JSONField("Snapshot Variables", default=dict, blank=True, help_text="Datos estáticos al momento del cálculo (tasas vigentes, garantías)")
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Clasificación Histórica de Riesgo"
        verbose_name_plural = "Clasificaciones Históricas de Riesgo"
        unique_together = ('operation', 'cut_off_date')

    def __str__(self):
        return f"{self.operation.operation_code} - {self.cut_off_date} - {self.sbs_classification}"

class VintageCohort(models.Model):
    disbursement_month = models.DateField("Mes de Cosecha", db_index=True)
    cut_off_date = models.DateField("Fecha de Corte de Medición", db_index=True)
    total_disbursed = models.DecimalField("Monto Desembolsado Total", max_digits=18, decimal_places=2, default=0)
    outstanding_balance = models.DecimalField("Saldo Vigente", max_digits=18, decimal_places=2, default=0)
    past_due_balance = models.DecimalField("Saldo Vencido (>30 días)", max_digits=18, decimal_places=2, default=0)
    npl_ratio = models.DecimalField("Ratio de Mora (%)", max_digits=7, decimal_places=4, default=0)

    class Meta:
        verbose_name = "Cohorte de Cosecha (Vintage)"
        verbose_name_plural = "Cohortes de Cosecha (Vintage)"
        unique_together = ('disbursement_month', 'cut_off_date')

    def __str__(self):
        return f"Cosecha {self.disbursement_month.strftime('%Y-%m')} en {self.cut_off_date.strftime('%Y-%m')}"

class TransitionMatrix(models.Model):
    from_date = models.DateField("Desde Fecha")
    to_date = models.DateField("Hasta Fecha")
    from_category = models.CharField("Categoría Origen", max_length=50)
    to_category = models.CharField("Categoría Destino", max_length=50)
    probability = models.DecimalField("Probabilidad Transición (%)", max_digits=7, decimal_places=4, default=0)
    
    class Meta:
        verbose_name = "Matriz de Transición"
        verbose_name_plural = "Matrices de Transición"
        unique_together = ('from_date', 'to_date', 'from_category', 'to_category')

    def __str__(self):
        return f"{self.from_date} -> {self.to_date}: {self.from_category} a {self.to_category} ({self.probability}%)"

class OverridingLog(models.Model):
    operation = models.ForeignKey(CreditOperation, on_delete=models.CASCADE, related_name='overridings')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date_applied = models.DateTimeField(auto_now_add=True)
    original_classification = models.CharField("Clasificación Original", max_length=50)
    new_classification = models.CharField("Nueva Clasificación", max_length=50)
    justification = models.TextField("Sustento Técnico")
    cut_off_date = models.DateField("Fecha de Corte de Aplicación")

    class Meta:
        verbose_name = "Ajuste por Excepción (Overriding)"
        verbose_name_plural = "Ajustes por Excepción (Overriding)"

    def __str__(self):
        return f"Excepción {self.operation.operation_code} por {self.user.username if self.user else 'N/A'}"

class AlertaActiva(models.Model):
    operation = models.ForeignKey(CreditOperation, on_delete=models.CASCADE, related_name='active_alerts')
    alert_type = models.CharField("Tipo de Alerta", max_length=100)
    description = models.TextField("Descripción de la Alerta")
    date_detected = models.DateField("Fecha Detectada", auto_now_add=True)
    is_resolved = models.BooleanField("Resuelta", default=False)
    severity = models.CharField("Severidad", max_length=20, choices=[
        ('ALTA', 'Alta'),
        ('MEDIA', 'Media'),
        ('BAJA', 'Baja')
    ], default='MEDIA')

    class Meta:
        verbose_name = "Alerta Temprana Activa"
        verbose_name_plural = "Alertas Tempranas Activas"

    def __str__(self):
        return f"Alerta {self.severity} en {self.operation.operation_code}: {self.alert_type}"
