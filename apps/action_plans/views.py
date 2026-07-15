from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ActionPlan, ActionFollowUp
from .forms import ActionPlanForm # I'll create this

def action_plan_list(request):
    plans = ActionPlan.objects.all().order_by('-due_date')
    context = {
        'page_title': 'Planes de Acción y Mitigación',
        'plans': plans
    }
    return render(request, 'action_plans/plan_list.html', context)

def action_plan_detail(request, pk):
    plan = get_object_or_404(ActionPlan, pk=pk)
    
    if request.method == 'POST':
        comment = request.POST.get('comment')
        progress = request.POST.get('progress')
        evidence = request.FILES.get('evidence')
        
        if comment:
            # Create follow-up
            ActionFollowUp.objects.create(
                action_plan=plan,
                comment=comment,
                evidence=evidence,
                performed_by=request.user if request.user.is_authenticated else None
            )
            
            # Update plan progress
            if progress:
                plan.progress = int(progress)
                if plan.progress >= 100:
                    plan.status = 'completed'
                elif plan.progress > 0 and plan.status == 'pending':
                    plan.status = 'in_progress'
                plan.save()
                
            messages.success(request, 'Seguimiento registrado exitosamente.')
            return redirect('action_plans:plan_detail', pk=pk)

    follow_ups = plan.follow_ups.all().order_by('-follow_up_date')
    context = {
        'page_title': f'Detalle del Plan: {plan.title}',
        'plan': plan,
        'follow_ups': follow_ups
    }
    return render(request, 'action_plans/plan_detail.html', context)

def create_action_plan(request):
    if request.method == 'POST':
        form = ActionPlanForm(request.POST)
        if form.is_valid():
            plan = form.save(commit=False)
            if request.user.is_authenticated:
                # You might want to assign a creator if the model has one
                pass
            plan.save()
            messages.success(request, 'Plan de acción creado exitosamente.')
            return redirect('action_plans:plan_list')
    else:
        form = ActionPlanForm()
    
    context = {
        'page_title': 'Nuevo Plan de Acción',
        'form': form
    }
    return render(request, 'action_plans/plan_form.html', context)

def edit_action_plan(request, pk):
    plan = get_object_or_404(ActionPlan, pk=pk)
    if request.method == 'POST':
        form = ActionPlanForm(request.POST, instance=plan)
        if form.is_valid():
            form.save()
            messages.success(request, 'Plan de acción actualizado exitosamente.')
            return redirect('action_plans:plan_list')
    else:
        form = ActionPlanForm(instance=plan)
        
    context = {
        'page_title': f'Editar Plan: {plan.title}',
        'form': form
    }
    return render(request, 'action_plans/plan_form.html', context)

def delete_action_plan(request, pk):
    plan = get_object_or_404(ActionPlan, pk=pk)
    if request.method == 'POST':
        plan.delete()
        messages.success(request, 'Plan de acción eliminado correctamente.')
        return redirect('action_plans:plan_list')
    
    context = {
        'page_title': 'Eliminar Plan de Acción',
        'item': plan,
        'cancel_url': 'action_plans:plan_list'
    }
    return render(request, 'generic_confirm_delete.html', context)
