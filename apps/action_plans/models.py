from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

class ActionPlan(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pendiente'),
        ('in_progress', 'En Proceso'),
        ('completed', 'Completado'),
        ('overdue', 'Vencido'),
        ('cancelled', 'Cancelado'),
    )
    
    title = models.CharField("Título de la Acción", max_length=255)
    description = models.TextField("Descripción de la Tarea")
    
    # Links
    risk = models.ForeignKey('risks.Risk', on_delete=models.CASCADE, related_name='action_plans', null=True, blank=True)
    control = models.ForeignKey('controls.RiskControl', on_delete=models.SET_NULL, null=True, blank=True, related_name='action_plans')
    
    responsible = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='assigned_actions')
    
    start_date = models.DateField("Fecha de Inicio", default=timezone.now)
    due_date = models.DateField("Fecha de Vencimiento")
    completion_date = models.DateField("Fecha de Cierre", null=True, blank=True)
    
    status = models.CharField("Estado", max_length=20, choices=STATUS_CHOICES, default='pending')
    progress = models.IntegerField("Progreso (%)", default=0)
    
    class Meta:
        verbose_name = "Plan de Acción"
        verbose_name_plural = "Planes de Acción"

    def clean(self):
        # Regla: No plan sin justificación
        if not self.risk and not self.control:
            raise ValidationError("Regla Operativa: Todo plan de acción debe estar vinculado a un riesgo o un control (justificación).")
        
        # Regla: No cerrar sin evidencia
        if self.status == 'completed':
            if not self.follow_ups.filter(evidence__isnull=False).exists():
                 raise ValidationError("Regla Operativa: No se puede completar una acción sin adjuntar evidencia en el seguimiento.")

    @property
    def is_overdue(self):
        return self.status != 'completed' and self.due_date < timezone.now().date()

    @property
    def is_upcoming(self):
        # Within next 7 days
        return self.status != 'completed' and not self.is_overdue and self.due_date <= (timezone.now().date() + timezone.timedelta(days=7))

    def save(self, *args, **kwargs):
        if self.status == 'completed' and not self.completion_date:
            self.completion_date = timezone.now().date()
        # Update status if overdue
        if self.is_overdue and self.status not in ['completed', 'cancelled']:
            self.status = 'overdue'
            
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class ActionFollowUp(models.Model):
    action_plan = models.ForeignKey(ActionPlan, on_delete=models.CASCADE, related_name='follow_ups')
    follow_up_date = models.DateTimeField("Fecha de Seguimiento", auto_now_add=True)
    comment = models.TextField("Comentario / Avance")
    performed_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)
    
    evidence = models.FileField("Evidencia", upload_to='action_plans/evidence/', null=True, blank=True)
    
    class Meta:
        verbose_name = "Seguimiento de Acción"
        verbose_name_plural = "Seguimientos de Acción"

    def __str__(self):
        return f"Seguimiento {self.action_plan.title} - {self.follow_up_date.date()}"
