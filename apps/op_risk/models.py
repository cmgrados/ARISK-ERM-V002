from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Macroprocess(models.Model):
    name = models.CharField(max_length=150, unique=True, verbose_name="Macroproceso")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")
    owner_position = models.ForeignKey('catalogs.Position', on_delete=models.SET_NULL, null=True, blank=True, related_name='oprisk_macroprocesses', verbose_name="Cargo Dueño")
    owner_area = models.ForeignKey('catalogs.OrganizationalUnit', on_delete=models.SET_NULL, null=True, blank=True, related_name='oprisk_macroprocesses_area', verbose_name="Área Dueña")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Macroproceso"
        verbose_name_plural = "Macroprocesos"
        ordering = ['name']

    def __str__(self):
        return self.name

class Process(models.Model):
    CRITICALITY_CHOICES = [
        ('ALTA', 'Alta'),
        ('MEDIA', 'Media'),
        ('BAJA', 'Baja'),
    ]
    macroprocess = models.ForeignKey(Macroprocess, on_delete=models.CASCADE, related_name='processes', verbose_name="Macroproceso")
    name = models.CharField(max_length=150, verbose_name="Proceso")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")
    criticality = models.CharField(max_length=20, choices=CRITICALITY_CHOICES, default='MEDIA', verbose_name="Criticidad")
    owner_position = models.ForeignKey('catalogs.Position', on_delete=models.SET_NULL, null=True, blank=True, related_name='oprisk_processes', verbose_name="Cargo Dueño")
    owner_area = models.ForeignKey('catalogs.OrganizationalUnit', on_delete=models.SET_NULL, null=True, blank=True, related_name='oprisk_processes_area', verbose_name="Área Dueña")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Proceso"
        verbose_name_plural = "Procesos"
        ordering = ['macroprocess', 'name']

    def __str__(self):
        return f"{self.macroprocess.name} - {self.name}"

class Subprocess(models.Model):
    process = models.ForeignKey(Process, on_delete=models.CASCADE, related_name='subprocesses', verbose_name="Proceso")
    name = models.CharField(max_length=150, verbose_name="Subproceso")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")
    owner_position = models.ForeignKey('catalogs.Position', on_delete=models.SET_NULL, null=True, blank=True, related_name='oprisk_subprocesses', verbose_name="Cargo Dueño")
    owner_area = models.ForeignKey('catalogs.OrganizationalUnit', on_delete=models.SET_NULL, null=True, blank=True, related_name='oprisk_subprocesses_area', verbose_name="Área Dueña")
    class Meta:
        verbose_name = "Subproceso"
        verbose_name_plural = "Subprocesos"
        
    def __str__(self):
        return f"{self.process.name} > {self.name}"

class Activity(models.Model):
    subprocess = models.ForeignKey(Subprocess, on_delete=models.CASCADE, related_name='activities', verbose_name="Subproceso")
    name = models.CharField(max_length=150, verbose_name="Actividad")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")
    owner_position = models.ForeignKey('catalogs.Position', on_delete=models.SET_NULL, null=True, blank=True, related_name='oprisk_activities', verbose_name="Cargo Dueño")
    owner_area = models.ForeignKey('catalogs.OrganizationalUnit', on_delete=models.SET_NULL, null=True, blank=True, related_name='oprisk_activities_area', verbose_name="Área Dueña")

    class Meta:
        verbose_name = "Actividad"
        verbose_name_plural = "Actividades"
        
    def __str__(self):
        return f"{self.subprocess.name} > {self.name}"

# Matrices de 5x5 (Parametrización)
class RiskCategory(models.Model):
    name = models.CharField(max_length=150, unique=True, verbose_name="Categoría de Riesgo")
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Categoría de Riesgo"
        verbose_name_plural = "Categorías de Riesgo"

    def __str__(self):
        return self.name

