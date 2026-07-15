from django import forms
from .models import Risk

class RiskForm(forms.ModelForm):
    class Meta:
        model = Risk
        fields = ['risk_type', 'process', 'name', 'description', 'causes', 'consequences', 'owner']
        widgets = {
            'risk_type': forms.Select(attrs={'class': 'form-control'}),
            'process': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del riesgo'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'causes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'consequences': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'owner': forms.Select(attrs={'class': 'form-control'}),
        }
