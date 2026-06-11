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

