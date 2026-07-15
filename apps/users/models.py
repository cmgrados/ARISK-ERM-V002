from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # Permisos genéricos y banderas base para el sistema ERM
    is_risk_manager = models.BooleanField(
        default=False, 
        help_text="Indica si el usuario es un gestor de riesgos certificado."
    )
    is_auditor = models.BooleanField(
        default=False,
        help_text="Indica si el usuario tiene rol de solo lectura/auditoría profunda."
    )
    # Información Corporativa
    position = models.ForeignKey(
        'catalogs.Position', on_delete=models.SET_NULL, blank=True, null=True, 
        verbose_name="Cargo"
    )
    department = models.ForeignKey(
        'catalogs.OrganizationalUnit', on_delete=models.SET_NULL, blank=True, null=True, 
        verbose_name="Área / Departamento"
    )
    
    def __str__(self):
        base_name = f"{self.username} - {self.get_full_name() or self.email}"
        if self.position and self.department:
            return f"{base_name} ({self.position} - {self.department})"
        return base_name
