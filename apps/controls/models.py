from django.db import models
from django.utils import timezone

class RiskControl(models.Model):
    CONTROL_TYPES = (
        ('PREVENTIVE', 'Preventivo'),
        ('DETECTIVE', 'Detectivo'),
        ('CORRECTIVE', 'Correctivo'),
    )
    
    risk = models.ForeignKey('risks.Risk', on_delete=models.CASCADE, related_name='controls')
    name = models.CharField("Nombre del Control", max_length=255)
    description = models.TextField("Descripción", blank=True)
    control_type = models.CharField("Tipo de Control", max_length=20, choices=CONTROL_TYPES)
    owner = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL, null=True, verbose_name="Dueño del Control"
    )
    frequency = models.CharField("Periodicidad", max_length=100, help_text="Ej: Diario, Mensual, Anual")
    evidence = models.FileField("Evidencia", upload_to='controls/evidence/', blank=True, null=True)
    is_active = models.BooleanField("Activo", default=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def get_latest_effectiveness(self):
        latest_test = self.tests.order_by('-test_date').first()
        return latest_test.effectiveness_score if latest_test else 0
    
    class Meta:
        verbose_name = "Control de Riesgo"
        verbose_name_plural = "Controles de Riesgo"

    def __str__(self):
        return self.name

class ControlTest(models.Model):
    control = models.ForeignKey(RiskControl, on_delete=models.CASCADE, related_name='tests')
    test_date = models.DateField("Fecha de Prueba", auto_now_add=True)
    tester = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL, null=True, verbose_name="Evaluador"
    )
    effectiveness_score = models.IntegerField("Nivel de Efectividad (1-100%)", default=100)
    comments = models.TextField("Comentarios", blank=True)
    
    class Meta:
        verbose_name = "Prueba de Control"
        verbose_name_plural = "Pruebas de Control"

    def __str__(self):
        return f"Prueba: {self.control.name} ({self.test_date})"
