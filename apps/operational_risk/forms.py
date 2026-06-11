from django import forms
from .models import PotentialLoss, OpRiskIncident

class PotentialLossForm(forms.ModelForm):
    class Meta:
        model = PotentialLoss
        fields = [
            'detection_date', 'process', 'subprocess', 'area', 
            'loss_type', 'description', 'estimated_amount', 'currency', 
            'priority', 'responsible', 'evidence', 'observations'
        ]
        widgets = {
            'detection_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'process': forms.Select(attrs={'class': 'form-control'}),
            'subprocess': forms.Select(attrs={'class': 'form-control'}),
            'area': forms.Select(attrs={'class': 'form-control'}),
            'loss_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Error de caja, Fraude, etc.'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'estimated_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'currency': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'responsible': forms.Select(attrs={'class': 'form-control'}),
            'evidence': forms.FileInput(attrs={'class': 'custom-file-input'}),
            'observations': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class PotentialLossAdjustmentForm(forms.ModelForm):
    class Meta:
        model = PotentialLoss
        fields = ['gross_loss', 'recovery_amount', 'status', 'observations']
        widgets = {
            'gross_loss': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'recovery_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'observations': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class LinkLossToIncidentForm(forms.Form):
    incident = forms.ModelChoiceField(
        queryset=OpRiskIncident.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control select2'}),
        label="Seleccionar Evento Operacional"
    )
