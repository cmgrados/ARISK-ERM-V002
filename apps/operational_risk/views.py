import json
from django.shortcuts import render, redirect, get_object_or_404
from django.core.serializers.json import DjangoJSONEncoder

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import HttpResponse, FileResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Sum
from .models import OpRiskIncident, OpRiskEventCategory, COSOComponent, COSOPrinciple, COSOAssessment, PotentialLoss, PotentialLossAudit, RiskManagementStep
from .forms import PotentialLossForm, PotentialLossAdjustmentForm, LinkLossToIncidentForm
from risks.models import Risk, RiskAssessment, ProbabilityScale, ImpactScale, RiskMatrixConfiguration
from controls.models import RiskControl
from action_plans.models import ActionPlan
from catalogs.models import RiskType, Process

def dashboard(request):
    incidents = OpRiskIncident.objects.all()
    
    # COSO III - 5 Components Maturity Calculation
    components = COSOComponent.objects.prefetch_related('principles__assessments').all()
    coso_stats = []
    
    for comp in components:
        principles = comp.principles.all()
        # Get latest assessment for each principle
        latest_scores = []
        for p in principles:
            last_eval = p.assessments.order_by('-evaluation_date').first()
            if last_eval:
                latest_scores.append(last_eval.score)
        
        avg = sum(latest_scores) / len(principles) if principles and latest_scores else 1
        coso_stats.append({
            'name': comp.name,
            'maturity_pct': (avg / 4) * 100,
            'avg_score': avg
        })

    # Summary stats
    total_events = incidents.count()
    total_loss = incidents.aggregate(Sum('gross_loss'))['gross_loss__sum'] or 0
    open_incidents = incidents.filter(status='open').count()
    
    # Heatmap summary
    op_type = RiskType.objects.filter(code='OP').first()
    op_assessments = RiskAssessment.objects.filter(risk__risk_type=op_type)
    
    critical_risks = op_assessments.filter(residual_score__gte=15).count()
    high_risks = op_assessments.filter(residual_score__range=(9, 14)).count()

    # Get Scales and Matrix Config for Dashboard Heatmap
    prob_scales = ProbabilityScale.objects.all().order_by('value')
    impact_scales = ImpactScale.objects.all().order_by('-value')
    matrix_config = RiskMatrixConfiguration.objects.all()
    config_dict = {(c.probability_id, c.impact_id): c for c in matrix_config}
    
    heatmap_grid = []
    for impact in impact_scales:
        row = []
        for prob in prob_scales:
            cell_config = config_dict.get((prob.id, impact.id))
            count = op_assessments.filter(inherent_probability=prob, inherent_impact=impact).count()
            row.append({
                'config': cell_config,
                'count': count
            })
        heatmap_grid.append(row)

    # Fetch top 5 action plans for op risks
    op_action_plans = ActionPlan.objects.filter(risk__risk_type=op_type).order_by('due_date')[:5]

    context = {
        'page_title': 'Dashboard Riesgo Operacional (COSO III)',
        'coso_stats': coso_stats,
        'total_events': total_events,
        'total_loss': total_loss,
        'open_incidents': open_incidents,
        'critical_risks': critical_risks,
        'high_risks': high_risks,
        'heatmap_grid': heatmap_grid,
        'prob_scales': prob_scales,
        'impact_scales': impact_scales,
        'incidents': incidents,
        'action_plans': op_action_plans,
    }
    return render(request, 'operational_risk/dashboard.html', context)

def op_data(request):
    incidents = OpRiskIncident.objects.all().prefetch_related('potential_losses').order_by('-discovery_date')
    context = {'page_title': 'Riesgo Operacional - Eventos e Incidentes', 'incidents': incidents}
    return render(request, 'operational_risk/op_data.html', context)

