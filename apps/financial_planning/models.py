from django.db import models
from decimal import Decimal
from users.models import TenantAwareModel

class PeriodoFinanciero(TenantAwareModel):
    """
    Controla el mes, año y si el balance ya ha sido cerrado (definitivo).
    Evita la duplicidad de balances para un mismo periodo.
    """
    STATUS_CHOICES = (
        ('DRAFT', 'Borrador'),
        ('FINAL', 'Definitivo'),
    )
    
    anio = models.PositiveIntegerField(verbose_name="Año")
    mes = models.PositiveIntegerField(verbose_name="Mes")
    estado = models.CharField(max_length=10, choices=STATUS_CHOICES, default='DRAFT')
    fecha_carga = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Periodo Financiero"
        verbose_name_plural = "Periodos Financieros"
        unique_together = ('organization', 'anio', 'mes')

    def __str__(self):
        return f"{self.anio}-{self.mes:02d} ({self.get_estado_display()})"

class CuentaContable(TenantAwareModel):
    """
    Estructura jerárquica de la cuenta (Ej. 1 -> 1.1 -> 1.1.1)
    """
    TIPO_CUENTA_CHOICES = (
        ('ACTIVO', 'Activo'),
        ('PASIVO', 'Pasivo'),
        ('PATRIMONIO', 'Patrimonio'),
        ('INGRESO', 'Ingreso'),
        ('GASTO', 'Gasto'),
    )
    
    codigo = models.CharField(max_length=50, verbose_name="Código de Cuenta")
    nombre = models.CharField(max_length=255, verbose_name="Nombre de la Cuenta")
    tipo = models.CharField(max_length=20, choices=TIPO_CUENTA_CHOICES)
    nivel = models.PositiveIntegerField(verbose_name="Nivel de Profundidad")
    
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, 
        related_name='subcuentas', verbose_name="Cuenta Padre"
    )

    class Meta:
        verbose_name = "Cuenta Contable"
        verbose_name_plural = "Cuentas Contables"
        unique_together = ('organization', 'codigo')

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

class BalanceDetalle(TenantAwareModel):
    """
    Guarda el monto exacto de una cuenta en un periodo específico.
    Persiste el Análisis Vertical y Horizontal para lecturas ultrarrápidas.
    """
    periodo = models.ForeignKey(PeriodoFinanciero, on_delete=models.CASCADE, related_name='detalles')
    cuenta = models.ForeignKey(CuentaContable, on_delete=models.CASCADE, related_name='balances')
    
    monto = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    analisis_vertical = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True, 
        verbose_name="% Análisis Vertical"
    )
    analisis_horizontal = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, 
        verbose_name="% Análisis Horizontal (Crecimiento)"
    )

    def __str__(self):
        return f"{self.cuenta.codigo} | {self.periodo} | {self.monto}"

class PlanFinanciero(TenantAwareModel):
    nombre = models.CharField(max_length=255, verbose_name="Nombre del Plan")
    descripcion = models.TextField(verbose_name="Descripción", blank=True, null=True)
    anio_base = models.PositiveIntegerField(verbose_name="Año Base")
    horizonte_anios = models.PositiveIntegerField(verbose_name="Horizonte (Años)", default=3)
    historical_data = models.JSONField(verbose_name="Data Histórica", blank=True, null=True, default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Plan Financiero"
        verbose_name_plural = "Planes Financieros"
        unique_together = ('organization', 'nombre')

    def __str__(self):
        return f"{self.nombre} ({self.anio_base})"

class FinancialPlan(TenantAwareModel):
    STATUS_CHOICES = (
        ('DRAFT', 'Draft'),
        ('ACTIVE', 'Active'),
        ('ARCHIVED', 'Archived'),
    )
    name = models.CharField(max_length=255, verbose_name="Nombre del Plan")
    start_date = models.DateField(verbose_name="Fecha de Inicio")
    end_date = models.DateField(verbose_name="Fecha Fin")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='DRAFT')

    class Meta:
        verbose_name = "Financial Plan"
        verbose_name_plural = "Financial Plans"
        unique_together = ('organization', 'name')

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"

