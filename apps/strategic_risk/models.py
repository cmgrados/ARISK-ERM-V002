from django.db import models
from django.conf import settings
from users.models import TenantAwareModel

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
        ('CONCLUSIONES', 'Matriz de Conclusiones'),
    ]
    plan = models.ForeignKey(StrategicPlan, on_delete=models.CASCADE, related_name='matrices')
    matrix_type = models.CharField('Tipo de Matriz', max_length=20, choices=MATRIX_CHOICES)
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

class Perspectiva(TenantAwareModel):
    plan = models.ForeignKey(StrategicPlan, on_delete=models.CASCADE, related_name='perspectivas', null=True, blank=True)
    nombre = models.CharField(max_length=150, verbose_name="Perspectiva")
    descripcion = models.TextField(blank=True, null=True)
    peso_porcentual = models.DecimalField(max_digits=5, decimal_places=2, default=25.00)

    class Meta:
        verbose_name = "Perspectiva"
        verbose_name_plural = "Perspectivas"
        unique_together = ('plan', 'nombre')

class TipoObjetivo(TenantAwareModel):
    plan = models.ForeignKey(StrategicPlan, on_delete=models.CASCADE, related_name='tipos_objetivo', null=True, blank=True)
    nombre = models.CharField(max_length=150, verbose_name="Tipo de Objetivo")

    class Meta:
        verbose_name = "Tipo de Objetivo"
        verbose_name_plural = "Tipos de Objetivo"
        unique_together = ('plan', 'nombre')

class AreaResponsable(TenantAwareModel):
    plan = models.ForeignKey(StrategicPlan, on_delete=models.CASCADE, related_name='areas_responsables', null=True, blank=True)
    nombre = models.CharField(max_length=150, verbose_name="Área Responsable")

    class Meta:
        verbose_name = "Área Responsable"
        verbose_name_plural = "Áreas Responsables"
        unique_together = ('plan', 'nombre')

class ResponsablePlan(TenantAwareModel):
    plan = models.ForeignKey(StrategicPlan, on_delete=models.CASCADE, related_name='responsables', null=True, blank=True)
    nombre = models.CharField(max_length=150, verbose_name="Responsable")

    class Meta:
        verbose_name = "Responsable"
        verbose_name_plural = "Responsables"
        unique_together = ('plan', 'nombre')

    def __str__(self):
        return self.nombre

class ObjetivoEstrategico(TenantAwareModel):
    perspectiva = models.ForeignKey(Perspectiva, on_delete=models.CASCADE, related_name='objetivos')
    codigo = models.CharField(max_length=20, verbose_name="Código (Ej. OE-01)")
    nombre = models.CharField(max_length=255, verbose_name="Objetivo Estratégico")
    descripcion = models.TextField(blank=True, null=True)
    
    tipo_objetivo = models.CharField(max_length=150, blank=True, null=True, verbose_name="Tipo de Objetivo")
    area_responsable = models.CharField(max_length=200, blank=True, null=True, verbose_name="Área Responsable")
    responsable = models.CharField(max_length=200, blank=True, null=True, verbose_name="Responsable")
    peso = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name="Peso (%)")

    class Meta:
        verbose_name = "Objetivo Estratégico"
        unique_together = ('organization', 'codigo')

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

class Indicador(TenantAwareModel):
    FRECUENCIA_CHOICES = [
        ('MENSUAL', 'Mensual'),
        ('TRIMESTRAL', 'Trimestral'),
        ('SEMESTRAL', 'Semestral'),
        ('ANUAL', 'Anual')
    ]
    
    objetivo = models.ForeignKey(ObjetivoEstrategico, on_delete=models.CASCADE, related_name='indicadores')
    nombre = models.CharField(max_length=255, verbose_name="Nombre del Indicador (KPI)")
    formula = models.CharField(
        max_length=255, 
        help_text="Fórmula matemática usando variables. Ej: (resultado_real / meta_programada) * 100"
    )
    unidad_medida = models.CharField(max_length=50, verbose_name="Unidad (%, $, N°)")
    frecuencia_medicion = models.CharField(max_length=20, choices=FRECUENCIA_CHOICES)
    tipo_objetivo = models.CharField(max_length=150, blank=True, null=True, verbose_name="Tipo Objetivo")
    
    linea_base = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    meta_final = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    peso = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name="Peso (%)")
    fecha_inicio = models.DateField(null=True, blank=True, verbose_name="Fecha Inicio")
    fecha_fin = models.DateField(null=True, blank=True, verbose_name="Fecha Fin")
    responsable = models.CharField(max_length=200, blank=True, null=True, verbose_name="Responsable")
    medio_verificacion = models.CharField(max_length=255, blank=True, null=True, verbose_name="Medio de Verificación")

    class Meta:
        verbose_name = "Indicador KPI"

    def __str__(self):
        return self.nombre

class MetaPeriodo(TenantAwareModel):
    indicador = models.ForeignKey(Indicador, on_delete=models.CASCADE, related_name='metas_periodo')
    periodo = models.CharField(max_length=50, verbose_name="Periodo (Ej. Q1-2026, Enero-2026)")
    
    meta_programada = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Meta Programada")
    resultado_real = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="Resultado Real logrado")
    
    porcentaje_cumplimiento = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    semaforo = models.CharField(max_length=20, null=True, blank=True, help_text="Rojo, Amarillo, Verde")

    class Meta:
        unique_together = ('indicador', 'periodo')

    def __str__(self):
        return f"{self.indicador.nombre} - {self.periodo}"

