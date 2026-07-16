from django.db import models
from django.utils.translation import gettext_lazy as _

class LiqLoadStatus(models.TextChoices):
    PENDING = 'PENDING', _('Pendiente')
    SUCCESS = 'SUCCESS', _('Éxito')
    ERROR = 'ERROR', _('Error')

class LiqTimeBand(models.Model):
    name = models.CharField(max_length=50, help_text="Nombre de la banda (Ej. 1M, 2M, 3M, 1A)")
    order = models.IntegerField(help_text="Orden de visualización")
    days_start = models.IntegerField(help_text="Límite inferior en días", null=True, blank=True)
    days_end = models.IntegerField(help_text="Límite superior en días", null=True, blank=True)
    
    class Meta:
        ordering = ['order']
        verbose_name = "Banda Temporal"
        verbose_name_plural = "Bandas Temporales"

    def __str__(self):
        return self.name

class LiqBalanceUpload(models.Model):
    period = models.DateField(help_text="Fecha de corte del balance")
    status = models.CharField(
        max_length=20, 
        choices=LiqLoadStatus.choices, 
        default=LiqLoadStatus.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-period']
        unique_together = ('period',)

    def __str__(self):
        return f"Upload {self.period.strftime('%Y-%m-%d')} - {self.status}"

class LiqBalanceDetail(models.Model):
    upload = models.ForeignKey(LiqBalanceUpload, on_delete=models.CASCADE, related_name='details')
    period = models.DateField()
    account_code = models.CharField(max_length=50)
    balance = models.DecimalField(max_digits=18, decimal_places=4, default=0)

    class Meta:
        indexes = [
            models.Index(fields=['period', 'account_code']),
        ]

    def __str__(self):
        return f"{self.period} - {self.account_code}: {self.balance}"


class LiqLiabilityDetail(models.Model):
    period = models.DateField()
    agency = models.CharField(max_length=100, null=True, blank=True)
    customer_name = models.CharField(max_length=255, null=True, blank=True)
    funding_type = models.CharField(max_length=100, null=True, blank=True)
    liquidity_item = models.CharField(max_length=100, null=True, blank=True)
    currency = models.CharField(max_length=20, null=True, blank=True)
    balance = models.DecimalField(max_digits=18, decimal_places=4, default=0)
    liquidity_band = models.CharField(max_length=50, null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['period', 'liquidity_band']),
            models.Index(fields=['period', 'liquidity_item']),
        ]

class CarteraPasivoCarga(models.Model):
    fecha_corte = models.DateField(db_index=True)
    of = models.CharField(max_length=50, null=True, blank=True)
    id_socio = models.CharField(max_length=50, null=True, blank=True)
    id_ahorro = models.CharField(max_length=50, null=True, blank=True)
    socio = models.CharField(max_length=255, null=True, blank=True)
    apertura = models.DateField(null=True, blank=True)
    ofic_apertura = models.CharField(max_length=100, null=True, blank=True)
    usuario = models.CharField(max_length=100, null=True, blank=True)
    captador = models.CharField(max_length=100, null=True, blank=True)
    producto = models.CharField(max_length=150, null=True, blank=True)
    tim = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    tea = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    ult_mov = models.DateField(null=True, blank=True)
    vence = models.DateField(null=True, blank=True)
    plz = models.IntegerField(null=True, blank=True, default=0)
    ah_vinc = models.IntegerField(null=True, blank=True, default=0)
    mon = models.CharField(max_length=20, null=True, blank=True)
    saldo = models.DecimalField(max_digits=18, decimal_places=4, default=0)
    agencia_calc = models.CharField(max_length=100, null=True, blank=True)
    cod_asesor = models.CharField(max_length=100, null=True, blank=True)
    producto_agrupado = models.CharField(max_length=100, null=True, blank=True)
    saldo_dpf = models.DecimalField(max_digits=18, decimal_places=4, default=0)
    saldo_prog = models.DecimalField(max_digits=18, decimal_places=4, default=0)
    saldo_ctas_libre = models.DecimalField(max_digits=18, decimal_places=4, default=0)
    trea = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    plazo_dpf = models.IntegerField(null=True, blank=True, default=0)
    p_vence2 = models.CharField(max_length=100, null=True, blank=True)
    adm_agen = models.CharField(max_length=100, null=True, blank=True)
    id_compuesto = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['fecha_corte', 'id_ahorro']),
        ]

class LiqSavingsAccount(models.Model):
    # Stub model
    name = models.CharField(max_length=255)
    
class LiqTermDeposit(models.Model):
    # Stub model
    name = models.CharField(max_length=255)

class SbsParameter(models.Model):
    indicator = models.CharField("Indicador / Ratio", max_length=100)
    code = models.CharField("Código Interno", max_length=50, unique=True)
    sign = models.CharField("Signo", max_length=10) # >=, <=, N/A
    limit_value = models.DecimalField("Límite Normativo", max_digits=18, decimal_places=4)
    limit_type = models.CharField("Tipo", max_length=50) # Porcentaje, Ratio / Valor
    updated_at = models.DateTimeField("Última Actualización", auto_now=True)

    class Meta:
        verbose_name = "Parámetro SBS"
        verbose_name_plural = "Parámetros SBS"

    def __str__(self):
        return f"{self.indicator} {self.sign} {self.limit_value}"

class VolatileBalanceLar(models.Model):
    period = models.DateField("F. Cálculo", db_index=True)
    segment = models.CharField("Segmento", max_length=100)
    currency = models.CharField("Moneda", max_length=20, default="MN")
    total_balance = models.DecimalField("Saldo Total", max_digits=18, decimal_places=4, default=0)
    volatile_balance = models.DecimalField("Saldo Volátil", max_digits=18, decimal_places=4, default=0)
    volatility_percentage = models.DecimalField("% Volatilidad", max_digits=7, decimal_places=4, default=0)
    executed_by = models.CharField("Ejecutado por", max_length=100, blank=True, null=True)
    executed_at = models.DateTimeField("F. Ejecución", auto_now_add=True)

    class Meta:
        verbose_name = "Saldo Volátil LaR"
        verbose_name_plural = "Saldos Volátiles LaR"
        unique_together = ('period', 'segment', 'currency')

    def __str__(self):
        return f"{self.period} - {self.segment} ({self.volatility_percentage}%)"
