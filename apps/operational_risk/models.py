from django.db import models
from django.utils import timezone
from decimal import Decimal

class OpRiskEventCategory(models.Model):
    name = models.CharField("Categoría de Evento", max_length=255)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Categoría de Evento Operacional"
        verbose_name_plural = "Categorías de Evento Operacional"

    def __str__(self):
        return self.name

class OpRiskIncident(models.Model):
    SEVERITY_CHOICES = (
        ('LOW', 'Bajo'),
        ('MEDIUM', 'Medio'),
        ('HIGH', 'Alto'),
        ('CRITICAL', 'Crítico'),
    )
    
    STATUS_CHOICES = (
        ('open', 'Abierto'),
        ('mitigated', 'Mitigado'),
        ('closed', 'Cerrado'),
    )
    
    title = models.CharField("Título del Evento", max_length=255)
    description = models.TextField("Descripción del Incidente")
    incident_date = models.DateField("Fecha de Ocurrencia")
    discovery_date = models.DateField("Fecha de Descubrimiento", default=timezone.now)
    
    category = models.ForeignKey(OpRiskEventCategory, on_delete=models.SET_NULL, null=True, verbose_name="Categoría Basilea")
    process = models.ForeignKey('catalogs.Process', on_delete=models.SET_NULL, null=True, verbose_name="Proceso Afectado")
    subprocess = models.ForeignKey('catalogs.Subprocess', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Subproceso Afectado")
    activity = models.ForeignKey('catalogs.Activity', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Actividad Afectada")
    
    risk = models.ForeignKey('risks.Risk', on_delete=models.SET_NULL, null=True, blank=True, related_name='incidents', verbose_name="Riesgo Asociado")
    
    severity = models.CharField("Severidad", max_length=20, choices=SEVERITY_CHOICES)
    status = models.CharField("Estado", max_length=20, choices=STATUS_CHOICES, default='open')
    
    gross_loss = models.DecimalField("Pérdida Bruta (S/)", max_digits=15, decimal_places=2, default=0)
    recovery_amount = models.DecimalField("Monto Recuperado", max_digits=15, decimal_places=2, default=0)
    net_loss = models.DecimalField("Pérdida Neta", max_digits=15, decimal_places=2, default=0, editable=False)
    
    reported_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='reported_incidents')
    
    root_cause_analysis = models.TextField("Análisis de Causa Raíz", blank=True)
    
    class Meta:
        verbose_name = "Incidente de Riesgo Operacional"
        verbose_name_plural = "Incidentes de Riesgo Operacional"

    def save(self, *args, **kwargs):
        # Calculate net loss automatically
        self.net_loss = Decimal(str(self.gross_loss or 0)) - Decimal(str(self.recovery_amount or 0))
        super().save(*args, **kwargs)

    def update_totals(self):
        """Consolidates totals from associated potential losses."""
        aggregates = self.potential_losses.exclude(
            status__in=['cancelled']
        ).aggregate(
            total_gross=models.Sum('gross_loss'),
            total_recovery=models.Sum('recovery_amount')
        )
        
        # We only update if there are linked losses, otherwise we keep manual values
        if aggregates['total_gross'] is not None:
            self.gross_loss = aggregates['total_gross']
            self.recovery_amount = aggregates['total_recovery'] or 0
            self.save()

    def __str__(self):
        return f"Incidente: {self.title} ({self.incident_date})"

class PotentialLoss(models.Model):
    STATUS_CHOICES = (
        ('preliminary', 'Preliminar'),
        ('review', 'En Revisión'),
        ('linked', 'Vinculada'),
        ('adjusted', 'Ajustada'),
        ('closed', 'Cerrada'),
        ('cancelled', 'Cancelada'),
    )
    
    CURRENCY_CHOICES = (
        ('PEN', 'Soles (S/)'),
        ('USD', 'Dólares ($)'),
    )

    PRIORITY_CHOICES = (
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
        ('critical', 'Crítica'),
    )

    code = models.CharField("Código", max_length=50, unique=True, blank=True)
    detection_date = models.DateField("Fecha de Detección", default=timezone.now)
    registration_date = models.DateTimeField("Fecha de Registro", auto_now_add=True)
    
    process = models.ForeignKey('catalogs.Process', on_delete=models.SET_NULL, null=True, verbose_name="Proceso")
    subprocess = models.ForeignKey('catalogs.Subprocess', on_delete=models.SET_NULL, null=True, verbose_name="Subproceso")
    area = models.ForeignKey('catalogs.OrganizationalUnit', on_delete=models.SET_NULL, null=True, verbose_name="Área/Unidad")
    
    loss_type = models.CharField("Tipo de Pérdida", max_length=100)
    description = models.TextField("Descripción")
    
    estimated_amount = models.DecimalField("Monto Estimado", max_digits=15, decimal_places=2)
    currency = models.CharField("Moneda", max_length=3, choices=CURRENCY_CHOICES, default='PEN')
    
    status = models.CharField("Estado", max_length=20, choices=STATUS_CHOICES, default='preliminary')
    priority = models.CharField("Prioridad", max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    responsible = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='responsible_losses')
    evidence = models.FileField("Evidencia Adjunta", upload_to='potential_losses/', blank=True, null=True)
    observations = models.TextField("Observaciones", blank=True)
    
    # Linking
    incident = models.ForeignKey(OpRiskIncident, on_delete=models.SET_NULL, null=True, blank=True, related_name='potential_losses', verbose_name="Evento Relacionado")
    linking_date = models.DateTimeField("Fecha de Vinculación", null=True, blank=True)
    
    # Financial consolidation
    recovery_amount = models.DecimalField("Monto Recuperado", max_digits=15, decimal_places=2, default=0)
    gross_loss = models.DecimalField("Monto Bruto Final", max_digits=15, decimal_places=2, default=0)
    net_loss = models.DecimalField("Monto Neto", max_digits=15, decimal_places=2, default=0, editable=False)
    
    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='created_losses')
    updated_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='updated_losses')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Posible Pérdida"
        verbose_name_plural = "Posibles Pérdidas"

    def save(self, *args, **kwargs):
        if not self.code:
            year = self.detection_date.year
            # Using a simple count for now, in a real environment we'd use a more robust sequence
            count = PotentialLoss.objects.filter(detection_date__year=year).count() + 1
            self.code = f"PP-{year}-{count:04d}"
        
        self.net_loss = Decimal(str(self.gross_loss or 0)) - Decimal(str(self.recovery_amount or 0))
        super().save(*args, **kwargs)
        
        if self.incident:
            self.incident.update_totals()

    def __str__(self):
        return f"{self.code} - {self.loss_type} ({self.estimated_amount})"

