from django.db import models
from django.conf import settings

class StrategicPlan(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Borrador'),
        ('ACTIVE', 'Activo'),
        ('CLOSED', 'Cerrado'),
        ('ARCHIVED', 'Archivado'),
    ]

    name = models.CharField('Nombre del Plan', max_length=200)
    institution = models.CharField('Institución', max_length=200, default='COOPAC')
    start_year = models.IntegerField('Año de Inicio')
    horizon_years = models.IntegerField('Horizonte (Años)', choices=[(3, '3 Años'), (4, '4 Años'), (5, '5 Años')], default=3)
    status = models.CharField('Estado', max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    version = models.CharField('Versión', max_length=10, default='1.0')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='Responsable')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Plan Estratégico'
        verbose_name_plural = 'Planes Estratégicos'

    def __str__(self):
        return f"{self.name} ({self.start_year} - {self.start_year + self.horizon_years - 1})"

class CorporatePhilosophy(models.Model):
    plan = models.OneToOneField(StrategicPlan, on_delete=models.CASCADE, related_name='philosophy')
    mission = models.TextField('Misión', blank=True, null=True)
    vision = models.TextField('Visión', blank=True, null=True)
    values = models.TextField('Valores', blank=True, null=True)

    class Meta:
        verbose_name = 'Filosofía Corporativa'
        verbose_name_plural = 'Filosofías Corporativas'

    def __str__(self):
        return f"Filosofía de {self.plan.name}"

# --- ENTORNOS Y DIAGNÓSTICO ---

class ExternalEnvironment(models.Model):
    plan = models.OneToOneField(StrategicPlan, on_delete=models.CASCADE, related_name='external_environment')
    international_analysis = models.TextField('Análisis Internacional', blank=True, null=True)
    national_analysis = models.TextField('Análisis Nacional', blank=True, null=True)
    economic_vars = models.TextField('Variables Económicas', blank=True, null=True)
    regulatory_vars = models.TextField('Variables Regulatorias', blank=True, null=True)
    social_vars = models.TextField('Variables Sociales', blank=True, null=True)
    technological_vars = models.TextField('Variables Tecnológicas', blank=True, null=True)
    competitive_vars = models.TextField('Variables Competitivas', blank=True, null=True)
    conclusions = models.TextField('Conclusiones', blank=True, null=True)

class FinancialEnvironment(models.Model):
    plan = models.OneToOneField(StrategicPlan, on_delete=models.CASCADE, related_name='financial_environment')
    system_structure = models.TextField('Estructura del Sistema Financiero', blank=True, null=True)
    credit_analysis = models.TextField('Análisis de Créditos', blank=True, null=True)
    deposit_analysis = models.TextField('Análisis de Depósitos', blank=True, null=True)
    trends_rates = models.TextField('Tendencias y Tasas', blank=True, null=True)
    observations = models.TextField('Observaciones', blank=True, null=True)

class InternalDiagnosis(models.Model):
    plan = models.OneToOneField(StrategicPlan, on_delete=models.CASCADE, related_name='internal_diagnosis')
    operations_scope = models.TextField('Ámbito de Operaciones', blank=True, null=True)
    credit_analysis = models.TextField('Análisis de Créditos (Interno)', blank=True, null=True)
    delinquency_analysis = models.TextField('Análisis de Mora', blank=True, null=True)
    deposit_analysis = models.TextField('Análisis de Depósitos (Interno)', blank=True, null=True)
    interest_rates = models.TextField('Tasas de Interés por Tipo de Depósito', blank=True, null=True)
    strengths = models.TextField('Fortalezas', blank=True, null=True)
    weaknesses = models.TextField('Debilidades', blank=True, null=True)

# --- MATRICES Y MODELOS ---

class StrategicMatrix(models.Model):
    MATRIX_CHOICES = [
        ('FODA', 'Matriz FODA'),
        ('EFI', 'Matriz EFI'),
        ('EFE', 'Matriz EFE'),
        ('MPC', 'Matriz de Perfil Competitivo'),
        ('METAS', 'Metas Planeadas'),
    ]
    plan = models.ForeignKey(StrategicPlan, on_delete=models.CASCADE, related_name='matrices')
    matrix_type = models.CharField('Tipo de Matriz', max_length=10, choices=MATRIX_CHOICES)
    data = models.JSONField('Datos de la Matriz', default=dict) # Guarda factores, pesos, calificaciones JSON
    conclusions = models.TextField('Conclusiones', blank=True, null=True)

