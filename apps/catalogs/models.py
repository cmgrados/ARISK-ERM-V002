from django.db import models

class Company(models.Model):
    name = models.CharField("Nombre de la Empresa", max_length=255)
    tax_id = models.CharField("RUC / Tax ID", max_length=20, unique=True)
    description = models.TextField("Descripción", blank=True)
    logo = models.ImageField("Logo", upload_to='companies/', blank=True, null=True)
    
    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"

    def __str__(self):
        return self.name

class Site(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='sites', verbose_name="Empresa")
    name = models.CharField("Sede / Local", max_length=255)
    address = models.CharField("Dirección", max_length=255, blank=True)
    
    class Meta:
        verbose_name = "Sede"
        verbose_name_plural = "Sedes"

    def __str__(self):
        return f"{self.name} ({self.company.name})"

class Management(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='managements', verbose_name="Sede")
    name = models.CharField("Gerencia", max_length=255)
    description = models.TextField("Descripción", blank=True)
    
    class Meta:
        verbose_name = "Gerencia"
        verbose_name_plural = "Gerencias"

    def __str__(self):
        return f"{self.name} - {self.site.name}"

class OrganizationalUnit(models.Model):
    management = models.ForeignKey(Management, on_delete=models.CASCADE, related_name='areas', verbose_name="Gerencia", null=True, blank=True)
    name = models.CharField("Área / Departamento", max_length=255)
    description = models.TextField("Descripción", blank=True)
    is_agency = models.BooleanField("¿Es una agencia?", default=False)
    parent = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children'
    )
    
    class Meta:
        verbose_name = "Área / Unidad"
        verbose_name_plural = "Áreas / Unidades"

    def __str__(self):
        return self.name

class Process(models.Model):
    CLASSIFICATION_CHOICES = (
        ('STRATEGIC', 'Estratégico'),
        ('MISSIONAL', 'Misional'),
        ('SUPPORT', 'Apoyo'),
    )
    
    STATUS_CHOICES = (
        ('ACTIVE', 'Activo'),
        ('INACTIVE', 'Inactivo'),
        ('UNDER_REVIEW', 'En Revisión'),
    )

    code = models.CharField("Código", max_length=20, unique=True, null=True)
    name = models.CharField("Nombre del Proceso", max_length=255)
    classification = models.CharField("Clasificación", max_length=20, choices=CLASSIFICATION_CHOICES, default='MISSIONAL')
    objective = models.TextField("Objetivo", blank=True)
    description = models.TextField("Descripción", blank=True)
    frequency = models.CharField("Frecuencia", max_length=100, blank=True, help_text="Ej: Diario, Mensual")
    status = models.CharField("Estado", max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    
    owner = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL, null=True, related_name='owned_processes',
        verbose_name="Responsable del Proceso"
    )
    unit = models.ForeignKey(
        OrganizationalUnit, on_delete=models.SET_NULL, null=True, blank=True, 
        related_name='processes', verbose_name="Área Asociada"
    )
    
    class Meta:
        verbose_name = "Proceso"
        verbose_name_plural = "Procesos"

    def __str__(self):
        return f"{self.code or 'S/C'} - {self.name}"

class Subprocess(models.Model):
    process = models.ForeignKey(Process, on_delete=models.CASCADE, related_name='subprocesses')
    code = models.CharField("Código", max_length=20, unique=True, null=True)
    name = models.CharField("Nombre del Subproceso", max_length=255)
    description = models.TextField("Descripción", blank=True)
    
    class Meta:
        verbose_name = "Subproceso"
        verbose_name_plural = "Subprocesos"

    def __str__(self):
        return f"{self.process.name} >> {self.name}"

class Activity(models.Model):
    subprocess = models.ForeignKey(Subprocess, on_delete=models.CASCADE, related_name='activities')
    code = models.CharField("Código", max_length=20, unique=True, null=True)
    name = models.CharField("Nombre de la Actividad", max_length=255)
    description = models.TextField("Descripción", blank=True)
    responsible = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL, null=True, related_name='responsible_activities',
        verbose_name="Responsable"
    )

    class Meta:
        verbose_name = "Actividad"
        verbose_name_plural = "Actividades"

    def __str__(self):
        return f"{self.subprocess.name} >> {self.name}"

class Product(models.Model):
    name = models.CharField("Nombre del Producto", max_length=255)
    description = models.TextField("Descripción", blank=True)
    is_active = models.BooleanField("Activo", default=True)
    
    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

    def __str__(self):
        return self.name

class RiskType(models.Model):
    code = models.CharField("Código de Riesgo", max_length=20, unique=True, help_text="Ej: OP, CR, LI")
    name = models.CharField("Nombre", max_length=255)
    description = models.TextField("Descripción", blank=True)
    
    class Meta:
        verbose_name = "Tipo de Riesgo"
        verbose_name_plural = "Tipos de Riesgo"

    def __str__(self):
        return f"[{self.code}] {self.name}"

class Parameter(models.Model):
    key = models.CharField("Clave", max_length=100, unique=True)
    value = models.CharField("Valor", max_length=255)
    description = models.TextField("Descripción", blank=True)
    
    class Meta:
        verbose_name = "Parámetro"
        verbose_name_plural = "Parámetros"

    def __str__(self):
        return self.key
