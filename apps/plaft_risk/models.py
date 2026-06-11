from django.db import models

class PlaftCustomerProfile(models.Model):
    RISK_LEVELS = (
        ('LOW', 'Bajo'),
        ('MEDIUM', 'Medio'),
        ('HIGH', 'Alto'),
        ('CRITICAL', 'Crítico'),
    )
    customer_id = models.CharField("ID Socio", max_length=50, unique=True)
    full_name = models.CharField("Nombre Completo", max_length=255)
    risk_level = models.CharField("Nivel de Riesgo", max_length=10, choices=RISK_LEVELS, default='LOW')
    last_review = models.DateField("Última Revisión", auto_now=True)
    is_pep = models.BooleanField("Es PEP", default=False)
    
    class Meta:
        verbose_name = "Perfil PLAFT de Cliente"
        verbose_name_plural = "Perfiles PLAFT de Clientes"
        
    def __str__(self):
        return f"{self.customer_id} - {self.full_name}"

class PlaftAlert(models.Model):
    STATE_CHOICES = (
        ('PENDING', 'Pendiente'),
        ('ANALYZING', 'En Análisis'),
        ('DISCARDED', 'Descartada'),
        ('ROS', 'Reportada (ROS)'),
    )
    customer = models.ForeignKey(PlaftCustomerProfile, on_delete=models.CASCADE, verbose_name="Socio")
    alert_type = models.CharField("Tipo de Alerta", max_length=100)
    description = models.TextField("Descripción")
    date_triggered = models.DateTimeField("Fecha de Activación", auto_now_add=True)
    status = models.CharField("Estado", max_length=20, choices=STATE_CHOICES, default='PENDING')
    
    class Meta:
        verbose_name = "Alerta PLAFT"
        verbose_name_plural = "Alertas PLAFT"
        
    def __str__(self):
        return f"Alerta {self.alert_type} - {self.customer.customer_id}"
