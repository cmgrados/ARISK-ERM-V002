from django.db import models

class ComplianceRequirement(models.Model):
    SOURCE_CHOICES = (
        ('SBS', 'SBS - Superintendencia de Banca y Seguros'),
        ('SUNAT', 'SUNAT - Administración Tributaria'),
        ('UIF', 'UIF-Perú - Inteligencia Financiera'),
        ('INDECOPI', 'INDECOPI - Protección al Consumidor'),
        ('SUNAFIL', 'SUNAFIL - Fiscalización Laboral'),
        ('PRIVACIDAD', 'Protección de Datos Personales'),
        ('INTERNA', 'Políticas Internas / Otros'),
    )
    description = models.TextField("Descripción del Requisito")
    source = models.CharField("Fuente / Ente Sancionador", max_length=20, choices=SOURCE_CHOICES)
    responsible_area = models.ForeignKey(
        'catalogs.OrganizationalUnit', 
        on_delete=models.SET_NULL, 
        null=True, 
        verbose_name="Área Responsable"
    )
    potential_sanction = models.TextField("Sanción Potencial (Multas/Medidas)", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Obligación de Cumplimiento"
        verbose_name_plural = "Obligaciones de Cumplimiento"

    def __str__(self):
        return f"{self.get_source_display()}: {self.description[:50]}..."

class ComplianceRisk(models.Model):
    FREQUENCY_CHOICES = (
        ('MONTHLY', 'Mensual'),
        ('QUARTERLY', 'Trimestral'),
        ('SEMIANNUAL', 'Semestral'),
        ('ANNUAL', 'Anual'),
    )
    requirement = models.ForeignKey(
        ComplianceRequirement, 
        on_delete=models.CASCADE, 
        related_name='risks',
        verbose_name="Requisito"
    )
    
    # Inherent Risk
    inherent_probability = models.IntegerField("Probabilidad Inherente (1-5)", default=3)
    inherent_impact = models.IntegerField("Impacto Inherente (1-5)", default=3)
    
    # Controls
    existing_controls = models.TextField("Controles existentes", blank=True)
    
    # Residual Risk
    residual_probability = models.IntegerField("Probabilidad Residual (1-5)", default=2)
    residual_impact = models.IntegerField("Impacto Residual (1-5)", default=2)
    
    # Monitoring
    indicator = models.TextField("Indicador de cumplimiento", blank=True)
    monitoring_frequency = models.CharField(
        "Frecuencia de monitoreo", 
        max_length=20, 
        choices=FREQUENCY_CHOICES, 
        default='MONTHLY'
    )
    evaluation_period = models.CharField(
        "Periodo de evaluación", 
        max_length=100, 
        help_text="Ej: 2026",
        default="2026"
    )

    class Meta:
        verbose_name = "Riesgo de Cumplimiento"
        verbose_name_plural = "Matriz de Riesgos de Cumplimiento"

    @property
    def inherent_risk_value(self):
        return self.inherent_probability * self.inherent_impact

    def get_risk_category(self, value):
        if value <= 4: return 'Muy Bajo'
        if value <= 9: return 'Bajo'
        if value <= 14: return 'Medio'
        if value <= 19: return 'Alto'
        return 'Muy Alto'

    def get_risk_color(self, value):
        if value <= 4: return '#28a745'  # Green
        if value <= 9: return '#8dc63f'  # Light Green
        if value <= 14: return '#ffc107' # Yellow
        if value <= 19: return '#fd7e14' # Orange
        return '#dc3545'                # Red

    @property
    def inherent_risk_category(self):
        return self.get_risk_category(self.inherent_risk_value)

    @property
    def inherent_risk_color(self):
        return self.get_risk_color(self.inherent_risk_value)

    @property
    def residual_risk_value(self):
        return self.residual_probability * self.residual_impact

    @property
    def residual_risk_category(self):
        return self.get_risk_category(self.residual_risk_value)

    @property
    def residual_risk_color(self):
        return self.get_risk_color(self.residual_risk_value)

    @property
    def compliance_status(self):
        findings = self.findings.all()
        if not findings: return 'GREEN'
        if findings.filter(state='OPEN').exists(): return 'RED'
        if findings.filter(state='IN_PROGRESS').exists(): return 'YELLOW'
        return 'GREEN'

    @property
    def compliance_status_color(self):
        colors = {'RED': '#dc3545', 'YELLOW': '#ffc107', 'GREEN': '#28a745'}
        return colors.get(self.compliance_status)

    @property
    def compliance_status_label(self):
        labels = {'RED': 'INCUMPLE', 'YELLOW': 'PARCIAL', 'GREEN': 'CUMPLE'}
        return labels.get(self.compliance_status)

    def __str__(self):
        return f"Riesgo: {self.requirement.description[:30]}..."

class ComplianceFinding(models.Model):
    STATE_CHOICES = (
        ('OPEN', 'Abierto'),
        ('IN_PROGRESS', 'En Progreso'),
        ('CLOSED', 'Cerrado'),
    )
    risk = models.ForeignKey(
        ComplianceRisk, 
        on_delete=models.CASCADE, 
        related_name='findings', 
        verbose_name="Riesgo Asociado"
    )
    description = models.TextField("Descripción del Hallazgo")
    state = models.CharField("Estado", max_length=20, choices=STATE_CHOICES, default='OPEN')
    due_date = models.DateField("Fecha Límite de Subsanación")
    responsible = models.ForeignKey(
        'users.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        verbose_name="Responsable"
    )
    
    class Meta:
        verbose_name = "Hallazgo de Cumplimiento"
        verbose_name_plural = "Hallazgos de Cumplimiento"
        
    def __str__(self):
        return f"Hallazgo: {self.risk.requirement.description[:20]}..."
