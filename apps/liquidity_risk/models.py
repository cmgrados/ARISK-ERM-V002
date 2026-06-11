from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

# ==============================================================================
# 1. CARGA DE INFORMACIÓN (UPLOADS & DETAILS)
# ==============================================================================

class LiqLoadStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pendiente'
    VALIDATING = 'VALIDATING', 'Validando'
    SUCCESS = 'SUCCESS', 'Cargado con éxito'
    ERROR = 'ERROR', 'Error'
    APPROVED = 'APPROVED', 'Aprobado'

class LiqBalanceUpload(models.Model):
    period = models.DateField("Periodo", db_index=True)
    file_source = models.FileField("Archivo Fuente", upload_to='liquidity/balance/')
    status = models.CharField(max_length=20, choices=LiqLoadStatus.choices, default=LiqLoadStatus.PENDING)
    observations = models.TextField("Observaciones", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    plan_model = models.ForeignKey('LiqAccountPlanModel', on_delete=models.SET_NULL, null=True, verbose_name="Modelo de Plan")
    CURRENCY_CHOICES = [
        ('MN', 'Soles (MN)'),
        ('ME', 'Dólares (ME)'),
        ('MX', 'Integrado (Soles + Dólares)')
    ]
    currency = models.CharField("Moneda", max_length=2, choices=CURRENCY_CHOICES, default='MN')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = "Carga de Balance"
        unique_together = ('period',)

class LiqBalanceDetail(models.Model):
    upload = models.ForeignKey(LiqBalanceUpload, on_delete=models.CASCADE, related_name='details')
    period = models.DateField("Periodo", db_index=True)
    currency = models.CharField("Moneda", max_length=10, db_index=True) # MN, ME
    account_code = models.CharField("Código Contable", max_length=20, db_index=True)
    account_name = models.CharField("Nombre Cuenta", max_length=255)
    balance = models.DecimalField("Saldo", max_digits=18, decimal_places=2)
    nature = models.CharField("Naturaleza", max_length=1, choices=[('D', 'Deudora'), ('A', 'Acreedora')])
    liquidity_item = models.CharField("Rubro de Liquidez", max_length=100, blank=True, db_index=True)

    class Meta:
        verbose_name = "Detalle de Balance"

class LiqLiabilityUpload(models.Model):
    period = models.DateField("Periodo", db_index=True)
    file_source = models.FileField("Archivo Fuente", upload_to='liquidity/liabilities/')
    status = models.CharField(max_length=20, choices=LiqLoadStatus.choices, default=LiqLoadStatus.PENDING)
    observations = models.TextField("Observaciones", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = "Carga de Pasivos"
        unique_together = ('period',)

class LiqLiabilityDetail(models.Model):
    upload = models.ForeignKey(LiqLiabilityUpload, on_delete=models.CASCADE, related_name='details')
    period = models.DateField("Periodo", db_index=True)
    
    # Source Fields
    agency = models.CharField("Agencia", max_length=100)
    opening_agency = models.CharField("A.G. Apertura", max_length=100, blank=True)
    customer_id = models.CharField("Socio", max_length=50, db_index=True)
    customer_name = models.CharField("Apellidos y Nombres", max_length=255)
    customer_age = models.IntegerField("Edad", null=True, blank=True)
    customer_gender = models.CharField("Sexo", max_length=10, blank=True)
    customer_birth_date = models.DateField("Fecha Nacimiento", null=True, blank=True)
    opening_date = models.DateField("Fecha Apertura")
    due_date = models.DateField("Fecha Vencimiento", null=True, blank=True)
    account_number = models.CharField("Nro Cuenta", max_length=50)
    product = models.CharField("Producto", max_length=100)
    currency = models.CharField("Moneda", max_length=10, db_index=True)
    amount = models.DecimalField("Monto", max_digits=18, decimal_places=2)
    balance = models.DecimalField("Saldo", max_digits=18, decimal_places=2)
    rate = models.DecimalField("TEA", max_digits=10, decimal_places=4, default=0)
    tem = models.DecimalField("TEM", max_digits=10, decimal_places=4, default=0)
    term_days = models.IntegerField("Plazo", default=0)
    created_by_user_code = models.CharField("Usuario Crea", max_length=50, blank=True)
    captador = models.CharField("Captador", max_length=100, blank=True)
    segment = models.CharField("Segmento", max_length=100, blank=True, default="PERSONA NATURAL")
    cancellation_date = models.DateField("Fecha Cancelación", null=True, blank=True)

    # Derived Fields
    liquidity_item = models.CharField("Rubro Liquidez", max_length=100, db_index=True) # Ahorro/Plazo
    funding_type = models.CharField("Tipo Captación", max_length=20, db_index=True) # AHORRO/PLAZO
    cut_off_status = models.CharField("Estado Registro", max_length=20, db_index=True) # VIGENTE/CANCELADO
    days_to_due = models.IntegerField("Días al Vencimiento", null=True, blank=True)
    liquidity_band = models.CharField("Banda Liquidez", max_length=20, db_index=True)
    
    # Validation/Audit
    is_observed = models.BooleanField("Observado", default=False)
    observation_detail = models.TextField("Detalle Observación", blank=True)

    class Meta:
        verbose_name = "Detalle de Pasivo"
        indexes = [
            models.Index(fields=['period', 'funding_type']),
            models.Index(fields=['period', 'liquidity_band']),
        ]

class LiqSavingsUpload(models.Model):
    period = models.DateField("Periodo", db_index=True)
    file_source = models.FileField("Archivo Fuente", upload_to='liquidity/savings/')
    status = models.CharField(max_length=20, choices=LiqLoadStatus.choices, default=LiqLoadStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

class LiqSavingsAccount(models.Model):
    upload = models.ForeignKey(LiqSavingsUpload, on_delete=models.CASCADE, related_name='accounts')
    period = models.DateField("Periodo", db_index=True)
    customer_id = models.CharField("Socio", max_length=50, db_index=True)
    customer_name = models.CharField("Nombres", max_length=255, blank=True)
    document = models.CharField("Documento", max_length=20, blank=True)
    account_number = models.CharField("Cuenta", max_length=50)
    product = models.CharField("Producto", max_length=100)
    currency = models.CharField("Moneda", max_length=10, db_index=True)
    balance = models.DecimalField("Saldo", max_digits=18, decimal_places=2)
    opening_date = models.DateField("Fecha Apertura")
    last_movement_date = models.DateField("Último Movimiento", null=True, blank=True)
    agency = models.CharField("Agencia", max_length=100)
    opening_agency = models.CharField("Agencia Apertura", max_length=100, blank=True)
    segment = models.CharField("Segmento", max_length=50, blank=True)
    
    # Demographic & Ops
    customer_age = models.IntegerField("Edad", null=True, blank=True)
    customer_gender = models.CharField("Sexo", max_length=10, blank=True)
    customer_birth_date = models.DateField("Fecha Nacimiento", null=True, blank=True)
    created_by_user_code = models.CharField("Usuario Crea", max_length=50, blank=True)
    captador = models.CharField("Captador", max_length=100, blank=True)
    cancellation_date = models.DateField("Fecha Cancelación", null=True, blank=True)
    
    is_major_depositor = models.BooleanField("Gran Depositante", default=False)
    customer_type = models.CharField("Tipo Cliente", max_length=20, default='NATURAL') # NATURAL, JURIDICA, GRAN_DEPOSITANTE

class LiqTermDepositUpload(models.Model):
    period = models.DateField("Periodo", db_index=True)
    file_source = models.FileField("Archivo Fuente", upload_to='liquidity/dpf/')
    status = models.CharField(max_length=20, choices=LiqLoadStatus.choices, default=LiqLoadStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

class LiqTermDeposit(models.Model):
    upload = models.ForeignKey(LiqTermDepositUpload, on_delete=models.CASCADE, related_name='deposits')
    period = models.DateField("Periodo", db_index=True)
    customer_id = models.CharField("Socio", max_length=50, db_index=True)
    customer_name = models.CharField("Nombres", max_length=255, blank=True)
    document = models.CharField("Documento", max_length=20, blank=True)
    certificate_number = models.CharField("Certificado", max_length=50)
    product = models.CharField("Producto", max_length=100)
    currency = models.CharField("Moneda", max_length=10, db_index=True)
    amount = models.DecimalField("Monto Original", max_digits=18, decimal_places=2)
    balance = models.DecimalField("Saldo", max_digits=18, decimal_places=2, default=0)
    rate = models.DecimalField("TEA (%)", max_digits=10, decimal_places=4)
    tem = models.DecimalField("TEM (%)", max_digits=10, decimal_places=4, default=0)
    opening_date = models.DateField("Fecha Constitución")
    due_date = models.DateField("Fecha Vencimiento")
    term_days = models.IntegerField("Plazo (Días)", default=0)
    residual_term = models.IntegerField("Plazo Residual", default=0)
    agency = models.CharField("Agencia", max_length=100)
    opening_agency = models.CharField("Agencia Apertura", max_length=100, blank=True)
    
    # Demographic & Ops
    customer_age = models.IntegerField("Edad", null=True, blank=True)
    customer_gender = models.CharField("Sexo", max_length=10, blank=True)
    customer_birth_date = models.DateField("Fecha Nacimiento", null=True, blank=True)
    created_by_user_code = models.CharField("Usuario Crea", max_length=50, blank=True)
    captador = models.CharField("Captador", max_length=100, blank=True)
    cancellation_date = models.DateField("Fecha Cancelación", null=True, blank=True)
    
    is_renewable = models.BooleanField("Renovable", default=False)
    is_major_depositor = models.BooleanField("Gran Depositante", default=False)
    customer_type = models.CharField("Tipo Cliente", max_length=20, default='NATURAL') # NATURAL, JURIDICA, GRAN_DEPOSITANTE

class LiqContributor(models.Model):
    period = models.DateField("Periodo", db_index=True)
    customer_id = models.CharField("Socio", max_length=50)
    balance = models.DecimalField("Saldo Aportes", max_digits=18, decimal_places=2)
    participation_pct = models.DecimalField("Participación (%)", max_digits=10, decimal_places=4)
    ranking = models.IntegerField("Ranking")

class LiqFundingUpload(models.Model):
    period = models.DateField("Periodo", db_index=True)
    file_source = models.FileField("Archivo Fuente", upload_to='liquidity/funding/')
    status = models.CharField(max_length=20, choices=LiqLoadStatus.choices, default=LiqLoadStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

class LiqFundingLine(models.Model):
    upload = models.ForeignKey(LiqFundingUpload, on_delete=models.CASCADE, related_name='lines', null=True)
    period = models.DateField("Periodo", db_index=True)
    financial_institution = models.CharField("Institución Financiera", max_length=255)
    line_type = models.CharField("Tipo de Línea", max_length=100)
    currency = models.CharField("Moneda", max_length=10)
    approved_amount = models.DecimalField("Monto Aprobado", max_digits=18, decimal_places=2)
    used_amount = models.DecimalField("Monto Utilizado", max_digits=18, decimal_places=2)
    available_amount = models.DecimalField("Monto Disponible", max_digits=18, decimal_places=2)
    approval_date = models.DateField("Fecha Aprobación")
    due_date = models.DateField("Fecha Vencimiento")
    guarantee = models.CharField("Garantía", max_length=255)
    tea = models.DecimalField("TEA (%)", max_digits=10, decimal_places=4)
    tcea = models.DecimalField("TCEA (%)", max_digits=10, decimal_places=4)
    status = models.CharField("Estado", max_length=50)

class LiqInvestmentUpload(models.Model):
    period = models.DateField("Periodo", db_index=True)
    file_source = models.FileField("Archivo Fuente", upload_to='liquidity/investments/')
    status = models.CharField(max_length=20, choices=LiqLoadStatus.choices, default=LiqLoadStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

class LiqInvestment(models.Model):
    upload = models.ForeignKey(LiqInvestmentUpload, on_delete=models.CASCADE, related_name='investments', null=True)
    period = models.DateField("Periodo", db_index=True)
    ifi = models.CharField("Institución Financiera", max_length=255)
    investment_type = models.CharField("Tipo Inversión", max_length=100) # Caja, Bancos, CDs, etc.
    currency = models.CharField("Moneda", max_length=10)
    amount = models.DecimalField("Monto", max_digits=18, decimal_places=2)
    due_date = models.DateField("Vencimiento", null=True, blank=True)
    rating = models.CharField("Calificación", max_length=10, blank=True)
    is_restricted = models.BooleanField("Restringido", default=False)

class LiqAvailableFund(models.Model):
    period = models.DateField("Periodo", db_index=True)
    ifi = models.CharField("Institución Financiera", max_length=255)
    currency = models.CharField("Moneda", max_length=10)
    amount = models.DecimalField("Monto", max_digits=18, decimal_places=2)
    is_restricted = models.BooleanField("Restringido", default=False)

class LiqPortfolioDetail(models.Model):
    period = models.DateField("Periodo", db_index=True)
    credit_status = models.CharField("Estado Crédito", max_length=50) # Vigente, Vencido, etc.
    balance = models.DecimalField("Saldo", max_digits=18, decimal_places=2)
    mora_days = models.IntegerField("Días Mora")
    expected_recovery = models.DecimalField("Recuperación Esperada", max_digits=18, decimal_places=2)

# ==============================================================================
# 2. PARAMETRIZACIÓN & METODOLOGÍA
# ==============================================================================

class LiqAccountPlanModel(models.Model):
    name = models.CharField("Nombre del Modelo", max_length=50, unique=True)
    description = models.TextField("Descripción", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class LiqAccountMapping(models.Model):
    plan_model = models.ForeignKey(LiqAccountPlanModel, on_delete=models.CASCADE, related_name='mappings', verbose_name="Modelo de Plan")
    account_code = models.CharField("Código Contable", max_length=20)
    account_name = models.CharField("Nombre de Cuenta", max_length=255, blank=True)
    liquidity_item = models.CharField("Rubro de Liquidez", max_length=100)
    
    # Methodological Fields
    ACCOUNT_TYPE_CHOICES = [('ACT', 'Activo'), ('PAS', 'Pasivo'), ('CON', 'Contingente'), ('PAT', 'Patrimonio')]
    account_type = models.CharField("Tipo", max_length=3, choices=ACCOUNT_TYPE_CHOICES, default='ACT')
    currency = models.CharField("Moneda", max_length=2, choices=[('MN', 'Soles'), ('ME', 'Dólares'), ('MX', 'Ambas')], default='MN')
    default_band = models.ForeignKey('LiqTimeBand', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Banda por Defecto")
    
    DISTRIBUTION_RULE_CHOICES = [
        ('TOTAL', 'Total en Banda Defecto'),
        ('VOLATILE', 'Volátil (Vencimiento 0-30 días)'),
        ('SCHEDULE', 'Cronograma Residual (Auxiliar)'),
        ('STABLE', 'Estable (Bandas Largas)'),
        ('CUSTOM', 'Regla Personalizada')
    ]
    distribution_rule = models.CharField("Regla de Distribución", max_length=20, choices=DISTRIBUTION_RULE_CHOICES, default='TOTAL')
    
    DATA_SOURCE_CHOICES = [
        ('BALANCE', 'Balance de Comprobación'),
        ('AUXILIARY', 'Auxiliar Complementario'),
        ('CREDIT_RISK', 'Módulo Riesgo Crédito (Solo Lectura)'),
        ('MANUAL', 'Ingreso Manual')
    ]
    data_source = models.CharField("Origen del Dato", max_length=15, choices=DATA_SOURCE_CHOICES, default='BALANCE')
    is_active = models.BooleanField("Vigente", default=True)

    class Meta:
        unique_together = ('plan_model', 'account_code')

class LiqTimeBand(models.Model):
    name = models.CharField("Nombre de Banda", max_length=100)
    start_days = models.IntegerField("Días Inicio")
    end_days = models.IntegerField("Días Fin")
    order = models.IntegerField("Orden", default=0)

    class Meta:
        ordering = ['order']

# ==============================================================================
# 3. RESULTADOS & ANALÍTICA (POSITION, GAP, STRESS)
# ==============================================================================

class LiqMonthlyPosition(models.Model):
    period = models.DateField("Periodo", db_index=True)
    currency = models.CharField("Moneda", max_length=10)
    liquid_assets = models.DecimalField("Activos Líquidos", max_digits=18, decimal_places=2)
    short_term_liabilities = models.DecimalField("Pasivos Corto Plazo", max_digits=18, decimal_places=2)
    liquidity_ratio = models.DecimalField("Ratio Liquidez (%)", max_digits=10, decimal_places=4)
    adjusted_ratio = models.DecimalField("Ratio Ajustado (%)", max_digits=10, decimal_places=4, null=True)

class LiqMonthlyIndicator(models.Model):
    period = models.DateField("Periodo", db_index=True)
    name = models.CharField("Nombre Indicador", max_length=100)
    value = models.DecimalField("Valor", max_digits=18, decimal_places=4)
    status = models.CharField("Estado (Semáforo)", max_length=10, default='VERDE')

class LiqGapReport(models.Model):
    period = models.DateField("Periodo", db_index=True)
    currency = models.CharField("Moneda", max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)

class LiqGapDetail(models.Model):
    report = models.ForeignKey(LiqGapReport, on_delete=models.CASCADE, related_name='details')
    band = models.ForeignKey(LiqTimeBand, on_delete=models.CASCADE)
    item_name = models.CharField("Rubro", max_length=255)
    item_type = models.CharField("Tipo", max_length=10, choices=[('ACT', 'Activo'), ('PAS', 'Pasivo')])
    amount = models.DecimalField("Monto", max_digits=18, decimal_places=2)

class LiqConcentrationReport(models.Model):
    period = models.DateField("Periodo", db_index=True)
    category = models.CharField("Categoría", max_length=50) # Depositantes, Aportantes, Acreedores
    item_name = models.CharField("Nombre", max_length=255)
    balance = models.DecimalField("Saldo", max_digits=18, decimal_places=2)
    participation_pct = models.DecimalField("Participación (%)", max_digits=10, decimal_places=4)

class LiqStressScenario(models.Model):
    name = models.CharField("Nombre Escenario", max_length=255)
    description = models.TextField()
    is_custom = models.BooleanField(default=True)

class LiqStressRun(models.Model):
    period = models.DateField("Periodo", db_index=True)
    scenario = models.ForeignKey(LiqStressScenario, on_delete=models.CASCADE)
    executed_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

class LiqStressResult(models.Model):
    run = models.ForeignKey(LiqStressRun, on_delete=models.CASCADE, related_name='results')
    indicator_name = models.CharField(max_length=100)
    base_value = models.DecimalField(max_digits=18, decimal_places=4)
    stressed_value = models.DecimalField(max_digits=18, decimal_places=4)
    impact = models.DecimalField(max_digits=18, decimal_places=4)

# ==============================================================================
# 3.5 METODOLOGÍA LaR (SALDO VOLÁTIL)
# ==============================================================================

class LiqLaRConfig(models.Model):
    name = models.CharField("Nombre Segmento/Config", max_length=100)
    confidence_level = models.DecimalField("Nivel de Confianza", max_digits=5, decimal_places=4, default=0.9500)
    historical_depth = models.IntegerField("Profundidad Histórica (Meses)", default=12)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class LiqLaRResult(models.Model):
    period = models.DateField("Periodo de Cálculo", db_index=True)
    segment = models.CharField("Segmento", max_length=100, blank=True)
    currency = models.CharField("Moneda", max_length=10, db_index=True)
    
    total_balance = models.DecimalField("Saldo Total", max_digits=18, decimal_places=2)
    lar_amount = models.DecimalField("Saldo Volátil (LaR)", max_digits=18, decimal_places=2)
    lar_percentage = models.DecimalField("Volatilidad (%)", max_digits=10, decimal_places=4)
    std_dev = models.DecimalField("Desviación Estándar", max_digits=18, decimal_places=4)
    
    # Audit & Tracking
    executed_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    # Data used for the calculation (for traceability)
    calculation_data = models.JSONField("Datos de Cálculo", null=True, blank=True)
    is_official = models.BooleanField("Usar para Brechas", default=False)
    
    class Meta:
        verbose_name = "Resultado LaR"
        unique_together = ('period', 'segment', 'currency')

# ==============================================================================
# 4. LÍMITES, ALERTAS & CONTINGENCIA
# ==============================================================================

class LiqLimit(models.Model):
    indicator_name = models.CharField("Indicador", max_length=100)
    limit_min = models.DecimalField("Mínimo", max_digits=10, decimal_places=4, null=True, blank=True)
    limit_max = models.DecimalField("Máximo", max_digits=10, decimal_places=4, null=True, blank=True)
    early_warning = models.DecimalField("Alerta Temprana", max_digits=10, decimal_places=4, null=True, blank=True)
    is_active = models.BooleanField(default=True)

class LiqSbsLimit(models.Model):
    code = models.CharField("Código", max_length=50, unique=True)
    name = models.CharField("Indicador", max_length=255)
    sign = models.CharField("Signo", max_length=5, default='>=')
    limit_value = models.DecimalField("Valor Límite", max_digits=10, decimal_places=4)
    is_percentage = models.BooleanField("Es Porcentaje", default=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} {self.sign} {self.limit_value}"

class LiqAlert(models.Model):
    period = models.DateField("Periodo")
    indicator_name = models.CharField(max_length=100)
    value = models.DecimalField(max_digits=18, decimal_places=4)
    severity = models.CharField(max_length=10) # VERDE, AMARILLO, NARANJA, ROJO
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class LiqBreach(models.Model):
    alert = models.OneToOneField(LiqAlert, on_delete=models.CASCADE)
    responsible = models.CharField("Responsable", max_length=255)
    corrective_action = models.TextField("Acción Correctiva")
    comment = models.TextField("Comentario")
    resolved_at = models.DateTimeField(null=True, blank=True)

class LiqContingencyPlan(models.Model):
    name = models.CharField("Nombre del Plan", max_length=255)
    description = models.TextField()
    is_active = models.BooleanField(default=True)

class LiqContingencyActivation(models.Model):
    plan = models.ForeignKey(LiqContingencyPlan, on_delete=models.CASCADE)
    activated_at = models.DateTimeField(auto_now_add=True)
    trigger_event = models.TextField("Evento Gatillo")
    status = models.CharField("Estado", max_length=20, default='OPEN') # OPEN, CLOSED
    closed_at = models.DateTimeField(null=True, blank=True)

class LiqContingencyAction(models.Model):
    activation = models.ForeignKey(LiqContingencyActivation, on_delete=models.CASCADE, related_name='actions')
    description = models.TextField()
    responsible = models.CharField(max_length=255)
    executed_at = models.DateTimeField(null=True, blank=True)
    result = models.TextField(blank=True)

# ==============================================================================
# 5. GOBIERNO & AUDITORÍA
# ==============================================================================

class LiqReport(models.Model):
    name = models.CharField("Nombre Reporte", max_length=255)
    report_type = models.CharField(max_length=50)
    period = models.DateField()
    file_path = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

class LiqApproval(models.Model):
    object_id = models.PositiveIntegerField()
    content_type = models.CharField(max_length=100) # Simplified for now
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    approved_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20) # APPROVED, REJECTED
    comments = models.TextField(blank=True)

class LiqAuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=255)
    details = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
