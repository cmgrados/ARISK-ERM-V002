from django import forms
from .models import ComplianceRisk, ComplianceRequirement
from catalogs.models import OrganizationalUnit

class ComplianceRiskForm(forms.ModelForm):
    # We might want to create a Requirement on the fly or select an existing one.
    # But usually, it's better to select an area and then define the requirement.
    # The user said "según las áreas registradas en sistemas y administración".
    
    responsible_area = forms.ModelChoiceField(
        queryset=OrganizationalUnit.objects.all(),
        label="Área Responsable",
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    source = forms.ChoiceField(
        choices=ComplianceRequirement.SOURCE_CHOICES,
        label="Fuente",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    requirement_description = forms.CharField(
        label="Descripción del Requisito",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    
    potential_sanction = forms.CharField(
        label="Sanción Potencial (Multas/Medidas)",
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Ej: Multa de 1 UIT...'})
    )

    class Meta:
        model = ComplianceRisk
        fields = [
            'inherent_probability', 'inherent_impact', 
            'existing_controls', 
            'residual_probability', 'residual_impact',
            'indicator', 'monitoring_frequency', 'evaluation_period'
        ]
        widgets = {
            'inherent_probability': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'inherent_impact': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'existing_controls': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'residual_probability': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'residual_impact': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'indicator': forms.TextInput(attrs={'class': 'form-control'}),
            'monitoring_frequency': forms.Select(attrs={'class': 'form-control'}),
            'evaluation_period': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        # First create the requirement
        area = self.cleaned_data['responsible_area']
        source = self.cleaned_data['source']
        desc = self.cleaned_data['requirement_description']
        sanction = self.cleaned_data['potential_sanction']
        
        requirement, _ = ComplianceRequirement.objects.get_or_create(
            description=desc,
            source=source,
            responsible_area=area,
            defaults={'potential_sanction': sanction}
        )
        
        instance = super().save(commit=False)
        instance.requirement = requirement
        if commit:
            instance.save()
        return instance