class BusinessModelCanvas(models.Model):
    plan = models.ForeignKey(StrategicPlan, on_delete=models.CASCADE, related_name='canvas')
    version = models.CharField('Versión', max_length=10, default='1.0')
    customer_segments = models.TextField('Segmentos de Clientes', blank=True, null=True)
    value_proposition = models.TextField('Propuesta de Valor', blank=True, null=True)
    channels = models.TextField('Canales', blank=True, null=True)
    customer_relationships = models.TextField('Relaciones con Clientes', blank=True, null=True)
    revenue_streams = models.TextField('Flujos de Ingreso', blank=True, null=True)
    key_resources = models.TextField('Recursos Clave', blank=True, null=True)
    key_activities = models.TextField('Actividades Clave', blank=True, null=True)
    key_partners = models.TextField('Socios Clave', blank=True, null=True)
    cost_structure = models.TextField('Estructura de Costos', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

# --- BALANCED SCORECARD ---

class StrategicPerspective(models.Model):
    plan = models.ForeignKey(StrategicPlan, on_delete=models.CASCADE, related_name='perspectives')
    name = models.CharField('Nombre de Perspectiva', max_length=100)
    description = models.TextField('Descripción', blank=True, null=True)
    order = models.IntegerField('Orden', default=0)

    def __str__(self):
        return self.name

class StrategicObjective(models.Model):
    perspective = models.ForeignKey(StrategicPerspective, on_delete=models.CASCADE, related_name='objectives')
    name = models.CharField('Objetivo Estratégico', max_length=255)
    description = models.TextField('Descripción', blank=True, null=True)

    def __str__(self):
        return self.name

class KPI(models.Model):
    objective = models.ForeignKey(StrategicObjective, on_delete=models.CASCADE, related_name='kpis')
    name = models.CharField('Indicador (KPI)', max_length=255)
    formula = models.TextField('Fórmula de Cálculo', blank=True, null=True)
    baseline = models.DecimalField('Línea Base', max_digits=15, decimal_places=2, default=0)
    target = models.DecimalField('Meta', max_digits=15, decimal_places=2, default=0)
    frequency = models.CharField('Frecuencia de Medición', max_length=50, choices=[('Mensual', 'Mensual'), ('Trimestral', 'Trimestral'), ('Semestral', 'Semestral'), ('Anual', 'Anual')])
    # Umbrales para semáforo (ej: si es mayor a green_threshold es verde, entre yellow y green es amarillo, menor a red es rojo)
    green_threshold = models.DecimalField('Límite Verde (>=)', max_digits=15, decimal_places=2, default=0)
    yellow_threshold = models.DecimalField('Límite Amarillo (>=)', max_digits=15, decimal_places=2, default=0)
    
    def __str__(self):
        return self.name

class KPIMeasurement(models.Model):
    kpi = models.ForeignKey(KPI, on_delete=models.CASCADE, related_name='measurements')
    period_date = models.DateField('Fecha de Medición')
    value = models.DecimalField('Valor Logrado', max_digits=15, decimal_places=2)
    observations = models.TextField('Observaciones / Desviaciones', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

# --- PROYECTOS ---

class StrategicProject(models.Model):
    objective = models.ForeignKey(StrategicObjective, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField('Nombre del Proyecto', max_length=255)
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='Responsable')
    start_date = models.DateField('Fecha de Inicio')
    end_date = models.DateField('Fecha de Fin')
    budget = models.DecimalField('Presupuesto', max_digits=15, decimal_places=2, default=0)
    status = models.CharField('Estado', max_length=50, choices=[('Planificado', 'Planificado'), ('En Curso', 'En Curso'), ('Retrasado', 'Retrasado'), ('Completado', 'Completado')])
    physical_progress = models.DecimalField('Avance Físico (%)', max_digits=5, decimal_places=2, default=0)
    financial_progress = models.DecimalField('Avance Financiero (%)', max_digits=5, decimal_places=2, default=0)
    risks = models.TextField('Riesgos del Proyecto', blank=True, null=True)

    def __str__(self):
        return self.name

# --- ENCUESTAS ---

class Survey(models.Model):
    TARGET_CHOICES = [('Socios', 'Socios'), ('Clientes', 'Clientes'), ('Colaboradores', 'Colaboradores')]
    plan = models.ForeignKey(StrategicPlan, on_delete=models.CASCADE, related_name='surveys')
    title = models.CharField('Título de la Encuesta', max_length=200)
    description = models.TextField('Descripción', blank=True, null=True)
    target_audience = models.CharField('Público Objetivo', max_length=50, choices=TARGET_CHOICES)
    is_active = models.BooleanField('Activa', default=True)
    created_at = models.DateTimeField(auto_now_add=True)

class SurveyQuestion(models.Model):
    TYPE_CHOICES = [('Text', 'Texto Libre'), ('Rating', 'Calificación 1-5'), ('Boolean', 'Sí/No')]
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField('Pregunta', max_length=500)
    question_type = models.CharField('Tipo de Pregunta', max_length=20, choices=TYPE_CHOICES)
    order = models.IntegerField('Orden', default=0)

class SurveyResponse(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='responses')
    responder_info = models.CharField('Información del Encuestado (Opcional)', max_length=200, blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

class SurveyAnswer(models.Model):
    response = models.ForeignKey(SurveyResponse, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(SurveyQuestion, on_delete=models.CASCADE)
    answer_text = models.TextField('Respuesta')
