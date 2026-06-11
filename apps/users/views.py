from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Role, User, AuditLog
from django.contrib import messages
import json

@login_required
def role_list(request):
    if not request.user.is_superuser:
        return redirect('/')
    roles = Role.objects.all()
    return render(request, 'users/role_list.html', {'roles': roles})

@login_required
def role_create(request):
    if not request.user.is_superuser:
        return redirect('/')
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Role.objects.create(name=name)
            return redirect('users:role_list')
    return render(request, 'users/role_form.html')

@login_required
def role_update(request, pk):
    if not request.user.is_superuser:
        return redirect('/')
    role = get_object_or_404(Role, pk=pk)
    
    modules = [
        {'id': 'integral_risk', 'name': 'Gestión Integral de Riesgos'},
        {'id': 'financial_planning', 'name': 'Planeamiento Financiero'},
        {'id': 'strategic_planning', 'name': 'Planeamiento Estratégico'},
        {'id': 'credit_risk', 'name': 'Riesgo Crédito'},
        {'id': 'liquidity_risk', 'name': 'Riesgo Liquidez'},
        {'id': 'market_risk', 'name': 'Riesgo de Mercado'},
        {'id': 'operational_risk', 'name': 'Riesgo Operacional'},
        {'id': 'compliance_risk', 'name': 'Riesgo de Cumplimiento'},
        {'id': 'plaft_risk', 'name': 'Riesgo PLAFT'},
    ]
    
    if request.method == 'POST':
        permissions = {}
        for mod in modules:
            acceder = request.POST.get(f'acceder_{mod["id"]}') == 'on'
            crear = request.POST.get(f'crear_{mod["id"]}') == 'on'
            editar = request.POST.get(f'editar_{mod["id"]}') == 'on'
            eliminar = request.POST.get(f'eliminar_{mod["id"]}') == 'on'
            ver_todo = request.POST.get(f'ver_todo_{mod["id"]}') == 'on'
            exportar = request.POST.get(f'exportar_{mod["id"]}') == 'on'
            
            permissions[mod['id']] = {
                'acceder': acceder,
                'crear': crear,
                'editar': editar,
                'eliminar': eliminar,
                'ver_todo': ver_todo,
                'exportar': exportar,
            }
        role.permissions = permissions
        role.save()
        return redirect('users:role_list')
        
    return render(request, 'users/role_permissions.html', {'role': role, 'modules': modules})

@login_required
def user_list(request):
    if not request.user.is_superuser:
        return redirect('/')
    users = User.objects.all().order_by('username')
    return render(request, 'users/user_list.html', {'users': users})

@login_required
def user_create(request):
    if not request.user.is_superuser:
        return redirect('/')
    roles = Role.objects.all()
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        role_id = request.POST.get('role_id')
        
        confirm_password = request.POST.get('confirm_password')
        
        if not username or not password:
            messages.error(request, 'El nombre de usuario y la contraseña son obligatorios.')
        elif password != confirm_password:
            messages.error(request, 'Las contraseñas no coinciden.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'El nombre de usuario ya existe.')
        else:
            try:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=password
                )
                user.is_staff = True
                if role_id:
                    user.role_id = role_id
                
                try:
                    user.hidden_modules = json.loads(request.POST.get('hidden_modules', '[]'))
                except:
                    pass
                
                user.save()
                messages.success(request, 'Usuario creado con éxito')
                return redirect('users:user_list')
            except Exception as e:
                messages.error(request, f'Error al crear el usuario: {str(e)}')
            
    return render(request, 'users/user_form.html', {'roles': roles, 'action': 'create'})

@login_required
def user_update(request, pk):
    if not request.user.is_superuser:
        return redirect('/')
    user = get_object_or_404(User, pk=pk)
    roles = Role.objects.all()
    
    if request.method == 'POST':
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        role_id = request.POST.get('role_id')
        is_active = request.POST.get('is_active') == 'on'
        
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if password and password != confirm_password:
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(request, 'users/user_form.html', {'roles': roles, 'action': 'update', 'current_user': user})
            
        if password:
            user.set_password(password)
            
        user.is_staff = True
            
        if role_id:
            user.role_id = role_id
        else:
            user.role = None
            
        try:
            user.hidden_modules = json.loads(request.POST.get('hidden_modules', '[]'))
        except:
            pass
            
        user.is_active = is_active
        user.save()
        
        if password:
            messages.success(request, 'Contraseña guardada con éxito')
        else:
            messages.success(request, 'Guardado con éxito')
            
        return redirect('users:user_list')
        
    return render(request, 'users/user_form.html', {'roles': roles, 'action': 'update', 'current_user': user})

@login_required
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'Usuario eliminado correctamente.')
        return redirect('users:user_list')
    return render(request, 'users/user_confirm_delete.html', {'user_instance': user})

@login_required
def audit_log(request):
    logs = AuditLog.objects.select_related('user').all()
    return render(request, 'users/audit_log.html', {'logs': logs})