class MacroAssumption(TenantAwareModel):
    plan = models.ForeignKey(FinancialPlan, on_delete=models.CASCADE, related_name='macro_assumptions')
    month = models.PositiveIntegerField(verbose_name="Mes de Proyección")
    inflation_rate = models.DecimalField(max_digits=7, decimal_places=4, default=Decimal('0.0000'))
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=4, default=Decimal('0.0000'))
    
    class Meta:
        verbose_name = "Supuesto Macroeconómico"
        verbose_name_plural = "Supuestos Macroeconómicos"
        unique_together = ('organization', 'plan', 'month')

class PlanAssumption(TenantAwareModel):
    CATEGORY_CHOICES = (
        ('CREDIT_PORTFOLIO', 'Cartera de Créditos'),
        ('DELINQUENCY', 'Mora'),
        ('SAVINGS', 'Ahorros'),
        ('DPF', 'DPF'),
        ('CONTRIBUTIONS', 'Aportes'),
    )
    plan = models.ForeignKey(FinancialPlan, on_delete=models.CASCADE, related_name='plan_assumptions')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    
    trend_rate = models.DecimalField(max_digits=7, decimal_places=4, default=Decimal('0.0000'), verbose_name="Tasa de Tendencia")
    optimistic_rate = models.DecimalField(max_digits=7, decimal_places=4, default=Decimal('0.0000'), verbose_name="Escenario Optimista")
    pessimistic_rate = models.DecimalField(max_digits=7, decimal_places=4, default=Decimal('0.0000'), verbose_name="Escenario Pesimista")

    class Meta:
        verbose_name = "Supuesto de Plan"
        verbose_name_plural = "Supuestos de Plan"
        unique_together = ('organization', 'plan', 'category')

class HistoricalData(TenantAwareModel):
    plan = models.ForeignKey(FinancialPlan, on_delete=models.CASCADE, related_name='historical_data')
    period = models.CharField(max_length=10, verbose_name="Periodo (YYYY-MM)")
    account_name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))

    class Meta:
        verbose_name = "Dato Histórico"
        verbose_name_plural = "Datos Históricos"
        unique_together = ('organization', 'plan', 'period', 'account_name')

class ProjectedData(TenantAwareModel):
    SCENARIO_CHOICES = (
        ('BASE', 'Base (Tendencia)'),
        ('OPTIMISTIC', 'Optimista'),
        ('PESSIMISTIC', 'Pesimista'),
    )
    plan = models.ForeignKey(FinancialPlan, on_delete=models.CASCADE, related_name='projected_data')
    month = models.PositiveIntegerField(verbose_name="Mes Proyectado (1 a N)")
    scenario = models.CharField(max_length=20, choices=SCENARIO_CHOICES, default='BASE')
    account_name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))

    class Meta:
        verbose_name = "Dato Proyectado"
        verbose_name_plural = "Datos Proyectados"
        unique_together = ('organization', 'plan', 'month', 'scenario', 'account_name')

class SimulacionEscenario(TenantAwareModel):
    """Guarda la configuración de tasas y variables (tendencias y montecarlo) para la proyección de los E.F."""
    plan = models.ForeignKey(PlanFinanciero, on_delete=models.CASCADE, related_name='escenarios')
    agencia = models.CharField(max_length=100, default='Consolidado')
    variable_id = models.CharField(max_length=100)
    variable_name = models.CharField(max_length=255)
    
    tasa_tendencia = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    tasa_base = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    tasa_pesimista = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    tasa_optimista = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    
    class Meta:
        verbose_name = "Simulación Escenario"
        verbose_name_plural = "Simulaciones Escenarios"
        unique_together = ('organization', 'plan', 'agencia', 'variable_id')

    def __str__(self):
        return f"{self.plan.nombre} - {self.variable_name} ({self.agencia})"

class ProyeccionMensual(TenantAwareModel):
    """Guarda el valor de la proyección (tendencia y montecarlo) por mes para proyectar en los estados financieros"""
    escenario = models.ForeignKey(SimulacionEscenario, on_delete=models.CASCADE, related_name='proyecciones')
    mes_proyeccion = models.PositiveIntegerField() # 1 a N
    
    valor_tendencia = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    valor_base = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    valor_pesimista = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    valor_optimista = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    
    mc_valor_base = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    mc_valor_pesimista = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    mc_valor_optimista = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)

    class Meta:
        verbose_name = "Proyección Mensual"
        verbose_name_plural = "Proyecciones Mensuales"
        unique_together = ('organization', 'escenario', 'mes_proyeccion')
        ordering = ['mes_proyeccion']

    def __str__(self):
        return f"{self.escenario.variable_name} - Mes {self.mes_proyeccion}"
