from django.db import models
from django.utils.translation import gettext_lazy as _

class MarketTimeBand(models.Model):
    name = models.CharField("Nombre de la banda", max_length=50, help_text="Ej: 0-30 días, 31-90 días, etc.")
    order = models.IntegerField("Orden de visualización", default=1)
    days_start = models.IntegerField("Límite inferior en días", null=True, blank=True)
    days_end = models.IntegerField("Límite superior en días", null=True, blank=True)

    class Meta:
        ordering = ['order']
        verbose_name = "Banda Temporal"
        verbose_name_plural = "Bandas Temporales"

    def __str__(self):
        return self.name

class PositionType(models.TextChoices):
    ASSET = 'ASSET', _('Activo')
    LIABILITY = 'LIABILITY', _('Pasivo')
    INVESTMENT = 'INVESTMENT', _('Inversión')

class CurrencyType(models.TextChoices):
    LOCAL = 'MN', _('Moneda Nacional')
    FOREIGN = 'ME', _('Moneda Extranjera')

class MarketPositionUpload(models.Model):
    period_date = models.DateField("Fecha de corte")
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='SUCCESS')
    
    class Meta:
        ordering = ['-period_date']
        verbose_name = "Carga de Posiciones"
        verbose_name_plural = "Cargas de Posiciones"

    def __str__(self):
        return f"Posiciones {self.period_date.strftime('%Y-%m-%d')}"

class MarketPosition(models.Model):
    upload = models.ForeignKey(MarketPositionUpload, on_delete=models.CASCADE, related_name='positions')
    position_type = models.CharField("Tipo", max_length=20, choices=PositionType.choices)
    account_code = models.CharField("Código de Cuenta", max_length=50)
    description = models.CharField("Descripción", max_length=255, blank=True, null=True)
    currency = models.CharField("Moneda", max_length=10, choices=CurrencyType.choices, default=CurrencyType.LOCAL)
    balance = models.DecimalField("Saldo", max_digits=18, decimal_places=4, default=0)
    interest_rate = models.DecimalField("TEA (%)", max_digits=10, decimal_places=4, help_text="Tasa Efectiva Anual (Ej: 12.5 para 12.5%)")
    repricing_date = models.DateField("Fecha Reprecio/Vcto.", null=True, blank=True)
    time_band = models.ForeignKey(MarketTimeBand, on_delete=models.SET_NULL, null=True, blank=True, related_name='positions')

    class Meta:
        indexes = [
            models.Index(fields=['upload', 'position_type']),
        ]
        verbose_name = "Posición de Mercado"
        verbose_name_plural = "Posiciones de Mercado"

    def __str__(self):
        return f"{self.account_code} - {self.balance}"

class ScenarioType(models.TextChoices):
    SENSITIVITY = 'SENS', _('Sensibilidad')
    STRESS = 'STRESS', _('Estrés')

class MarketScenario(models.Model):
    name = models.CharField("Nombre del Escenario", max_length=100)
    scenario_type = models.CharField("Tipo", max_length=15, choices=ScenarioType.choices, default=ScenarioType.SENSITIVITY)
    rate_shock_bps = models.IntegerField("Shock Tasas (bps)", default=0, help_text="Ej: 100 para +1%, -50 para -0.5%")
    fx_shock_percent = models.DecimalField("Shock T.C. (%)", max_digits=10, decimal_places=4, default=0, help_text="Ej: 5 para depreciación de 5%")
    is_active = models.BooleanField("Activo", default=True)

    class Meta:
        verbose_name = "Escenario de Mercado"
        verbose_name_plural = "Escenarios de Mercado"

    def __str__(self):
        return self.name

class MarketLimit(models.Model):
    name = models.CharField("Indicador", max_length=100)
    threshold_value = models.DecimalField("Valor Límite", max_digits=18, decimal_places=4)
    is_percentage = models.BooleanField("Es Porcentaje?", default=True)

    class Meta:
        verbose_name = "Límite de Mercado"
        verbose_name_plural = "Límites de Mercado"

    def __str__(self):
        return f"{self.name} - {self.threshold_value}"
