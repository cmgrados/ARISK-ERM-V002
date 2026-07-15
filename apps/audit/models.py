from django.db import models
from django.conf import settings

class ActivityLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Usuario")
    action = models.CharField(max_length=50, verbose_name="Acción")
    path = models.CharField(max_length=255, verbose_name="Ruta")
    description = models.TextField(blank=True, verbose_name="Descripción")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="Dirección IP")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y Hora")

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Log de Actividad"
        verbose_name_plural = "Logs de Actividad"

    def __str__(self):
        username = self.user.username if self.user else 'Anónimo'
        return f"{username} - {self.action} - {self.path} - {self.timestamp}"
