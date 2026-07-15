from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from .models import User
from catalogs.models import Position
from .forms import CustomUserCreationForm, CustomUserChangeForm

class SuperuserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser
        
    def handle_no_permission(self):
        messages.error(self.request, "No tienes permisos para acceder a la gestiÃ³n de usuarios.")
        return redirect('home')

class UserListView(SuperuserRequiredMixin, ListView):
    model = User
    template_name = 'users/user_list.html'
    context_object_name = 'users'
    ordering = ['-date_joined']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'GestiÃ³n de Usuarios'
        return context

class UserCreateView(SuperuserRequiredMixin, CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'users/user_form.html'
    success_url = reverse_lazy('users:user_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Nuevo Usuario'
        return context

    def form_valid(self, form):
        messages.success(self.request, "Usuario creado exitosamente.")
        return super().form_valid(form)

class UserUpdateView(SuperuserRequiredMixin, UpdateView):
    model = User
    form_class = CustomUserChangeForm
    template_name = 'users/user_form.html'
    success_url = reverse_lazy('users:user_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Editar Usuario'
        return context

    def form_valid(self, form):
        messages.success(self.request, "Usuario actualizado exitosamente.")
        return super().form_valid(form)

@user_passes_test(lambda u: u.is_superuser)
def user_toggle_active(request, pk):
    user_to_toggle = get_object_or_404(User, pk=pk)
    if user_to_toggle == request.user:
        messages.error(request, "No puedes desactivar tu propia cuenta.")
        return redirect('users:user_list')
        
    user_to_toggle.is_active = not user_to_toggle.is_active
    user_to_toggle.save()
    status = "activado" if user_to_toggle.is_active else "desactivado"
    messages.success(request, f"El usuario {user_to_toggle.username} ha sido {status}.")
    return redirect('users:user_list')

def load_positions(request):
    department_id = request.GET.get('department')
    if department_id:
        positions = Position.objects.filter(department_id=department_id, is_active=True).order_by('name')
        # Si el área no tiene cargos, podemos retornar todos los activos o una lista vacía.
        if not positions.exists():
            positions = Position.objects.filter(is_active=True).order_by('name')
    else:
        positions = Position.objects.filter(is_active=True).order_by('name')
    return JsonResponse(list(positions.values('id', 'name')), safe=False)

