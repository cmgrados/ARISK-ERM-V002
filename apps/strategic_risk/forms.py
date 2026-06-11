from django import forms
from .models import StrategicPlan, ExternalEnvironment, FinancialEnvironment, InternalDiagnosis

class StrategicPlanForm(forms.ModelForm):
    class Meta:
        model = StrategicPlan
        fields = ['name', 'institution', 'start_year', 'horizon_years', 'status', 'version']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Plan Estratégico 2026-2028'}),
            'institution': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la Institución'}),
            'start_year': forms.NumberInput(attrs={'class': 'form-control', 'min': '2000', 'max': '2100'}),
            'horizon_years': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'version': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ExternalEnvironmentForm(forms.ModelForm):
    class Meta:
        model = ExternalEnvironment
        exclude = ['plan']
        widgets = {
            'international_analysis': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'national_analysis': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'economic_vars': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'regulatory_vars': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'social_vars': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'technological_vars': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'competitive_vars': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'conclusions': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

class FinancialEnvironmentForm(forms.ModelForm):
    class Meta:
        model = FinancialEnvironment
        exclude = ['plan']
        widgets = {
            'system_structure': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'credit_analysis': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'deposit_analysis': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'trends_rates': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'observations': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

class InternalDiagnosisForm(forms.ModelForm):
    class Meta:
        model = InternalDiagnosis
        exclude = ['plan']
        widgets = {
            'operations_scope': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'credit_analysis': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'delinquency_analysis': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'deposit_analysis': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'interest_rates': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'strengths': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'weaknesses': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
