from django import forms
from .models import ActionPlan, ActionFollowUp

class ActionPlanForm(forms.ModelForm):
    class Meta:
        model = ActionPlan
        fields = ['title', 'description', 'risk', 'control', 'responsible', 'start_date', 'due_date', 'status', 'progress']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Implementar autenticación multifactor'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'risk': forms.Select(attrs={'class': 'form-control'}),
            'control': forms.Select(attrs={'class': 'form-control'}),
            'responsible': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'progress': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
        }

class ActionFollowUpForm(forms.ModelForm):
    class Meta:
        model = ActionFollowUp
        fields = ['comment', 'evidence']
        widgets = {
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describa el avance...'}),
            'evidence': forms.FileInput(attrs={'class': 'form-control'}),
        }
