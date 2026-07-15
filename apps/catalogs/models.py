from django.db import models

class Company(models.Model):
    name = models.CharField("Razón Social", max_length=255)
    tax_id = models.CharField("RUC", max_length=20, unique=True)
    address = models.CharField("Dirección", max_length=255, blank=True)
    headquarters = models.CharField("Oficina Principal", max_length=255, blank=True)
    description = models.TextField("Descripción", blank=True)
    logo = models.ImageField("Logo", upload_to='companies/', blank=True, null=True)
    
    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"

    def __str__(self):
        return self.name

class Site(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='sites', verbose_name="Empresa")
    code = models.CharField("Código de Agencia", max_length=50, blank=True)
    name = models.CharField("Nombre de la Agencia", max_length=255)
    address = models.CharField("Dirección", max_length=255, blank=True)
    responsible = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='managed_agencies', verbose_name="Responsable"
    )
    
    class Meta:
        verbose_name = "Agencia"
        verbose_name_plural = "Agencias"

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
    is_active = models.BooleanField("Activo", default=True)
    parent = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children'
    )
    
    class Meta:
        verbose_name = "Área / Unidad"
        verbose_name_plural = "Áreas / Unidades"

    def __str__(self):
        return self.name

class Position(models.Model):
    name = models.CharField("Cargo", max_length=255)
    description = models.TextField("Descripción", blank=True)
    department = models.ForeignKey(
        OrganizationalUnit, on_delete=models.CASCADE, related_name='positions',
        verbose_name="Área / Departamento", null=True, blank=True
    )
    is_active = models.BooleanField("Activo", default=True)
    
    class Meta:
        verbose_name = "Cargo"
        verbose_name_plural = "Cargos"

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

class RiskCatalog(models.Model):
    name = models.CharField("Nombre del Riesgo", max_length=200, unique=True)
    description = models.TextField("Descripción / Notas", blank=True)

    class Meta:
        verbose_name = "Catálogo de Riesgo"
        verbose_name_plural = "Catálogo de Riesgos"

    def __str__(self):
        return self.name

class Parameter(models.Model):
    key = models.CharField("Clave", max_length=100, unique=True)
    value = models.CharField("Valor", max_length=255)
    description = models.TextField("Descripción", blank=True)
    
    class Meta:
        verbose_name = "Parámetro"
        verbose_name_plural = "Parámetros"

    def __str__(self):
        return self.key

class SystemIntegration(models.Model):
    PROVIDER_CHOICES = [
        ('gemini', 'Google Gemini'),
        ('openai', 'OpenAI (ChatGPT)'),
        ('mistral', 'Mistral AI'),
        ('google_drive', 'Google Drive'),
        ('google_calendar', 'Google Calendar'),
    ]
    provider = models.CharField("Proveedor", max_length=50, choices=PROVIDER_CHOICES, unique=True)
    api_key = models.CharField("Clave API (Simple)", max_length=255, blank=True, null=True, help_text="Ej: API Key de Gemini")
    json_credentials = models.TextField("Credenciales JSON", blank=True, null=True, help_text="Pega el contenido del credentials.json aquí")
    extra_config = models.CharField("Configuración Extra (Ej: Folder ID)", max_length=255, blank=True, null=True)
    is_active = models.BooleanField("Activo", default=True)

    class Meta:
        verbose_name = "Integración del Sistema"
        verbose_name_plural = "Integraciones del Sistema"

    def __str__(self):
        return self.get_provider_display()

class AIModulePrompt(models.Model):
    MODULE_CHOICES = [
        ('op_risk', 'Riesgo Operacional'),
        ('credit_risk', 'Riesgo de Crédito'),
        ('strategic_risk', 'Riesgo Estratégico'),
    ]
    MODEL_CHOICES = [
        ('gemini-flash-latest', 'Gemini Flash (Rápido)'),
        ('gemini-pro-latest', 'Gemini Pro (Avanzado)'),
        ('gpt-4o', 'GPT-4o (Avanzado)'),
        ('gpt-4o-mini', 'GPT-4o Mini (Rápido)'),
        ('mistral-large-latest', 'Mistral Large'),
        ('mistral-small-latest', 'Mistral Small'),
    ]
    module = models.CharField("Módulo", max_length=50, choices=MODULE_CHOICES, unique=True)
    provider = models.ForeignKey(SystemIntegration, on_delete=models.CASCADE, limit_choices_to={'provider__in': ['gemini', 'openai', 'mistral']}, verbose_name="Proveedor de IA")
    model_name = models.CharField("Modelo (Ej: gpt-4o, gemini-flash-latest)", max_length=100, choices=MODEL_CHOICES, default='gemini-flash-latest', help_text="Nombre exacto del modelo según la API del proveedor.")
    system_prompt = models.TextField("Prompt del Sistema", help_text="Instrucciones base (Rol) para la IA en este módulo.")
    is_active = models.BooleanField("Activo", default=True)

    class Meta:
        verbose_name = "Prompt de IA por Módulo"
        verbose_name_plural = "Prompts de IA por Módulo"

    def __str__(self):
        return f"Prompt para {self.get_module_display()} ({self.provider.get_provider_display()})"
