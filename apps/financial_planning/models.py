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
