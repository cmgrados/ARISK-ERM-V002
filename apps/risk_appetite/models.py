from django.db import models
from django.conf import settings

class RAFFramework(models.Model):
    STATE_CHOICES = (
        ('DRAFT', 'Borrador'),
        ('IN_REVIEW', 'En Revisión'),
        ('APPROVED', 'Aprobado'),
        ('EXPIRED', 'Vencido'),
        ('ARCHIVED', 'Archivado'),
    )
    code = models.CharField("Código", max_length=50, unique=True)
    name = models.CharField("Nombre del Marco", max_length=255)
    version = models.CharField("Versión", max_length=20)
    start_date = models.DateField("Fecha Inicio")
    end_date = models.DateField("Fecha Fin", null=True, blank=True)
    state = models.CharField("Estado", max_length=20, choices=STATE_CHOICES, default='DRAFT')
    description = models.TextField("Descripción", blank=True)
    approved_by = models.CharField("Aprobado por", max_length=255, blank=True)
    approval_date = models.DateField("Fecha Aprobación", null=True, blank=True)

    class Meta:
        verbose_name = "Marco de Apetito (RAF)"
        verbose_name_plural = "Marcos de Apetito (RAF)"

    def __str__(self):
        return f"{self.name} v{self.version}"

class RAFStatement(models.Model):
    POSTURE_CHOICES = (
        ('CONSERVATIVE', 'Conservador'),
        ('MODERATE', 'Moderado'),
        ('SELECTIVE', 'Selectivo'),
        ('ZERO_TOLERANCE', 'Cero Tolerancia'),
    )
    framework = models.ForeignKey(RAFFramework, on_delete=models.CASCADE, related_name='statements')
    risk_type = models.CharField("Tipo de Riesgo", max_length=100) # Could be FK to a RiskType catalog
    application_level = models.CharField("Nivel de Aplicación", max_length=100, default='Global')
    qualitative_statement = models.TextField("Declaración Cualitativa")
    risk_posture = models.CharField("Postura de Riesgo", max_length=50, choices=POSTURE_CHOICES)
    strategic_objective = models.CharField("Objetivo Estratégico", max_length=255, blank=True)
    valid_from = models.DateField("Vigencia Desde")
    valid_until = models.DateField("Vigencia Hasta", null=True, blank=True)

    class Meta:
        verbose_name = "Declaración de Apetito"
        verbose_name_plural = "Declaraciones de Apetito"

class KRICatalog(models.Model):
    KRI_LEVELS = (
        ('L1', 'Nivel 1 (Institucional)'),
        ('L2', 'Nivel 2 (Negocio/Operativo)'),
    )
    DIRECTION_CHOICES = (
        ('UP', 'Mayor es peor'),
        ('DOWN', 'Menor es peor'),
        ('RANGE', 'Fuera de Rango es peor'),
    )
    code = models.CharField("Código KRI", max_length=50, unique=True)
    name = models.CharField("Nombre", max_length=255)
    description = models.TextField("Descripción", blank=True)
    risk_type = models.CharField("Tipo de Riesgo", max_length=100)
    formula = models.TextField("Fórmula de Cálculo")
    unit = models.CharField("Unidad de Medida", max_length=50)
    frequency = models.CharField("Frecuencia", max_length=50) # Ej: Mensual, Trimestral
    data_source = models.CharField("Fuente de Datos", max_length=255)
    kri_level = models.CharField("Tipo de Indicador", max_length=10, choices=KRI_LEVELS)
    direction = models.CharField("Sentido", max_length=10, choices=DIRECTION_CHOICES)

    class Meta:
        verbose_name = "Catálogo de KRI"
        verbose_name_plural = "Catálogo de KRIs"

    def __str__(self):
        return f"{self.code} - {self.name}"