class PotentialLossAudit(models.Model):
    loss = models.ForeignKey(PotentialLoss, on_delete=models.CASCADE, related_name='audit_log')
    user = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=100) # Created, Updated, Linked, etc.
    field_name = models.CharField(max_length=100, blank=True)
    old_value = models.TextField(blank=True)
    new_value = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
class COSOComponent(models.Model):
    name = models.CharField("Componente COSO", max_length=255)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Componente COSO"
        verbose_name_plural = "Componentes COSO"
        ordering = ['order']

    def __str__(self):
        return self.name

class COSOPrinciple(models.Model):
    component = models.ForeignKey(COSOComponent, on_delete=models.CASCADE, related_name='principles')
    code = models.CharField("Código", max_length=10)
    name = models.CharField("Principio", max_length=255)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Principio COSO"
        verbose_name_plural = "Principios COSO"
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"

class COSOAssessment(models.Model):
    SCORE_CHOICES = (
        (4, 'Muy Favorable'),
        (3, 'Favorable'),
        (2, 'Poco Favorable'),
        (1, 'Sin Registro'),
    )
    
    principle = models.ForeignKey(COSOPrinciple, on_delete=models.CASCADE, related_name='assessments')
    evaluation_date = models.DateField("Fecha de Evaluación", default=timezone.now)
    score = models.IntegerField("Nivel de Madurez", choices=SCORE_CHOICES, default=1)
    evidence = models.TextField("Evidencia / Sustento", blank=True)
    gap_analysis = models.TextField("Análisis de Brechas", blank=True)
    assessed_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = "Evaluación COSO"
        verbose_name_plural = "Evaluaciones COSO"
        unique_together = ['principle', 'evaluation_date']

    def __str__(self):
        return f"Eval {self.principle.code} - {self.evaluation_date}"

class RiskManagementStep(models.Model):
    name = models.CharField("Nombre de la Etapa", max_length=100)
    description = models.CharField("Descripción Corta", max_length=255)
    instruction = models.TextField("Instrucciones Detalladas (Manual)")
    url_name = models.CharField("Nombre de la URL (Django)", max_length=100)
    order = models.PositiveIntegerField("Orden", default=0)
    icon = models.CharField("Icono FontAwesome", max_length=50, default="fas fa-step-forward")
    
    class Meta:
        verbose_name = "Etapa del Ciclo de Gestión"
        verbose_name_plural = "Etapas del Ciclo de Gestión"
        ordering = ['order']

    def __str__(self):
        return f"{self.order}. {self.name}"

class RiskCycleSnapshot(models.Model):
    snapshot_date = models.DateField("Fecha de Cierre", default=timezone.now)
    cycle_name = models.CharField("Nombre del Ciclo/Mes", max_length=100)
    
    maturity_pct = models.DecimalField("Nivel de Madurez (%)", max_digits=5, decimal_places=2)
    avg_residual_score = models.DecimalField("Riesgo Residual Promedio", max_digits=5, decimal_places=2)
    high_risks_count = models.IntegerField("Cant. Riesgos Críticos")
    total_gross_loss = models.DecimalField("Pérdida Bruta Acumulada", max_digits=15, decimal_places=2)
    plan_compliance_pct = models.DecimalField("Cumplimiento de Planes (%)", max_digits=5, decimal_places=2)
    
    comments = models.TextField("Observaciones del Cierre", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Snapshot de Ciclo de Riesgo"
        verbose_name_plural = "Snapshots de Ciclo de Riesgo"
        ordering = ['-snapshot_date']

    def __str__(self):
        return f"Snapshot {self.cycle_name} ({self.snapshot_date})"
