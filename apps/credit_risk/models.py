from django.db import models

class Customer(models.Model):
    document_id = models.CharField("Documento/DNI", max_length=20, unique=True)
    external_id = models.CharField("Código de Socio", max_length=50, blank=True, null=True)
    name = models.CharField("Nombre/Razón Social", max_length=255)
    
    # Demographic fields
    age = models.IntegerField("Edad", null=True, blank=True)
    gender = models.CharField("Género (M/F)", max_length=1, blank=True, null=True)
    birth_date = models.DateField("Fecha de Nacimiento", null=True, blank=True)
    address = models.CharField("Dirección", max_length=255, blank=True, null=True)
    district = models.CharField("Distrito", max_length=100, blank=True, null=True)
    province = models.CharField("Provincia", max_length=100, blank=True, null=True)
    department = models.CharField("Departamento", max_length=100, blank=True, null=True)
    
    segment = models.CharField("Segmento", max_length=100)
    economic_activity = models.CharField("Actividad Económica", max_length=255)
    zone = models.CharField("Zona", max_length=100)
    
    class Meta:
        verbose_name = "Cliente / Socio"
        verbose_name_plural = "Clientes / Socios"

    def __str__(self):
        return f"{self.document_id} - {self.name}"

class CreditOperation(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='operations')
    operation_code = models.CharField("Código de Operación", max_length=50) # Removed unique=True
    product = models.ForeignKey(
        'catalogs.Product', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Producto"
    )
    product_name = models.CharField("Nombre Producto (Texto)", max_length=255, blank=True, db_index=True)
    
    # Financial fields
    disbursement_date = models.DateField("Fecha de Desembolso", null=True, blank=True)
    original_amount = models.DecimalField("Monto Desembolsado", max_digits=15, decimal_places=2, default=0)
    currency = models.CharField("Moneda (PEN/USD)", max_length=3, default='PEN')
    
    balance = models.DecimalField("Saldo", max_digits=15, decimal_places=2, default=0)
    rate = models.DecimalField("Tasa (%)", max_digits=5, decimal_places=2, default=0)
    term = models.IntegerField("Plazo (meses)", default=0)
    payment_periodicity = models.IntegerField("Periodicidad de Pago (Días)", default=30)
    maturity_date = models.DateField("Fecha de Vencimiento", null=True, blank=True)
    
    last_movement_date = models.DateField("Última Fecha de Movimiento", null=True, blank=True)
    credit_type = models.CharField("Tipo de Crédito", max_length=150, blank=True)
    
    generic_provision = models.DecimalField("Provisión Genérica", max_digits=15, decimal_places=2, default=0)
    specific_provision = models.DecimalField("Provisión Específica", max_digits=15, decimal_places=2, default=0)
    required_provision = models.DecimalField("Provisión Requerida", max_digits=15, decimal_places=2, default=0)
    established_provision = models.DecimalField("Provisión Constituida", max_digits=15, decimal_places=2, default=0)
    interest_receivable = models.DecimalField("Interés por Cobrar", max_digits=15, decimal_places=2, default=0)
    interest_suspended = models.DecimalField("Interés Suspenso", max_digits=15, decimal_places=2, default=0)
    
    current_portfolio = models.DecimalField("Cartera Vigente", max_digits=15, decimal_places=2, default=0)
    past_due_portfolio = models.DecimalField("Cartera Vencida", max_digits=15, decimal_places=2, default=0)
    refinanced_current = models.DecimalField("Refinanciado Vigente", max_digits=15, decimal_places=2, default=0)
    refinanced_past_due = models.DecimalField("Refinanciado Vencida", max_digits=15, decimal_places=2, default=0)
    restructured_current = models.DecimalField("Reprogramación Vigente", max_digits=15, decimal_places=2, default=0)
    restructured_past_due = models.DecimalField("Reprogramación Vencida", max_digits=15, decimal_places=2, default=0)
    judicial_portfolio = models.DecimalField("Cartera Judicial", max_digits=15, decimal_places=2, default=0)
    
    agreement = models.CharField("Convenio", max_length=255, blank=True)
    advisor_code = models.CharField("Código de Analista / Solicitud", max_length=100, blank=True)
    
    guarantee_type = models.CharField("Tipo de Garantía", max_length=100, blank=True)
    guarantee_value = models.DecimalField("Valor Garantía", max_digits=15, decimal_places=2, default=0)
    
    # Operational fields
    agency = models.CharField("Agencia/Oficina", max_length=100, blank=True, null=True, db_index=True)
    advisor = models.CharField("Asesor de Crédito", max_length=255, blank=True, null=True)
    
    bucket = models.CharField("Bucket / Tramo de Mora", max_length=50, blank=True)
    days_past_due = models.IntegerField("Días de Mora", default=0, db_index=True)
    sbs_classification = models.CharField("Clasificación SBS", max_length=50, blank=True, db_index=True)
    
    provision = models.DecimalField("Provisión Mínima (Legacy)", max_digits=15, decimal_places=2, default=0)
    is_refinanced = models.BooleanField("¿Refinanciado?", default=False)
    load_date = models.DateField("Fecha de Corte / Carga", null=True, blank=True, db_index=True)
    
    class Meta:
        verbose_name = "Operación Crediticia"
        verbose_name_plural = "Operaciones Crediticias"
        constraints = [
            models.UniqueConstraint(fields=['customer', 'operation_code', 'load_date'], name='unique_op_per_cutoff')
        ]

    def __str__(self):
        return f"Op {self.operation_code} - {self.customer.name}"

class CreditRiskMetrics(models.Model):
    operation = models.OneToOneField(CreditOperation, on_delete=models.CASCADE, related_name='metrics')
    pd = models.DecimalField("Probabilidad de Incumplimiento (PD %)", max_digits=7, decimal_places=4, default=0)
    ead = models.DecimalField("Exposición (EAD)", max_digits=15, decimal_places=2, default=0)
    lgd = models.DecimalField("Pérdida Dado el Incumplimiento (LGD %)", max_digits=7, decimal_places=4, default=0)
    expected_loss = models.DecimalField("Pérdida Esperada (EL)", max_digits=15, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = "Métrica de Riesgo de Crédito"
        verbose_name_plural = "Métricas de Riesgo de Crédito"

    def save(self, *args, **kwargs):
        # Formula EL = PD * EAD * LGD (PD and LGD are percentages)
        self.expected_loss = (self.pd / 100) * self.ead * (self.lgd / 100)
        super().save(*args, **kwargs)


class CreditRiskPeriodParameter(models.Model):
    load_date = models.DateField("Fecha de Corte", unique=True)
    patrimonio_efectivo = models.DecimalField("Patrimonio Efectivo", max_digits=18, decimal_places=2, default=500000000.0)
    monto_mitigador = models.DecimalField("Monto Mitigador (Calculado)", max_digits=18, decimal_places=2, default=50000000.0)
    description = models.TextField("Descripción / Notas", blank=True)
    
    class Meta:
        verbose_name = "Parámetro de Riesgo por Periodo"
        verbose_name_plural = "Parámetros de Riesgo por Periodo"
        ordering = ['-load_date']

    def __str__(self):
        return f"{self.load_date} - Patrimonio: {self.monto_mitigador}"
