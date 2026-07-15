from django.db import models

class BulkLoadLog(models.Model):
    LOAD_TYPES = [
        ('CREDIT', 'Cartera de Créditos'),
        ('LIABILITY', 'Pasivos / Depósitos'),
        ('SOCIO', 'Base de Socios'),
    ]
    file_name = models.CharField(max_length=255)
    load_type = models.CharField(max_length=20, choices=LOAD_TYPES, default='CREDIT')
    load_date = models.DateTimeField(auto_now_add=True)
    cut_off_dates = models.TextField(help_text="Lista de fechas de corte identificadas en la carga", null=True, blank=True)
    records_processed = models.IntegerField(default=0)
    status = models.CharField(max_length=50, default='Success')
    error_message = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['-load_date']

    def __str__(self):
        return f"{self.file_name} - {self.load_date.strftime('%Y-%m-%d %H:%M')}"

    @property
    def dates_list(self):
        if self.cut_off_dates:
            return self.cut_off_dates.split(',')
        return []

class Socio(models.Model):
    # Identificación
    csocio = models.CharField(max_length=50, null=True, blank=True, help_text="CÓDIGO DE SOCIO")
    tid = models.IntegerField(null=True, blank=True, help_text="TIPO DE SOCIO, DONDE 1 ES PERSONA NATURAL Y 2 ES PERSONA JURIDICA")
    nid = models.CharField(max_length=50, null=True, blank=True, help_text="NÚMERO DE DOCUMENTOS DE IDENTIDAD DNI O RUC")
    ncl = models.CharField(max_length=255, null=True, blank=True, help_text="APELLIDOS Y NOMBRES O RAZÓN SOCIAL")
    
    # Datos Institucionales
    condsocio = models.CharField(max_length=100, null=True, blank=True, help_text="CONDICIÓN DE SOCIO HABIL O INHABIL")
    codoficina = models.CharField(max_length=50, null=True, blank=True, help_text="CODIGO DE OFICINA")
    oficina = models.CharField(max_length=255, null=True, blank=True, help_text="NOMBRE DE OFICINA")
    fingreso = models.DateField(null=True, blank=True, help_text="FECHA DE INGRESO")
    aportes = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True, help_text="SALDO DE APORTACIONES")
    corte = models.DateField(null=True, blank=True, help_text="FECHA DE CORTE")

    # Datos de Contacto
    direccion = models.TextField(null=True, blank=True, help_text="DIRECCIÓN DE DOMICILIO")
    telefono = models.CharField(max_length=50, null=True, blank=True, help_text="CELULAR")
    correo = models.EmailField(null=True, blank=True, help_text="CORREO")
    
    # Metadatos de Carga
    load_log = models.ForeignKey('BulkLoadLog', on_delete=models.CASCADE, related_name='socios', null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.nid} - {self.ncl}"

class LiqAccountPlanModel(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="Nombre del modelo de plan de cuentas (ej. ESTANDAR)")
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class LiqAccountMapping(models.Model):
    ACCOUNT_TYPES = [
        ('ACT', 'Activo'),
        ('PAS', 'Pasivo'),
        ('PAT', 'Patrimonio'),
        ('ING', 'Ingreso'),
        ('GAS', 'Gasto'),
        ('OTR', 'Otro'),
    ]
    CURRENCIES = [
        ('PEN', 'Soles (S/)'),
        ('USD', 'Dólares ($)'),
        ('EUR', 'Euros (€)'),
    ]
    DISTRIBUTION_RULES = [
        ('SCHEDULE', 'Por Cronograma'),
        ('HISTORICAL', 'Distribución Histórica'),
        ('CONTRACTUAL', 'Vencimiento Contractual'),
        ('IMMEDIATE', 'Disponibilidad Inmediata'),
        ('OTHER', 'Otros'),
    ]
    DATA_SOURCES = [
        ('BALANCE', 'Balance General (Contabilidad)'),
        ('CREDIT_RISK', 'Módulo Riesgo Crediticio'),
        ('MANUAL', 'Ingreso Manual'),
        ('CORE', 'Core Bancario / Otras Tablas'),
    ]

    plan_model = models.ForeignKey(LiqAccountPlanModel, on_delete=models.CASCADE, related_name='mappings')
    account_code = models.CharField(max_length=50, help_text="Código contable")
    account_name = models.CharField(max_length=255, help_text="Nombre de la cuenta")
    liquidity_category = models.CharField(max_length=100, null=True, blank=True, help_text="Categoría de liquidez asignada (ej. Activo Líquido, Pasivo Volátil)")
    liquidity_item = models.CharField(max_length=100, null=True, blank=True, help_text="Rubro Liquidez")
    account_type = models.CharField(max_length=3, choices=ACCOUNT_TYPES, default='OTR')
    currency = models.CharField(max_length=3, choices=CURRENCIES, default='PEN')
    distribution_rule = models.CharField(max_length=20, choices=DISTRIBUTION_RULES, default='OTHER')
    data_source = models.CharField(max_length=20, choices=DATA_SOURCES, default='BALANCE')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('plan_model', 'account_code')

    def __str__(self):
        return f"{self.account_code} - {self.account_name} ({self.liquidity_category})"

class DatabaseBackup(models.Model):
    file_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)
    size_bytes = models.BigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='Success')
    is_scheduled = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.file_name