class ProbabilityLevel(models.Model):
    level = models.IntegerField(unique=True, verbose_name="Nivel (1-5)")
    name = models.CharField(max_length=100, verbose_name="Nombre (Ej: Posible)")
    description = models.TextField(blank=True, null=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=0.0, help_text="Peso para cálculos")

    class Meta:
        verbose_name = "Nivel de Probabilidad"
        verbose_name_plural = "Niveles de Probabilidad"
        ordering = ['level']

    def __str__(self):
        return f"{self.level} - {self.name}"

class ImpactLevel(models.Model):
    level = models.IntegerField(unique=True, verbose_name="Nivel (1-5)")
    name = models.CharField(max_length=100, verbose_name="Nombre (Ej: Catastrófico)")
    description = models.TextField(blank=True, null=True)
    financial_threshold = models.DecimalField(max_digits=15, decimal_places=2, default=0.0, help_text="Umbral económico")

    class Meta:
        verbose_name = "Nivel de Impacto"
        verbose_name_plural = "Niveles de Impacto"
        ordering = ['level']

    def __str__(self):
        return f"{self.level} - {self.name}"

class RiskStatus(models.Model):
    code = models.CharField(max_length=20, unique=True, verbose_name="Código Interno (Ej: DRAFT, APPROVED)")
    name = models.CharField(max_length=100, verbose_name="Nombre (Ej: Borrador, Aprobado)")
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Estado del Riesgo"
        verbose_name_plural = "Estados del Riesgo"

    def __str__(self):
        return self.name

