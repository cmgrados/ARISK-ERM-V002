from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'position', 'department', 'groups', 'is_risk_manager', 'is_auditor', 'is_superuser')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.Select(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
            'groups': forms.SelectMultiple(attrs={'class': 'form-control select2'}),
            'is_risk_manager': forms.CheckboxInput(attrs={'class': 'custom-control-input'}),
            'is_auditor': forms.CheckboxInput(attrs={'class': 'custom-control-input'}),
            'is_superuser': forms.CheckboxInput(attrs={'class': 'custom-control-input'}),
        }

class CustomUserChangeForm(UserChangeForm):
    password = None # La edición no maneja cambio de contraseña directamente
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'position', 'department', 'groups', 'is_risk_manager', 'is_auditor', 'is_superuser')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.Select(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
            'groups': forms.SelectMultiple(attrs={'class': 'form-control select2'}),
            'is_risk_manager': forms.CheckboxInput(attrs={'class': 'custom-control-input'}),
            'is_auditor': forms.CheckboxInput(attrs={'class': 'custom-control-input'}),
            'is_superuser': forms.CheckboxInput(attrs={'class': 'custom-control-input'}),
        }
