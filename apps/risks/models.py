from django.db import models
from django.core.exceptions import ValidationError
from decimal import Decimal

class Risk(models.Model):
    RISK_CATEGORY_CHOICES = (
        ('OPERATIONAL', 'Operacional'),
        ('TECHNOLOGICAL', 'Tecnológico'),
        ('LEGAL', 'Legal'),
        ('FRAUD', 'Fraude'),
        ('CONTINUITY', 'Continuidad'),
        ('REPUTATIONAL', 'Reputacional'),
    )
    
    CRITICALITY_CHOICES = (
        ('LOW', 'Baja'),
        ('MEDIUM', 'Media'),
        ('HIGH', 'Alta'),
        ('CRITICAL', 'Crítica'),
    )

    risk_type = models.ForeignKey('catalogs.RiskType', on_delete=models.CASCADE, verbose_name="Tipo de Riesgo (Normativo)")
    category = models.CharField("Categoría", max_length=20, choices=RISK_CATEGORY_CHOICES, default='OPERATIONAL')
    
    # Hierarchical Association
    process = models.ForeignKey('catalogs.Process', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Proceso")
    subprocess = models.ForeignKey('catalogs.Subprocess', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Subproceso")
    activity = models.ForeignKey('catalogs.Activity', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Actividad")
    
    name = models.CharField("Nombre del Riesgo", max_length=255)
    description = models.TextField("Descripción Detallada", blank=True)
    
    owner = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL, null=True, related_name='owned_risks', verbose_name="Dueño del Riesgo"
    )
    
    criticallity = models.CharField("Criticidad Manual", max_length=20, choices=CRITICALITY_CHOICES, default='MEDIUM')
    
    class Meta:
        verbose_name = "Riesgo"
        verbose_name_plural = "Riesgos"

    def __str__(self):
        return f"[{self.get_category_display()}] {self.name}"

class RiskCause(models.Model):
    risk = models.ForeignKey(Risk, on_delete=models.CASCADE, related_name='causes_list')
    description = models.TextField("Descripción de la Causa")
    
    class Meta:
        verbose_name = "Causa de Riesgo"
        verbose_name_plural = "Causas de Riesgo"

    def __str__(self):
        return self.description[:50]

class RiskConsequence(models.Model):
    CONSEQUENCE_TYPE_CHOICES = (
        ('FINANCIAL', 'Financiera'),
        ('LEGAL', 'Legal'),
        ('REPUTATIONAL', 'Reputacional'),
        ('OPERATIONAL', 'Operativa'),
        ('REGULATORY', 'Regulatoria'),
    )
    
    risk = models.ForeignKey(Risk, on_delete=models.CASCADE, related_name='consequences_list')
    consequence_type = models.CharField("Tipo de Consecuencia", max_length=20, choices=CONSEQUENCE_TYPE_CHOICES)
    description = models.TextField("Descripción del Impacto")
    
    class Meta:
        verbose_name = "Consecuencia de Riesgo"
        verbose_name_plural = "Consecuencias de Riesgo"

    def __str__(self):
        return f"[{self.get_consequence_type_display()}] {self.description[:50]}"

class ProbabilityScale(models.Model):
    name = models.CharField("Nivel de Probabilidad", max_length=100)
    value = models.IntegerField("Valor Numérico (1-5)")
    description = models.TextField("Descripción / Criterio", blank=True)
    
    class Meta:
        verbose_name = "Escala de Probabilidad"
        verbose_name_plural = "Escalas de Probabilidad"
        ordering = ['value']

    def __str__(self):
        return f"{self.value} - {self.name}"

class ImpactScale(models.Model):
    name = models.CharField("Nivel de Impacto", max_length=100)
    value = models.IntegerField("Valor Numérico (1-5)")
    description = models.TextField("Descripción / Criterio", blank=True)
    
    class Meta:
        verbose_name = "Escala de Impacto"
        verbose_name_plural = "Escalas de Impacto"
        ordering = ['value']

    def __str__(self):
        return f"{self.value} - {self.name}"

class RiskMatrixConfiguration(models.Model):
    COLOR_CHOICES = (
        ('GREEN', 'Verde (Bajo)'),
        ('YELLOW', 'Amarillo (Medio)'),
        ('ORANGE', 'Naranja (Alto)'),
        ('RED', 'Rojo (Crítico)'),
    )
    
    probability = models.ForeignKey(ProbabilityScale, on_delete=models.CASCADE)
    impact = models.ForeignKey(ImpactScale, on_delete=models.CASCADE)
    severity_level = models.CharField("Nivel de Severidad", max_length=20, choices=COLOR_CHOICES)
    score = models.IntegerField("Puntaje Combinado", default=0)
    
    class Meta:
        verbose_name = "Configuración de Matriz"
        verbose_name_plural = "Configuraciones de Matriz"
        unique_together = ['probability', 'impact']

    def __str__(self):
        return f"P:{self.probability.value} x I:{self.impact.value} = {self.get_severity_level_display()}"

class RiskAssessment(models.Model):
    risk = models.ForeignKey(Risk, on_delete=models.CASCADE, related_name='assessments')
    assessment_date = models.DateField("Fecha de Evaluación", auto_now_add=True)
    
    # Riesgo Inherente (Inputs)
    inherent_probability = models.ForeignKey(ProbabilityScale, on_delete=models.PROTECT, related_name='inherent_assessments', null=True, blank=True)
    inherent_impact = models.ForeignKey(ImpactScale, on_delete=models.PROTECT, related_name='inherent_assessments', null=True, blank=True)
    
    # Riesgo Inherente (Calculado)
    inherent_score = models.IntegerField("Puntaje Inherente", editable=False, default=0)
    inherent_severity = models.CharField("Severidad Inherente", max_length=20, editable=False, blank=True)
    
    # Mitigación por Controles
    mitigation_factor = models.DecimalField("Factor de Mitigación (0-1)", max_digits=5, decimal_places=2, default=0, editable=False)
    
    # Riesgo Residual (Calculado)
    residual_score = models.DecimalField("Puntaje Residual", max_digits=10, decimal_places=2, editable=False, default=0)
    residual_severity = models.CharField("Severidad Residual", max_length=20, editable=False, blank=True)
    
    comments = models.TextField("Comentarios de Evaluación", blank=True)
    
    class Meta:
        verbose_name = "Evaluación de Riesgo"
        verbose_name_plural = "Evaluaciones de Riesgo"

    def calculate_effectiveness(self):
        controls = self.risk.controls.filter(is_active=True)
        if not controls.exists():
            return Decimal('0')
        
        # Simple average of latest effectiveness tests
        total_eff = sum(c.get_latest_effectiveness() for c in controls)
        return Decimal(str(total_eff)) / (Decimal(str(controls.count())) * 100)

    def save(self, *args, **kwargs):
        # 1. Get Inherent Score from Matrix Config
        config = RiskMatrixConfiguration.objects.filter(
            probability=self.inherent_probability,
            impact=self.inherent_impact
        ).first()
        
        if config:
            self.inherent_score = config.score
            self.inherent_severity = config.severity_level
        else:
            # Fallback to simple multiplication if no config
            self.inherent_score = self.inherent_probability.value * self.inherent_impact.value
            self.inherent_severity = 'YELLOW'

        # 2. Calculate Mitigation from Controls
        self.mitigation_factor = self.calculate_effectiveness()
        
        # 3. Calculate Residual Risk
        self.residual_score = Decimal(str(self.inherent_score)) * (Decimal('1') - self.mitigation_factor)
        
        # 4. Map Residual Score back to Severity (Approximation)
        # In a real system, we might have another matrix for residual, but we'll use thresholds here
        if self.residual_score < 5:
            self.residual_severity = 'GREEN'
        elif self.residual_score < 12:
            self.residual_severity = 'YELLOW'
        elif self.residual_score < 20:
            self.residual_severity = 'ORANGE'
        else:
            self.residual_severity = 'RED'
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Evaluación {self.risk.name} - {self.assessment_date}"