def export_op_risk_excel(request):
    import io
    import xlsxwriter
    from django.http import HttpResponse
    
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    sheet = workbook.add_worksheet("Eventos de Riesgo")
    
    # Header format
    header_fmt = workbook.add_format({'bold': True, 'bg_color': '#161065', 'font_color': 'white'})
    headers = ['ID', 'Título', 'Categoría', 'Proceso', 'Fecha Ocurrencia', 'Fecha Descubrimiento', 'Severidad', 'Estado', 'Pérdida Bruta (S/)', 'Monto Recuperado', 'Pérdida Neta']
    
    for col, header in enumerate(headers):
        sheet.write(0, col, header, header_fmt)
    
    incidents = OpRiskIncident.objects.all().select_related('category', 'process')
    for row, inc in enumerate(incidents, 1):
        sheet.write(row, 0, inc.id)
        sheet.write(row, 1, inc.title)
        sheet.write(row, 2, str(inc.category or 'N/A'))
        sheet.write(row, 3, str(inc.process or 'N/A'))
        sheet.write(row, 4, str(inc.incident_date))
        sheet.write(row, 5, str(inc.discovery_date))
        sheet.write(row, 6, inc.get_severity_display())
        sheet.write(row, 7, inc.get_status_display())
        sheet.write(row, 8, float(inc.gross_loss))
        sheet.write(row, 9, float(inc.recovery_amount))
        sheet.write(row, 10, float(inc.net_loss))
        
    workbook.close()
    output.seek(0)
    
    from django.http import HttpResponse
    response = HttpResponse(output.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="Eventos_Riesgo_Operacional.xlsx"'
    return response

def import_op_risk_excel(request):
    import pandas as pd
    from django.contrib import messages
    from django.shortcuts import redirect
    from catalogs.models import Process
    
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        try:
            df = pd.read_excel(file)
            count = 0
            
            # Severity mapping
            sev_map = {
                'Bajo': 'LOW', 'Medio': 'MEDIUM', 'Alto': 'HIGH', 'Crítico': 'CRITICAL',
                'LOW': 'LOW', 'MEDIUM': 'MEDIUM', 'HIGH': 'HIGH', 'CRITICAL': 'CRITICAL'
            }
            
            for _, row in df.iterrows():
                # Skip example row if present (optional but good)
                if row.get('Título') == 'Ej: Fraude Externo - Clonación':
                    continue
                    
                # Get category
                cat_name = row.get('Categoría', '')
                category = None
                if cat_name and not pd.isna(cat_name):
                    category, _ = OpRiskEventCategory.objects.get_or_create(name=cat_name)
                
                # Get process
                proc_name = row.get('Proceso', '')
                process = None
                if proc_name and not pd.isna(proc_name):
                    process = Process.objects.filter(name=proc_name).first()
                
                # Map severity
                raw_sev = row.get('Severidad', 'Medio')
                severity = sev_map.get(raw_sev, 'MEDIUM')
                
                # Parse dates
                def parse_date(val):
                    if pd.isna(val): return timezone.now().date()
                    try: return pd.to_datetime(val).date()
                    except: return timezone.now().date()

                OpRiskIncident.objects.create(
                    title=row.get('Título', 'Sin Título'),
                    description=row.get('Descripción', 'Importado vía Excel'),
                    incident_date=parse_date(row.get('Fecha Ocurrencia')),
                    discovery_date=parse_date(row.get('Fecha Descubrimiento')),
                    category=category,
                    process=process,
                    severity=severity,
                    gross_loss=row.get('Pérdida Bruta (S/)', 0),
                    recovery_amount=row.get('Monto Recuperado', 0),
                    status='open'
                )
                count += 1
            messages.success(request, f"Se han importado {count} eventos exitosamente.")
        except Exception as e:
            messages.error(request, f"Error al importar: {str(e)}")
            
    return redirect('operational_risk:op_data')

def download_op_risk_template(request):
    import io
    import xlsxwriter
    from django.http import HttpResponse
    
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    sheet = workbook.add_worksheet("Plantilla_Eventos")
    
    # Formats
    header_fmt = workbook.add_format({'bold': True, 'bg_color': '#1a2a6c', 'font_color': 'white', 'border': 1})
    hint_fmt = workbook.add_format({'italic': True, 'font_color': '#666666'})
    
    headers = [
        'Título', 'Descripción', 'Categoría', 'Proceso', 'Fecha Ocurrencia', 
        'Fecha Descubrimiento', 'Severidad', 'Pérdida Bruta (S/)', 'Monto Recuperado'
    ]
    
    for col, header in enumerate(headers):
        sheet.write(0, col, header, header_fmt)
        sheet.set_column(col, col, 20)
    
    # Examples / Hints
    hints = [
        'Ej: Fraude Externo - Clonación', 'Breve descripción del evento', 
        'Ej: Fraude Externo', 'Ej: Atención al Cliente', '2024-01-01', 
        '2024-01-02', 'Bajo/Medio/Alto/Crítico', '1500.00', '200.00'
    ]
    for col, hint in enumerate(hints):
        sheet.write(1, col, hint, hint_fmt)
        
    workbook.close()
    output.seek(0)
    
    from django.http import HttpResponse
    response = HttpResponse(output.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="Plantilla_Modelo_Riesgo_Operacional.xlsx"'
    return response
@require_POST
def save_event(request):
    event_id = request.POST.get('event_id')
    title = request.POST.get('title')
    gross_loss = request.POST.get('gross_loss')
    status = request.POST.get('status')
    discovery_date = request.POST.get('discovery_date')
    
    if event_id:
        incident = OpRiskIncident.objects.get(id=event_id)
        incident.title = title
        incident.gross_loss = gross_loss
        incident.status = status
        incident.discovery_date = discovery_date
        incident.save()
        messages.success(request, f'Evento "#{incident.id:05d}" actualizado correctamente.')
    else:
        incident = OpRiskIncident.objects.create(
            title=title,
            gross_loss=gross_loss,
            status=status,
            discovery_date=discovery_date,
            incident_date=discovery_date # Simplified
        )
        messages.success(request, f'Evento "#{incident.id:05d}" registrado correctamente.')
        
    return redirect('operational_risk:op_data')

@require_POST
def delete_event(request):
    event_id = request.POST.get('event_id')
    try:
        incident = OpRiskIncident.objects.get(id=event_id)
        title = incident.title
        incident.delete()
        messages.success(request, f'Evento "{title}" eliminado correctamente.')
    except OpRiskIncident.DoesNotExist:
        messages.error(request, 'El evento no existe.')
    return redirect('operational_risk:op_data')

@require_POST
def bulk_delete(request):
    selected_ids = request.POST.getlist('selected_ids')
    if selected_ids:
        count = OpRiskIncident.objects.filter(id__in=selected_ids).delete()[0]
        messages.success(request, f'Se han eliminado {count} eventos correctamente.')
    else:
        messages.warning(request, 'No se seleccionaron eventos para eliminar.')
    return redirect('operational_risk:op_data')
def coso_diagnostic(request):
    components = COSOComponent.objects.prefetch_related('principles').all()
    selected_date = request.GET.get('date', timezone.now().strftime('%Y-%m-%d'))
    
    # Get existing assessments for this date
    assessments = COSOAssessment.objects.filter(evaluation_date=selected_date)
    assessment_dict = {a.principle_id: a for a in assessments}
    
    # Calculate maturity per component
    component_stats = []
    total_score = 0
    total_principles = 0
    
    for comp in components:
        comp_principles = comp.principles.all()
        comp_scores = [assessment_dict[p.id].score for p in comp_principles if p.id in assessment_dict]
        
        avg = sum(comp_scores) / len(comp_principles) if comp_principles and comp_scores else 1
        # Map 1-4 to 0-100% (1=0%, 2=33%, 3=66%, 4=100% roughly or just keep 1-4)
        # Scale: 1: 25%, 2: 50%, 3: 75%, 4: 100%
        maturity_pct = (avg / 4) * 100
        
        component_stats.append({
            'component': comp,
            'avg_score': avg,
            'maturity_pct': maturity_pct,
            'principles_count': len(comp_principles),
            'assessed_count': len(comp_scores)
        })
        
        total_score += sum(comp_scores)
        total_principles += len(comp_principles)

    overall_maturity = (total_score / (total_principles * 4)) * 100 if total_principles else 0

    context = {
        'page_title': 'Diagnóstico de Madurez COSO III',
        'components': components,
        'component_stats': component_stats,
        'overall_maturity': overall_maturity,
        'selected_date': selected_date,
        'assessment_dict': assessment_dict,
        'score_choices': COSOAssessment.SCORE_CHOICES
    }
    return render(request, 'operational_risk/coso_diagnostic.html', context)

@require_POST
def save_coso_assessment(request):
    principle_id = request.POST.get('principle_id')
    score = request.POST.get('score')
    evidence = request.POST.get('evidence', '')
    gap_analysis = request.POST.get('gap_analysis', '')
    eval_date = request.POST.get('date', timezone.now().date())
    
    assessment, created = COSOAssessment.objects.update_or_create(
        principle_id=principle_id,
        evaluation_date=eval_date,
        defaults={
            'score': score,
            'evidence': evidence,
            'gap_analysis': gap_analysis,
            'assessed_by': request.user if request.user.is_authenticated else None
        }
    )
    
    return HttpResponse(status=204) # No content, handled by AJAX or just silent

def risk_matrix(request):
    # Filter for Operational Risks
    op_risk_type = RiskType.objects.filter(code='OP').first()
    risks = Risk.objects.filter(risk_type=op_risk_type).select_related('process')
    
    # Get Scales
    prob_scales = ProbabilityScale.objects.all().order_by('value')
    impact_scales = ImpactScale.objects.all().order_by('-value') # Descending for the Y-axis
    
    # Get Matrix Configuration
    matrix_config = RiskMatrixConfiguration.objects.all()
    config_dict = {(c.probability_id, c.impact_id): c for c in matrix_config}
    
    # Calculate counts and map risks
    matrix_data = []
    critical_count = 0
    high_count = 0
    controlled_count = 0
    
    # Grid for Heatmap
    heatmap_grid = []
    for impact in impact_scales:
        row = []
        for prob in prob_scales:
            cell_config = config_dict.get((prob.id, impact.id))
            # Count risks in this cell (Inherent)
            count = RiskAssessment.objects.filter(
                risk__risk_type=op_risk_type,
                inherent_probability=prob,
                inherent_impact=impact
            ).count()
            
            row.append({
                'prob': prob,
                'impact': impact,
                'config': cell_config,
                'count': count
            })
        heatmap_grid.append(row)

    for r in risks:
        latest_eval = r.assessments.order_by('-assessment_date').first()
        score = latest_eval.residual_score if latest_eval else 0
        
        # These counts are for Residual Risk (Controlled)
        if score >= 15:
            critical_count += 1
        elif score >= 8:
            high_count += 1
        else:
            controlled_count += 1
            
        matrix_data.append({
            'risk': r,
            'eval': latest_eval
        })
        
    context = {
        'page_title': 'Matriz de Riesgos Operacionales (RCSA)',
        'matrix_data': matrix_data,
        'heatmap_grid': heatmap_grid,
        'prob_scales': prob_scales,
        'impact_scales': impact_scales,
        'critical_count': critical_count,
        'high_count': high_count,
        'controlled_count': controlled_count,
    }
    return render(request, 'operational_risk/risk_matrix.html', context)

def potential_loss_list(request):
    losses = PotentialLoss.objects.all().order_by('-detection_date')
    context = {
        'page_title': 'Gestión de Posibles Pérdidas',
        'losses': losses,
    }
    return render(request, 'operational_risk/potential_loss_list.html', context)

def potential_loss_create(request):
    if request.method == 'POST':
        form = PotentialLossForm(request.POST, request.FILES)
        if form.is_valid():
            loss = form.save(commit=False)
            loss.created_by = request.user if request.user.is_authenticated else None
            loss.save()
            
            # Audit log
            PotentialLossAudit.objects.create(
                loss=loss,
                user=request.user if request.user.is_authenticated else None,
                action='Creado',
                new_value=f"Pérdida registrada por {loss.currency} {loss.estimated_amount}"
            )
            
            messages.success(request, f"Posible pérdida {loss.code} registrada correctamente.")
            return redirect('operational_risk:potential_loss_list')
    else:
        form = PotentialLossForm()
    
    context = {
        'page_title': 'Registrar Posible Pérdida',
        'form': form,
    }
    return render(request, 'operational_risk/potential_loss_form.html', context)

def potential_loss_detail(request, pk):
    loss = get_object_or_404(PotentialLoss, pk=pk)
    audit_log = loss.audit_log.all()
    
    if request.method == 'POST':
        # Quick link from detail
        incident_id = request.POST.get('incident_id')
        if incident_id:
            incident = get_object_or_404(OpRiskIncident, pk=incident_id)
            loss.incident = incident
            loss.status = 'linked'
            loss.linking_date = timezone.now()
            loss.save()
            
            PotentialLossAudit.objects.create(
                loss=loss,
                user=request.user if request.user.is_authenticated else None,
                action='Vinculado',
                new_value=f"Vinculado a evento #{incident.id:05d} - {incident.title}"
            )
            messages.success(request, f"Vinculado correctamente al evento #{incident.id:05d}")
            return redirect('operational_risk:potential_loss_detail', pk=pk)

    context = {
        'page_title': f'Detalle de Pérdida {loss.code}',
        'loss': loss,
        'audit_log': audit_log,
        'incidents': OpRiskIncident.objects.all().order_by('-discovery_date'),
    }
    return render(request, 'operational_risk/potential_loss_detail.html', context)

def potential_loss_edit(request, pk):
    loss = get_object_or_404(PotentialLoss, pk=pk)
    if request.method == 'POST':
        form = PotentialLossForm(request.POST, request.FILES, instance=loss)
        if form.is_valid():
            updated_loss = form.save(commit=False)
            updated_loss.updated_by = request.user if request.user.is_authenticated else None
            updated_loss.save()
            
            PotentialLossAudit.objects.create(
                loss=loss,
                user=request.user if request.user.is_authenticated else None,
                action='Editado',
                new_value=f"Pérdida editada"
            )
            
            messages.success(request, f"Posible pérdida {loss.code} editada correctamente.")
            return redirect('operational_risk:potential_loss_detail', pk=pk)
    else:
        form = PotentialLossForm(instance=loss)
    
    context = {
        'page_title': f'Editar Pérdida {loss.code}',
        'form': form,
        'loss': loss,
    }
    return render(request, 'operational_risk/potential_loss_form.html', context)

def potential_loss_delete(request, pk):
    loss = get_object_or_404(PotentialLoss, pk=pk)
    if request.method == 'POST':
        code = loss.code
        loss.delete()
        messages.success(request, f"Pérdida {code} eliminada exitosamente.")
        return redirect('operational_risk:potential_loss_list')
    # Can also render a simple confirmation template if needed, but standard is POST from a button.
    return redirect('operational_risk:potential_loss_detail', pk=pk)

def potential_loss_adjust(request, pk):
    loss = get_object_or_404(PotentialLoss, pk=pk)
    if request.method == 'POST':
        form = PotentialLossAdjustmentForm(request.POST, instance=loss)
        if form.is_valid():
            # Capture old values for audit
            old_gross = loss.gross_loss
            old_status = loss.status
            
            adjusted_loss = form.save(commit=False)
            adjusted_loss.updated_by = request.user if request.user.is_authenticated else None
            adjusted_loss.save()
            
            # Audit entries
            if old_gross != adjusted_loss.gross_loss:
                PotentialLossAudit.objects.create(
                    loss=loss,
                    user=request.user if request.user.is_authenticated else None,
                    action='Ajuste de Monto',
                    field_name='gross_loss',
                    old_value=str(old_gross),
                    new_value=str(adjusted_loss.gross_loss)
                )
            
            messages.success(request, f"Ajustes aplicados a {loss.code}")
            return redirect('operational_risk:potential_loss_detail', pk=pk)
    else:
        form = PotentialLossAdjustmentForm(instance=loss)
    
    context = {
        'page_title': f'Ajustar Pérdida {loss.code}',
        'form': form,
        'loss': loss,
    }
    return render(request, 'operational_risk/potential_loss_form.html', context)

def export_potential_losses_excel(request):
    import io
    import xlsxwriter
    
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    sheet = workbook.add_worksheet("Posibles_Pérdidas")
    
    # Headers
    headers = [
        'Código', 'Fecha Detección', 'Proceso', 'Tipo Pérdida', 'Descripción', 
        'Monto Estimado', 'Moneda', 'Estado', 'Prioridad', 'Evento Vinculado',
        'Monto Bruto Final', 'Monto Recuperado', 'Pérdida Neta'
    ]
    
    header_fmt = workbook.add_format({'bold': True, 'bg_color': '#161065', 'font_color': 'white', 'border': 1})
    num_fmt = workbook.add_format({'num_format': '#,##0.00'})
    date_fmt = workbook.add_format({'num_format': 'dd/mm/yyyy'})
    
    for col, head in enumerate(headers):
        sheet.write(0, col, head, header_fmt)
        
    losses = PotentialLoss.objects.all().select_related('process', 'incident').order_by('-detection_date')
    
    for row, loss in enumerate(losses, start=1):
        sheet.write(row, 0, loss.code)
        sheet.write(row, 1, loss.detection_date.strftime('%Y-%m-%d')) # Simplified date
        sheet.write(row, 2, loss.process.name if loss.process else 'N/A')
        sheet.write(row, 3, loss.loss_type)
        sheet.write(row, 4, (loss.description[:50] + '...') if len(loss.description) > 50 else loss.description)
        sheet.write(row, 5, float(loss.estimated_amount), num_fmt)
        sheet.write(row, 6, loss.currency)
        sheet.write(row, 7, loss.get_status_display())
        sheet.write(row, 8, loss.get_priority_display())
        sheet.write(row, 9, f"#{loss.incident.id:05d}" if loss.incident else 'Sin vincular')
        sheet.write(row, 10, float(loss.gross_loss), num_fmt)
        sheet.write(row, 11, float(loss.recovery_amount), num_fmt)
        sheet.write(row, 12, float(loss.net_loss), num_fmt)
        
    workbook.close()
    output.seek(0)
    
    from django.http import HttpResponse
    _content = output.getvalue() if hasattr(output, "getvalue") else output.read()
    response = HttpResponse(_content, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="Reporte_Posibles_Perdidas.xlsx"'
    return response

@require_POST
def import_potential_losses_excel(request):
    import pandas as pd
    from catalogs.models import Process
    from django.utils import timezone
    
    if request.FILES.get('file'):
        file = request.FILES['file']
        try:
            df = pd.read_excel(file)
            count = 0
            
            # Map priorities
            priority_map = {
                'Baja': 'low', 'Media': 'medium', 'Alta': 'high', 'Crítica': 'critical',
                'low': 'low', 'medium': 'medium', 'high': 'high', 'critical': 'critical'
            }
            
            for _, row in df.iterrows():
                # Skip example row if present
                if row.get('Tipo de Pérdida') == 'Ej: Fraude Externo - Clonación':
                    continue
                    
                # Get process
                proc_name = row.get('Proceso', '')
                process = None
                if proc_name and not pd.isna(proc_name):
                    process = Process.objects.filter(name=proc_name).first()
                
                # Parse priority
                raw_prio = row.get('Prioridad', 'Media')
                priority = priority_map.get(raw_prio, 'medium')
                
                # Parse dates
                def parse_date(val):
                    if pd.isna(val): return timezone.now().date()
                    try: return pd.to_datetime(val).date()
                    except: return timezone.now().date()

                loss = PotentialLoss.objects.create(
                    detection_date=parse_date(row.get('Fecha Detección')),
                    process=process,
                    loss_type=row.get('Tipo de Pérdida', 'Desconocido'),
                    description=row.get('Descripción', 'Importado vía Excel'),
                    estimated_amount=row.get('Monto Estimado', 0),
                    currency=row.get('Moneda', 'PEN'),
                    priority=priority,
                    status='preliminary',
                    created_by=request.user if request.user.is_authenticated else None
                )
                
                # Audit log
                PotentialLossAudit.objects.create(
                    loss=loss,
                    user=request.user if request.user.is_authenticated else None,
                    action='Importado Masivamente',
                    new_value=f"Pérdida registrada por {loss.currency} {loss.estimated_amount}"
                )
                
                count += 1
            messages.success(request, f"Se han importado {count} posibles pérdidas exitosamente.")
        except Exception as e:
            messages.error(request, f"Error al importar: {str(e)}")
            
    return redirect('operational_risk:potential_loss_list')

def download_potential_loss_template(request):
    import io
    import xlsxwriter
    from django.http import FileResponse
    
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    sheet = workbook.add_worksheet("Plantilla_Posibles_Pérdidas")
    
    headers = [
        'Fecha Detección', 'Proceso', 'Tipo de Pérdida', 'Descripción', 
        'Monto Estimado', 'Moneda', 'Prioridad'
    ]
    
    header_fmt = workbook.add_format({'bold': True, 'bg_color': '#161065', 'font_color': 'white', 'border': 1})
    for col, head in enumerate(headers):
        sheet.write(0, col, head, header_fmt)
        
    # Example row
    example_data = [
        '2024-05-10', 'Atención al Cliente', 'Ej: Fraude Externo - Clonación',
        'Se detectó una posible pérdida por clonación de tarjetas en agencia norte...',
        5000.00, 'PEN', 'Alta'
    ]
    
    for col, data in enumerate(example_data):
        sheet.write(1, col, data)
        
    # Set column widths
    sheet.set_column('A:A', 15)
    sheet.set_column('B:B', 25)
    sheet.set_column('C:C', 30)
    sheet.set_column('D:D', 40)
    sheet.set_column('E:E', 15)
    sheet.set_column('F:F', 10)
    sheet.set_column('G:G', 15)
    
    workbook.close()
    output.seek(0)
    
    from django.http import HttpResponse
    _content = output.getvalue() if hasattr(output, "getvalue") else output.read()
    response = HttpResponse(_content, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="Plantilla_Importacion_Posibles_Perdidas.xlsx"'
    return response

def risk_detail(request, pk):
    risk = get_object_or_404(Risk, pk=pk)
    controls = risk.controls.all()
    action_plans = risk.action_plans.all()
    assessments = risk.assessments.all().order_by('-assessment_date')
    latest_assessment = assessments.first()
    
    context = {
        'risk': risk,
        'controls': controls,
        'action_plans': action_plans,
        'assessments': assessments,
        'latest_assessment': latest_assessment,
        'incidents': risk.incidents.all().order_by('-incident_date'),
        'page_title': f'Gestión de Riesgo: {risk.name}',
    }
    return render(request, 'operational_risk/risk_detail.html', context)

@require_POST
def save_risk_assessment(request, pk):
    risk = get_object_or_404(Risk, pk=pk)
    
    try:
        inherent_prob = int(request.POST.get('inherent_probability', 1))
        inherent_imp = int(request.POST.get('inherent_impact', 1))
        residual_prob = int(request.POST.get('residual_probability', 1))
        residual_imp = int(request.POST.get('residual_impact', 1))
        comments = request.POST.get('comments', '')
        
        RiskAssessment.objects.create(
            risk=risk,
            inherent_probability=inherent_prob,
            inherent_impact=inherent_imp,
            residual_probability=residual_prob,
            residual_impact=residual_imp,
            comments=comments
        )
        messages.success(request, 'Nueva medición generada con éxito.')
    except Exception as e:
        messages.error(request, f'Error al generar la medición: {str(e)}')
        
    return redirect('operational_risk:risk_detail', pk=pk)

def management_cycle(request):
    """
    Sequential flow of Operational Risk Management.
    """
    # Get steps from DB or use defaults if empty
    db_steps = RiskManagementStep.objects.all().order_by('order')
    
    if not db_steps.exists() or db_steps.count() < 10:
        # Clear old steps if count doesn't match new architecture
        RiskManagementStep.objects.all().delete()
        
        # Populate new 10-step architecture
        default_steps = [
            {
                'order': 1, 
                'name': 'Estructura Organizacional', 
                'description': 'Registro de Empresas, Sedes, Gerencias y Áreas.', 
                'icon': 'fas fa-sitemap', 
                'url_name': 'catalogs:org_structure', 
                'instruction': 'Defina la jerarquía institucional. Sin una estructura clara, no es posible asignar responsabilidades ni procesos.'
            },
            {
                'order': 2, 
                'name': 'Gestión de Procesos', 
                'description': 'Mapa de Procesos, Subprocesos y Actividades.', 
                'icon': 'fas fa-project-diagram', 
                'url_name': 'catalogs:process_map', 
                'instruction': 'Registre los procesos estratégicos, misionales y de apoyo. Identifique las actividades críticas donde residen los riesgos.'
            },
            {
                'order': 3, 
                'name': 'Gestión de Riesgos', 
                'description': 'Identificación y Clasificación de Riesgos.', 
                'icon': 'fas fa-exclamation-circle', 
                'url_name': 'risks:risk_inventory', 
                'instruction': 'Identifique qué puede salir mal. Clasifique los riesgos por tipo y asócielos a sus causas y consecuencias.'
            },
            {
                'order': 4, 
                'name': 'Evaluación de Riesgos', 
                'description': 'Medición de Probabilidad e Impacto (Inherente).', 
                'icon': 'fas fa-calculator', 
                'url_name': 'risks:evaluation_dashboard', 
                'instruction': 'Evalúe la exposición al riesgo sin considerar controles. Utilice las escalas paramétricas definidas por la organización.'
            },
            {
                'order': 5, 
                'name': 'Gestión de Controles', 
                'description': 'Diseño, Ejecución y Efectividad de Controles.', 
                'icon': 'fas fa-shield-alt', 
                'url_name': 'controls:control_inventory', 
                'instruction': 'Documente los controles existentes. Evalúe su efectividad para mitigar el riesgo inherente y llegar al riesgo residual.'
            },
            {
                'order': 6, 
                'name': 'Registro de Eventos', 
                'description': 'Base de Incidentes y Pérdidas Operativas.', 
                'icon': 'fas fa-history', 
                'url_name': 'operational_risk:op_data', 
                'instruction': 'Registre los eventos materializados. Esto permite validar la efectividad de la gestión y retroalimentar la matriz.'
            },
            {
                'order': 7, 
                'name': 'Matriz Automática', 
                'description': 'Heatmap y Mapa de Calor Dinámico.', 
                'icon': 'fas fa-th', 
                'url_name': 'operational_risk:risk_matrix', 
                'instruction': 'Visualice la exposición neta de la organización. La matriz se construye automáticamente con las últimas evaluaciones.'
            },
            {
                'order': 8, 
                'name': 'Planes de Acción', 
                'description': 'Tratamiento y Mitigación de Brechas.', 
                'icon': 'fas fa-tasks', 
                'url_name': 'action_plans:plan_list', 
                'instruction': 'Defina tareas para reducir los riesgos que exceden el apetito. Asigne responsables y fechas de cumplimiento.'
            },
            {
                'order': 9, 
                'name': 'Reportes y Exportación', 
                'description': 'Generación de Informes PDF/Excel para Auditoría.', 
                'icon': 'fas fa-file-export', 
                'url_name': 'reports:dashboard', 
                'instruction': 'Genere la documentación necesaria para cumplimiento regulatorio y reportes a la alta gerencia.'
            },
            {
                'order': 10, 
                'name': 'Monitoreo y Dashboard', 
                'description': 'Indicadores KRI y Visión Ejecutiva.', 
                'icon': 'fas fa-chart-line', 
                'url_name': 'operational_risk:dashboard', 
                'instruction': 'Monitoree el perfil de riesgo en tiempo real. Utilice KPIs y KRIs para anticipar desviaciones críticas.'
            },
        ]
        for ds in default_steps:
            RiskManagementStep.objects.create(**ds)
        db_steps = RiskManagementStep.objects.all().order_by('order')

    steps = []
    from catalogs.models import Process
    from risks.models import Risk, RiskAssessment
    from action_plans.models import ActionPlan
    from .models import OpRiskIncident, COSOAssessment, PotentialLoss

    for s in db_steps:
        # Calculate status based on specific logical dependencies
        status = 'pending'
        if s.order == 1: # COSO
            if COSOAssessment.objects.exists(): status = 'completed'
        elif s.order == 2: # Processes
            if Process.objects.exists(): status = 'completed'
        elif s.order == 3: # RCSA
            if RiskAssessment.objects.filter(risk__risk_type__code='OP').exists(): status = 'completed'
        elif s.order == 4: # Events
            if OpRiskIncident.objects.exists(): status = 'completed'
        elif s.order == 5: # Potential Losses
            if PotentialLoss.objects.exists(): status = 'completed'
        elif s.order == 6: # Action Plans
            if ActionPlan.objects.filter(risk__risk_type__code='OP').exists(): status = 'completed'
        elif s.order == 7: # Follow-up
            if ActionPlan.objects.filter(risk__risk_type__code='OP', status='completed').exists(): status = 'completed'
        elif s.order == 8: # Feedback
            if RiskAssessment.objects.filter(risk__risk_type__code='OP').exists(): status = 'completed'
        
        steps.append({
            'name': s.name,
            'description': s.description,
            'icon': s.icon,
            'url_name': s.url_name,
            'instruction': s.instruction,
            'status': status,
            'order': s.order
        })
    
    context = {
        'steps': steps,
        'page_title': 'Ciclo de Gestión de Riesgo Operacional'
    }
    return render(request, 'operational_risk/management_cycle.html', context)



@login_required
def save_rcsa(request):
    if request.method == 'POST':
        risk_id = request.POST.get('risk_id')
        risk = get_object_or_404(Risk, id=risk_id)
        
        # Get scale IDs from form
        prob_id = request.POST.get('inherent_probability')
        imp_id = request.POST.get('inherent_impact')
        
        prob_scale = get_object_or_404(ProbabilityScale, id=prob_id)
        imp_scale = get_object_or_404(ImpactScale, id=imp_id)
        
        # Update or create assessment
        assessment, created = RiskAssessment.objects.get_or_create(risk=risk)
        assessment.inherent_probability = prob_scale
        assessment.inherent_impact = imp_scale
        # These fields might be deprecated or still used for quick override
        # For now, let's keep them if they exist in models.py
        assessment.comments = request.POST.get('comments', '')
        assessment.save()
        
        messages.success(request, f"Evaluación RCSA actualizada para: {risk.name}")
        return redirect('operational_risk:risk_matrix')
    return redirect('operational_risk:risk_matrix')

@login_required
def create_risk(request):
    from risks.forms import RiskForm
    from catalogs.models import RiskType, Process
    
    process_id = request.GET.get('process_id')
    initial_data = {}
    if process_id:
        initial_data['process'] = process_id
    
    # Default to OP risk type if available
    op_type = RiskType.objects.filter(code='OP').first()
    if op_type:
        initial_data['risk_type'] = op_type.id

    if request.method == 'POST':
        form = RiskForm(request.POST)
        if form.is_valid():
            risk = form.save()
            messages.success(request, f"Riesgo '{risk.name}' creado exitosamente.")
            if risk.process:
                return redirect('catalogs:process_detail', pk=risk.process.id)
            return redirect('operational_risk:risk_matrix')
    else:
        form = RiskForm(initial=initial_data)
    
    return render(request, 'catalogs/form_generic.html', {
        'form': form, 
        'title': 'Identificar Nuevo Riesgo',
        'subtitle': 'Vincule el riesgo a un proceso para habilitar su evaluación RCSA.'
    })

def download_rcsa_template(request):
    import io
    import xlsxwriter
    from django.http import HttpResponse
    
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    sheet = workbook.add_worksheet("RCSA_Template")
    
    # Formats
    header_fmt = workbook.add_format({'bold': True, 'bg_color': '#10b981', 'font_color': 'white', 'border': 1})
    hint_fmt = workbook.add_format({'italic': True, 'font_color': '#666666'})
    
    headers = [
        'Nombre del Proceso', 'Nombre del Riesgo', 'Descripción del Riesgo', 
        'Probabilidad (1-5)', 'Impacto (1-5)', 'Diseño Control (%)', 
        'Ejecución Control (%)', 'Comentarios'
    ]
    
    for col, header in enumerate(headers):
        sheet.write(0, col, header, header_fmt)
        sheet.set_column(col, col, 25)
    
    # Example Row
    example = [
        'Gestión Contable', 'Error en Registro de Gastos', 'Omisión involuntaria de facturas.',
        '4', '3', '80', '70', 'Revisión mensual pendiente.'
    ]
    for col, value in enumerate(example):
        sheet.write(1, col, value, hint_fmt)
        
    workbook.close()
    output.seek(0)
    
    response = HttpResponse(output.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="Plantilla_RCSA_A_RISK.xlsx"'
    return response

@login_required
def import_rcsa_excel(request):
    from risks.models import Risk, RiskAssessment
    from catalogs.models import Process, RiskType
    import pandas as pd
    
    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES.get('excel_file')
        try:
            df = pd.read_excel(excel_file)
            count = 0
            op_type = RiskType.objects.filter(code='OP').first()
            if not op_type:
                op_type = RiskType.objects.create(code='OP', name='Riesgo Operacional')
            
            for _, row in df.iterrows():
                proc_name = str(row.get('Nombre del Proceso', '')).strip()
                risk_name = str(row.get('Nombre del Riesgo', '')).strip()
                
                if not proc_name or not risk_name or proc_name == 'nan' or risk_name == 'nan':
                    continue
                
                # 1. Get or Create Process
                process, _ = Process.objects.get_or_create(name=proc_name)
                
                # 2. Get or Create Risk
                risk, _ = Risk.objects.get_or_create(
                    name=risk_name,
                    process=process,
                    defaults={
                        'risk_type': op_type,
                        'description': str(row.get('Descripción del Riesgo', ''))
                    }
                )
                
                # 3. Create/Update Assessment
                assessment, _ = RiskAssessment.objects.get_or_create(risk=risk)
                
                # Map numeric values to scales
                prob_val = int(row.get('Probabilidad (1-5)', 1))
                imp_val = int(row.get('Impacto (1-5)', 1))
                
                assessment.inherent_probability = ProbabilityScale.objects.filter(value=prob_val).first() or ProbabilityScale.objects.first()
                assessment.inherent_impact = ImpactScale.objects.filter(value=imp_val).first() or ImpactScale.objects.first()
                
                assessment.comments = str(row.get('Comentarios', ''))
                assessment.save()
                count += 1
                
            messages.success(request, f"Se han procesado {count} evaluaciones RCSA exitosamente.")
        except Exception as e:
            messages.error(request, f"Error al procesar el archivo: {str(e)}")
            
    return redirect('operational_risk:risk_matrix')
def executive_report(request):
    """
    Step 8: Final Executive Report consolidating all steps of the Operational Risk cycle.
    Includes Snapshot saving and historical trend analysis.
    """
    from .models import COSOAssessment, OpRiskIncident, PotentialLoss, RiskCycleSnapshot
    from risks.models import RiskAssessment
    from action_plans.models import ActionPlan
    from django.db.models import Sum, Avg
    
    # 1. Maturity Stats
    total_coso = COSOAssessment.objects.count()
    avg_coso = COSOAssessment.objects.aggregate(Avg('score'))['score__avg'] or 1
    maturity_pct = (avg_coso / 4) * 100
    
    # 2. Risk Matrix Stats
    op_assessments = RiskAssessment.objects.filter(risk__risk_type__code='OP')
    avg_residual = op_assessments.aggregate(Avg('residual_score'))['residual_score__avg'] or 0
    high_risks = op_assessments.filter(residual_score__gte=15).count()
    
    # 3. Incident & Loss Stats
    total_incidents = OpRiskIncident.objects.count()
    total_gross_loss = OpRiskIncident.objects.aggregate(Sum('gross_loss'))['gross_loss__sum'] or 0
    potential_loss_sum = PotentialLoss.objects.aggregate(Sum('estimated_amount'))['estimated_amount__sum'] or 0
    
    # 4. Action Plan Stats
    total_plans = ActionPlan.objects.filter(risk__risk_type__code='OP').count()
    completed_plans = ActionPlan.objects.filter(risk__risk_type__code='OP', status='completed').count()
    plan_compliance = (completed_plans / total_plans * 100) if total_plans > 0 else 0
    
    # Handle Snapshot Saving
    if request.method == 'POST' and 'save_snapshot' in request.POST:
        cycle_name = request.POST.get('cycle_name', f"Ciclo {timezone.now().strftime('%B %Y')}")
        comments = request.POST.get('comments', '')
        
        RiskCycleSnapshot.objects.create(
            cycle_name=cycle_name,
            maturity_pct=maturity_pct,
            avg_residual_score=avg_residual,
            high_risks_count=high_risks,
            total_gross_loss=total_gross_loss,
            plan_compliance_pct=plan_compliance,
            comments=comments
        )
        messages.success(request, f'Snapshot "{cycle_name}" guardado exitosamente para el histórico.')
        return redirect('operational_risk:executive_report')

    # 5. Alerts System
    alerts = []
    overdue_plans = ActionPlan.objects.filter(risk__risk_type__code='OP', status='overdue')
    for p in overdue_plans:
        alerts.append({'type': 'danger', 'msg': f'ACCIÓN VENCIDA: {p.title}', 'ref': p.due_date})
    
    critical_incidents = OpRiskIncident.objects.filter(severity='CRITICAL', status='open')
    for i in critical_incidents:
        alerts.append({'type': 'warning', 'msg': f'INCIDENTE CRÍTICO ABIERTO: {i.title}', 'ref': i.discovery_date})

    # 6. Historical Data
    snapshots = RiskCycleSnapshot.objects.all().order_by('snapshot_date')
    
    # 7. AI Agent Insights
    from .ai_agent import OperationalRiskAIAgent
    ai_agent = OperationalRiskAIAgent()
    ai_insights = ai_agent.generate_executive_summary()
    
    context = {
        'page_title': 'Informe Ejecutivo Final de Riesgo Operacional',
        'maturity_pct': maturity_pct,
        'avg_residual': avg_residual,
        'high_risks_count': high_risks,
        'total_incidents': total_incidents,
        'total_gross_loss': total_gross_loss,
        'potential_loss_sum': potential_loss_sum,
        'plan_compliance': plan_compliance,
        'total_plans': total_plans,
        'completed_plans': completed_plans,
        'alerts': alerts[:5],
        'snapshots': snapshots,
        'ai_narrative': ai_insights['narrative'],
        'ai_recommendations': ai_insights['all_insights'],
    }
    return render(request, 'operational_risk/executive_report.html', context)

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def op_risk_ai_chat(request):
    if request.method == 'POST':
        import json
        try:
            data = json.loads(request.body)
            query = data.get('query', '')
            
            from .ai_agent import OperationalRiskAIAgent
            agent = OperationalRiskAIAgent()
            response = agent.chat(query)
            
            return JsonResponse({'response': response})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request'}, status=400)

def delete_risk(request, pk):
    risk = get_object_or_404(Risk, pk=pk)
    if request.method == 'POST':
        name = risk.name
        risk.delete()
        messages.success(request, f'Riesgo "{name}" eliminado correctamente.')
        return redirect('operational_risk:risk_matrix')
    
    context = {
        'page_title': 'Eliminar Riesgo Operacional',
        'item': risk,
        'cancel_url': 'operational_risk:risk_matrix'
    }
    return render(request, 'generic_confirm_delete.html', context)