# Riesgos y Controles
class Risk(models.Model):
    name = models.CharField(max_length=200, verbose_name="Riesgo")
    cause = models.TextField(verbose_name="Causa", blank=True, null=True)
    event = models.TextField(verbose_name="Evento", blank=True, null=True)
    consequence = models.TextField(verbose_name="Impacto/Consecuencia", blank=True, null=True)
    
    process = models.ForeignKey(Process, on_delete=models.CASCADE, related_name='risks', verbose_name="Proceso")
    category = models.ForeignKey(RiskCategory, on_delete=models.SET_NULL, null=True, verbose_name="Categoría de Riesgo")
    
    inherent_probability = models.ForeignKey(ProbabilityLevel, on_delete=models.SET_NULL, null=True, related_name='risks_inherent_prob', verbose_name="Probabilidad Inherente")
    inherent_impact = models.ForeignKey(ImpactLevel, on_delete=models.SET_NULL, null=True, related_name='risks_inherent_imp', verbose_name="Impacto Inherente")
    
    residual_probability = models.ForeignKey(ProbabilityLevel, on_delete=models.SET_NULL, null=True, blank=True, related_name='risks_residual_prob', verbose_name="Probabilidad Residual")
    residual_impact = models.ForeignKey(ImpactLevel, on_delete=models.SET_NULL, null=True, blank=True, related_name='risks_residual_imp', verbose_name="Impacto Residual")
    
    status = models.ForeignKey(RiskStatus, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Estado")
    owner = models.ForeignKey('catalogs.Position', on_delete=models.SET_NULL, null=True, blank=True, related_name='oprisk_owned_risks', verbose_name="Dueño del Cargo")
    extra_data = models.JSONField(blank=True, default=dict, verbose_name="Datos Adicionales (Custom Fields)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Riesgo"
        verbose_name_plural = "Riesgos"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.name:
            from catalogs.models import RiskCatalog
            RiskCatalog.objects.get_or_create(name=self.name)

    def __str__(self):
        return self.name

class Control(models.Model):
    TYPE_CHOICES = [
        ('PREVENTIVE', 'Preventivo'),
        ('DETECTIVE', 'Detectivo'),
        ('CORRECTIVE', 'Correctivo'),
    ]
    name = models.CharField(max_length=200, verbose_name="Nombre del Control")
    description = models.TextField(verbose_name="Descripción", blank=True, null=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='PREVENTIVE', verbose_name="Tipo de Control")
    periodicity = models.CharField(max_length=100, verbose_name="Periodicidad", help_text="Ej: Diario, Mensual")
    owner = models.ForeignKey('catalogs.Position', on_delete=models.SET_NULL, null=True, blank=True, related_name='oprisk_owned_controls', verbose_name="Responsable")
    
    design_efficacy = models.IntegerField(verbose_name="Eficacia del Diseño (%)", default=100)
    operational_effectiveness = models.IntegerField(verbose_name="Efectividad Operativa (%)", default=100)
    
    risks = models.ManyToManyField(Risk, related_name='controls', blank=True, verbose_name="Riesgos Mitigados")
    extra_data = models.JSONField(blank=True, default=dict, verbose_name="Datos Adicionales (Custom Fields)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Control"
        verbose_name_plural = "Controles"

    def __str__(self):
        return self.name

# Eventos e Incidentes
class RiskEvent(models.Model):
    EVENT_TYPES = [
        ('LOSS', 'Pérdida'),
        ('NEAR_MISS', 'Cuasi Pérdida'),
        ('SYSTEM_FAILURE', 'Falla de Sistema'),
        ('FRAUD', 'Fraude'),
    ]
    title = models.CharField(max_length=200, verbose_name="Título del Evento")
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, verbose_name="Tipo de Evento")
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.0, verbose_name="Monto de Pérdida")
    date_occurred = models.DateField(verbose_name="Fecha de Ocurrencia")
    date_discovered = models.DateField(verbose_name="Fecha de Descubrimiento")
    
    root_cause = models.TextField(verbose_name="Causa Raíz", blank=True, null=True)
    immediate_action = models.TextField(verbose_name="Acción Tomada", blank=True, null=True)
    
    process = models.ForeignKey(Process, on_delete=models.SET_NULL, null=True, blank=True, related_name='events', verbose_name="Proceso Afectado")
    failed_control = models.ForeignKey(Control, on_delete=models.SET_NULL, null=True, blank=True, related_name='failed_in_events', verbose_name="Control Fallido")
    
    reported_by = models.ForeignKey('catalogs.Position', on_delete=models.SET_NULL, null=True, blank=True, related_name='oprisk_reported_events', verbose_name="Responsable")
    extra_data = models.JSONField(blank=True, default=dict, verbose_name="Datos Adicionales (Custom Fields)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Evento de Riesgo"
        verbose_name_plural = "Eventos de Riesgo"

    def __str__(self):
        return f"{self.date_occurred} - {self.title}"

# KRIs
class KeyRiskIndicator(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nombre del KRI")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")
    process = models.ForeignKey(Process, on_delete=models.SET_NULL, null=True, blank=True, related_name='kris', verbose_name="Proceso")
    risk = models.ForeignKey(Risk, on_delete=models.SET_NULL, null=True, blank=True, related_name='kris', verbose_name="Riesgo")
    owner = models.ForeignKey('catalogs.Position', on_delete=models.SET_NULL, null=True, blank=True, related_name='oprisk_owned_kris', verbose_name="Responsable")
    
    green_threshold = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Umbral Verde (<=)", default=0)
    yellow_threshold = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Umbral Amarillo (<=)", default=0)
    red_threshold = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Umbral Rojo (>)", default=0)
    
    class Meta:
        verbose_name = "KRI"
        verbose_name_plural = "KRIs"

    def __str__(self):
        return self.name

class KRIReading(models.Model):
    kri = models.ForeignKey(KeyRiskIndicator, on_delete=models.CASCADE, related_name='readings')
    date = models.DateField(verbose_name="Fecha de Lectura")
    value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor")
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Lectura de KRI"
        verbose_name_plural = "Lecturas de KRIs"
        ordering = ['-date']

# Planes de Acción
class ActionPlan(models.Model):
    STATUS_CHOICES = [
        ('OPEN', 'Abierto'),
        ('IN_PROGRESS', 'En Progreso'),
        ('COMPLETED', 'Completado'),
        ('OVERDUE', 'Atrasado'),
    ]
    title = models.CharField(max_length=200, verbose_name="Título del Hallazgo/Plan")
    description = models.TextField(verbose_name="Acción Correctiva")
    owner = models.ForeignKey('catalogs.Position', on_delete=models.SET_NULL, null=True, related_name='oprisk_action_plans', verbose_name="Responsable")
    commitment_date = models.DateField(verbose_name="Fecha Compromiso")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN', verbose_name="Estado")
    
    risk = models.ForeignKey(Risk, on_delete=models.SET_NULL, null=True, blank=True, related_name='action_plans', verbose_name="Riesgo")
    event = models.ForeignKey(RiskEvent, on_delete=models.SET_NULL, null=True, blank=True, related_name='action_plans', verbose_name="Evento")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Plan de Acción"
        verbose_name_plural = "Planes de Acción"

    def __str__(self):
        return self.title

class ActionPlanEvidence(models.Model):
    action_plan = models.ForeignKey(ActionPlan, on_delete=models.CASCADE, related_name='evidences')
    file = models.FileField(upload_to='op_risk/evidences/', blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

# Documentos (Generic Relations)
class OpRiskDocument(models.Model):
    title = models.CharField(max_length=200, verbose_name="Título del Documento")
    file = models.FileField(upload_to='op_risk/documents/', blank=True, null=True, verbose_name="Archivo Local")
    drive_url = models.URLField(max_length=500, blank=True, null=True, verbose_name="Enlace de Drive/Nube")
    version = models.CharField(max_length=20, default="1.0", verbose_name="Versión")
    
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, verbose_name="Tipo de Registro Relacionado", null=True, blank=True)
    object_id = models.PositiveIntegerField(verbose_name="ID del Registro", null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    uploaded_by = models.ForeignKey('catalogs.Position', on_delete=models.SET_NULL, null=True, verbose_name="Responsable")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Documento RO"
        verbose_name_plural = "Documentos RO"

    def __str__(self):
        return f"{self.title} (v{self.version})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Subida automática a Google Drive si hay un archivo local y el enlace proporcionado es una carpeta
        if self.file and self.drive_url and '/folders/' in self.drive_url:
            from .drive_utils import upload_to_drive
            try:
                new_url = upload_to_drive(self.file.path, self.drive_url)
                if new_url:
                    self.drive_url = new_url
                    super().save(update_fields=['drive_url'])
            except Exception as e:
                print(f"Error en la integración con Google Drive: {e}")

class OperationalCapitalCalculation(models.Model):
    year = models.IntegerField(verbose_name="Año de Cálculo", unique=True)
    gross_income_y1 = models.DecimalField(max_digits=20, decimal_places=2, verbose_name="Ingresos Brutos (Año - 1)")
    gross_income_y2 = models.DecimalField(max_digits=20, decimal_places=2, verbose_name="Ingresos Brutos (Año - 2)")
    gross_income_y3 = models.DecimalField(max_digits=20, decimal_places=2, verbose_name="Ingresos Brutos (Año - 3)")
    alfa_factor = models.DecimalField(max_digits=5, decimal_places=4, default=0.15, verbose_name="Factor Alfa (Ej: 15%)")
    
    calculated_capital = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True, verbose_name="Capital Requerido Calculado")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cálculo Capital Operacional"
        verbose_name_plural = "Cálculos Capital Operacional"
        ordering = ['-year']

    def save(self, *args, **kwargs):
        # Calculate capital (Basic Indicator Approach): 
        # (Sum of positive gross incomes / number of positive years) * alfa
        incomes = [self.gross_income_y1, self.gross_income_y2, self.gross_income_y3]
        positive_incomes = [i for i in incomes if i > 0]
        if positive_incomes:
            avg_income = sum(positive_incomes) / len(positive_incomes)
            self.calculated_capital = avg_income * self.alfa_factor
        else:
            self.calculated_capital = 0
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Capital {self.year}: {self.calculated_capital}"
