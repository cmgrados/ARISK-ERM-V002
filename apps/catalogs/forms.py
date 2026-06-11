from django import forms
from .models import OrganizationalUnit, Process, Subprocess

class OrganizationalUnitForm(forms.ModelForm):
    class Meta:
        model = OrganizationalUnit
        fields = ['name', 'description', 'is_agency', 'parent']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Finanzas, Tesorería...'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción de las funciones...'}),
            'is_agency': forms.CheckboxInput(attrs={'class': 'custom-control-input', 'id': 'isAgencyCheck'}),
            'parent': forms.Select(attrs={'class': 'form-control select2'}),
        }

class ProcessForm(forms.ModelForm):
    class Meta:
        model = Process
        fields = ['name', 'description', 'owner']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Gestión de Créditos...'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción del proceso...'}),
            'owner': forms.Select(attrs={'class': 'form-control select2'}),
        }

class SubprocessForm(forms.ModelForm):
    class Meta:
        model = Subprocess
        fields = ['process', 'name', 'description']
        widgets = {
            'process': forms.Select(attrs={'class': 'form-control select2'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Evaluación Crediticia...'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción del subproceso...'}),
        }