class RAFThreshold(models.Model):
    framework = models.ForeignKey(RAFFramework, on_delete=models.CASCADE, related_name='thresholds')
    kri = models.ForeignKey(KRICatalog, on_delete=models.CASCADE)
    scope_type = models.CharField("Alcance (Institución/Unidad)", max_length=100, default='Institución')
    scope_id = models.CharField("ID de Alcance", max_length=100, blank=True) # ID de Agencia, Unidad, etc.
    
    target_value = models.DecimalField("Valor Objetivo", max_digits=15, decimal_places=4)
    green_threshold = models.DecimalField("Umbral Verde (Apetito)", max_digits=15, decimal_places=4)
    yellow_threshold = models.DecimalField("Umbral Amarillo (Alerta Temprana)", max_digits=15, decimal_places=4)
    orange_threshold = models.DecimalField("Umbral Naranja (Preventivo)", max_digits=15, decimal_places=4, null=True, blank=True)
    red_threshold = models.DecimalField("Umbral Rojo (Tolerancia Excedida)", max_digits=15, decimal_places=4)
    capacity_value = models.DecimalField("Valor Capacidad Máxima", max_digits=15, decimal_places=4, null=True, blank=True)
    observation = models.TextField("Observación", blank=True)

    class Meta:
        verbose_name = "Umbral de Apetito"
        verbose_name_plural = "Umbrales de Apetito"

class KRIMeasurement(models.Model):
    SEMAPHORE_CHOICES = (
        ('GREEN', 'Verde (Objetivo)'),
        ('YELLOW', 'Amarillo (Preventiva)'),
        ('ORANGE', 'Naranja (Tolerancia Excedida)'),
        ('RED', 'Rojo (Crítica / Capacidad)'),
    )
    kri = models.ForeignKey(KRICatalog, on_delete=models.CASCADE)
    cut_off_date = models.DateField("Fecha de Corte")
    value = models.DecimalField("Valor Medido", max_digits=15, decimal_places=4)
    semaphore = models.CharField("Estado Semáforo", max_length=20, choices=SEMAPHORE_CHOICES)
    deviation = models.DecimalField("Desviación (%)", max_digits=10, decimal_places=2, default=0)
    comment = models.TextField("Comentario", blank=True)
    loaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = "Medición de KRI"
        verbose_name_plural = "Mediciones de KRIs"

class RAFBreach(models.Model):
    STATE_CHOICES = (
        ('OPEN', 'Abierto'),
        ('ANALYZING', 'En Análisis'),
        ('REMEDIATING', 'En Remediación'),
        ('CLOSED', 'Cerrado'),
    )
    measurement = models.ForeignKey(KRIMeasurement, on_delete=models.CASCADE)
    breach_type = models.CharField("Tipo de Exceso", max_length=100) # Tolerancia o Capacidad
    event_date = models.DateField("Fecha de Evento")
    severity = models.CharField("Severidad", max_length=50) # Alerta Temprana o Crítica
    cause = models.TextField("Causa")
    impact = models.TextField("Impacto")
    required_action = models.TextField("Acción Requerida")
    responsible = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    due_date = models.DateField("Fecha Compromiso")
    state = models.CharField("Estado", max_length=20, choices=STATE_CHOICES, default='OPEN')

    class Meta:
        verbose_name = "Exceso de Límite (Breach)"
        verbose_name_plural = "Excesos de Límites (Breaches)"

class RAFActionPlan(models.Model):
    breach = models.ForeignKey(RAFBreach, on_delete=models.CASCADE, related_name='action_plans')
    action = models.TextField("Acción")
    response_type = models.CharField("Tipo de Respuesta", max_length=100) # Mitigar, Aceptar, etc.
    responsible = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    start_date = models.DateField("Fecha Inicio")
    end_date = models.DateField("Fecha Fin")
    state = models.CharField("Estado", max_length=50)
    effectiveness = models.TextField("Efectividad", blank=True)

    class Meta:
        verbose_name = "Plan de Acción (RAF)"
        verbose_name_plural = "Planes de Acción (RAF)"

class RAFApproval(models.Model):
    framework = models.ForeignKey(RAFFramework, on_delete=models.CASCADE)
    instance = models.CharField("Instancia (Comité/Directorio)", max_length=100)
    approver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    date = models.DateField("Fecha")
    decision = models.CharField("Decisión", max_length=50)
    comment = models.TextField("Comentario", blank=True)

    class Meta:
        verbose_name = "Aprobación RAF"
        verbose_name_plural = "Aprobaciones RAF"

class RAFChangeLog(models.Model):
    entity = models.CharField("Entidad", max_length=100)
    entity_id = models.IntegerField("ID Entidad")
    field = models.CharField("Campo", max_length=100)
    old_value = models.TextField("Valor Anterior", blank=True)
    new_value = models.TextField("Valor Nuevo", blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField("Fecha", auto_now_add=True)
    reason = models.TextField("Motivo", blank=True)

    class Meta:
        verbose_name = "Log de Cambios RAF"
        verbose_name_plural = "Logs de Cambios RAF"
