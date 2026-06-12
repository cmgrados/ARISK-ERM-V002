from django.db import models
from django.contrib.auth.models import AbstractUser
import threading

_thread_locals = threading.local()

def get_current_organization():
    return getattr(_thread_locals, 'organization_id', None)

class TenantManager(models.Manager):
    """
    Manager personalizado para todos los modelos del negocio.
    Filtra automáticamente por el organization_id del hilo actual.
    """
    def get_queryset(self):
        queryset = super().get_queryset()
        current_org_id = get_current_organization()
        if current_org_id:
            return queryset.filter(organization_id=current_org_id)
        return queryset

class Organization(models.Model):
    """
    Representa a una Cooperativa o Entidad. 
    Este es el núcleo del sistema Multitenant.
    """
    name = models.CharField(max_length=200, unique=True, verbose_name="Nombre de la Cooperativa")
    ruc = models.CharField(max_length=20, unique=True, verbose_name="RUC", null=True, blank=True)
    is_active = models.BooleanField(default=True, verbose_name="Activa")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Organización/Cooperativa"
        verbose_name_plural = "Organizaciones/Cooperativas"

    def __str__(self):
        return self.name

class Role(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre del Perfil")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")
    permissions = models.JSONField(default=dict, blank=True, verbose_name="Permisos")
    
    def __str__(self):
        return self.name

class User(AbstractUser):
    organization = models.ForeignKey(
        Organization, 
        on_delete=models.CASCADE, 
        related_name='users',
        null=True, 
        blank=True,
        verbose_name="Cooperativa"
    )
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Perfil de Usuario")
    # Permisos genéricos y banderas base para el sistema ERM
    is_risk_manager = models.BooleanField(
        default=False, 
        help_text="Indica si el usuario es un gestor de riesgos certificado."
    )
    is_auditor = models.BooleanField(
        default=False,
        help_text="Indica si el usuario tiene rol de solo lectura/auditoría profunda."
    )
    
    # Permisos de acceso a módulos principales (Legacy / Standalone)
    # Recomendado: Usar el campo `role` para perfiles granulares.
    hidden_modules = models.JSONField(default=list, blank=True, verbose_name="Módulos Ocultos")
    can_access_integral_risk_flag = models.BooleanField(
        default=True,
        verbose_name="Acceso (Legacy): Gestión Integral de Riesgos",
    )
    can_access_financial_planning_flag = models.BooleanField(
        default=True,
        verbose_name="Acceso (Legacy): Planeamiento Financiero",
    )
    can_access_strategic_planning_flag = models.BooleanField(
        default=True,
        verbose_name="Acceso (Legacy): Planeamiento Estratégico",
    )
    
    @property
    def can_access_integral_risk(self):
        if self.is_superuser: return True
        if self.role and self.role.permissions.get('integral_risk', {}).get('acceder', False):
            return True
        return self.can_access_integral_risk_flag

    @property
    def can_access_financial_planning(self):
        if self.is_superuser: return True
        if self.role and self.role.permissions.get('financial_planning', {}).get('acceder', False):
            return True
        return self.can_access_financial_planning_flag

    @property
    def can_access_strategic_planning(self):
        if self.is_superuser: return True
        if self.role and self.role.permissions.get('strategic_planning', {}).get('acceder', False):
            return True
        return self.can_access_strategic_planning_flag

    def has_module_perms(self, module_name, action='acceder'):
        if self.is_superuser: return True
        if self.role:
            return self.role.permissions.get(module_name, {}).get(action, False)
        return False
        
    def __str__(self):
        return f"{self.username} - {self.get_full_name() or self.email}"

class AuditLog(models.Model):
    ACTION_CHOICES = (
        ('CREATE', 'Creación'),
        ('UPDATE', 'Actualización'),
        ('DELETE', 'Eliminación'),
        ('LOGIN', 'Inicio de sesión'),
        ('LOGOUT', 'Cierre de sesión'),
        ('ACCESS', 'Acceso a módulo'),
        ('OTHER', 'Otra acción'),
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs', verbose_name="Usuario responsable")
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name="Acción")
    module = models.CharField(max_length=100, verbose_name="Módulo / Entidad")
    description = models.TextField(verbose_name="Descripción detallada")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="Dirección IP")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y Hora")
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Registro de Auditoría"
        verbose_name_plural = "Registros de Auditoría"

    def __str__(self):
        return f"{self.get_action_display()} en {self.module} por {self.user} el {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"

class TenantAwareModel(models.Model):
    """
    Clase abstracta de la que deben heredar todos tus modelos de negocio
    (Estrategias, Objetivos, Proyectos, etc.) para aplicar aislamiento de datos.
    """
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, verbose_name="Cooperativa")
    
    objects = TenantManager() # Filtro automático aplicado
    all_objects = models.Manager() # Manager base para ver todo sin filtro

    class Meta:
        abstract = True