# --- EJECUCIÓN OPERATIVA Y MONITOREO (PROYECTOS) ---

from django.core.exceptions import ValidationError
from decimal import Decimal

class ProyectoIniciativa(TenantAwareModel):
    ESTADO_CHOICES = [
        ('PLANIFICADO', 'Planificado'),
        ('EN_PROCESO', 'En Proceso'),
        ('RETRASADO', 'Retrasado'),
        ('COMPLETADO', 'Completado'),
        ('SUSPENDIDO', 'Suspendido'),
    ]
    indicador = models.ForeignKey('Indicador', on_delete=models.CASCADE, related_name='proyectos')
    codigo = models.CharField('Código del Proyecto', max_length=20)
    nombre = models.CharField('Nombre del Proyecto', max_length=255)
    fecha_inicio = models.DateField('Fecha de Inicio')
    fecha_fin = models.DateField('Fecha de Fin')
    presupuesto_total = models.DecimalField('Presupuesto Total ($)', max_digits=15, decimal_places=2, default=0)
    estado = models.CharField('Estado', max_length=50, choices=ESTADO_CHOICES, default='PLANIFICADO')

    # Estos campos se calculan dinámicamente mediante el servicio o properties
    porcentaje_avance_fisico = models.DecimalField('Avance Físico (%)', max_digits=5, decimal_places=2, default=0)
    porcentaje_avance_financiero = models.DecimalField('Avance Financiero (%)', max_digits=5, decimal_places=2, default=0)
    semaforo_ejecucion = models.CharField('Semáforo de Ejecución', max_length=20, null=True, blank=True)

    class Meta:
        verbose_name = "Proyecto e Iniciativa"
        verbose_name_plural = "Proyectos e Iniciativas"
        unique_together = ('organization', 'codigo')

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

    def actualizar_avances(self):
        # El avance físico es el promedio de avance de sus hitos (o ponderado si existiera peso)
        hitos = self.hitos.all()
        if hitos.exists():
            avance = sum(h.porcentaje_avance_real for h in hitos) / hitos.count()
            self.porcentaje_avance_fisico = round(avance, 2)

        # El avance financiero es (gasto real total / presupuesto total) * 100
        ejecuciones = self.ejecuciones.all()
        gasto_total = sum(e.gasto_real for e in ejecuciones)
        if self.presupuesto_total > 0:
            self.porcentaje_avance_financiero = round((gasto_total / self.presupuesto_total) * 100, 2)

        # Semáforo de Ejecución: si el físico es mucho menor que el financiero, hay ineficiencia (Rojo)
        brecha = self.porcentaje_avance_financiero - self.porcentaje_avance_fisico
        if brecha > 15:
            self.semaforo_ejecucion = 'Rojo'
        elif brecha > 5:
            self.semaforo_ejecucion = 'Amarillo'
        else:
            self.semaforo_ejecucion = 'Verde'

        self.save()

class EjecucionPresupuestaria(TenantAwareModel):
    proyecto = models.ForeignKey(ProyectoIniciativa, on_delete=models.CASCADE, related_name='ejecuciones')
    periodo = models.CharField('Periodo (Ej. Mes/Trimestre)', max_length=50)
    gasto_programado = models.DecimalField('Gasto Programado ($)', max_digits=15, decimal_places=2, default=0)
    gasto_real = models.DecimalField('Gasto Real ($)', max_digits=15, decimal_places=2, default=0)
    justificacion = models.TextField('Justificación de Desviación', blank=True, null=True)

    class Meta:
        verbose_name = "Ejecución Presupuestaria"
        unique_together = ('proyecto', 'periodo')

    def clean(self):
        super().clean()
        desviacion = self.gasto_programado - self.gasto_real
        
        # Validar que el gasto acumulado no supere el presupuesto del proyecto
        gastos_existentes = EjecucionPresupuestaria.objects.filter(proyecto=self.proyecto).exclude(pk=self.pk)
        total_acumulado = sum(e.gasto_real for e in gastos_existentes) + self.gasto_real
        if total_acumulado > self.proyecto.presupuesto_total:
            raise ValidationError({
                'gasto_real': f'El gasto real acumulado ({total_acumulado}) no puede exceder el presupuesto total del proyecto ({self.proyecto.presupuesto_total}).'
            })

        # Regla crítica: si hay sobre-ejecución (gasto_real > gasto_programado) exige justificación
        if desviacion < 0 and not self.justificacion:
            raise ValidationError({
                'justificacion': 'Se requiere una justificación porque el gasto real supera al gasto programado en este periodo.'
            })

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

class HitoProyecto(TenantAwareModel):
    proyecto = models.ForeignKey(ProyectoIniciativa, on_delete=models.CASCADE, related_name='hitos')
    nombre = models.CharField('Nombre del Hito/Entregable', max_length=255)
    fecha_entrega = models.DateField('Fecha Programada de Entrega')
    porcentaje_avance_programado = models.DecimalField('Avance Programado (%)', max_digits=5, decimal_places=2, default=0)
    porcentaje_avance_real = models.DecimalField('Avance Real (%)', max_digits=5, decimal_places=2, default=0)
    justificacion = models.TextField('Justificación de Retraso', blank=True, null=True)

    class Meta:
        verbose_name = "Hito del Proyecto"

    def clean(self):
        super().clean()
        # Regla crítica: Si el avance real es inferior al programado, se exige justificación
        if self.porcentaje_avance_real < self.porcentaje_avance_programado and not self.justificacion:
            raise ValidationError({
                'justificacion': 'Se requiere una justificación obligatoria porque el avance real es menor al programado.'
            })

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

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
