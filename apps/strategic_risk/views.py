from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from functools import wraps
from django.contrib import messages
from django.http import JsonResponse
import json
from .models import StrategicPlan, ExternalEnvironment, FinancialEnvironment, InternalDiagnosis, StrategicPerspective, StrategicObjective, KPI, StrategicMatrix, BusinessModelCanvas, CorporatePhilosophy
from .forms import StrategicPlanForm, ExternalEnvironmentForm, FinancialEnvironmentForm, InternalDiagnosisForm

def check_module_access(module_name):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_superuser:
                if module_name in getattr(request.user, 'hidden_modules', []):
                    return render(request, 'access_denied.html', {'module_name': module_name})
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

@login_required
@check_module_access('Estrategia y Objetivos')
def dashboard(request):
    planes = StrategicPlan.objects.all().order_by('-start_year')
    context = {
        'page_title': 'Planeamiento Estratégico - Dashboard',
        'planes': planes
    }
    return render(request, 'strategic_risk/dashboard.html', context)

@login_required
@check_module_access('Estrategia y Objetivos')
def plan_create(request):
    if request.method == 'POST':
        form = StrategicPlanForm(request.POST)
        if form.is_valid():
            plan = form.save(commit=False)
            plan.created_by = request.user
            plan.save()
            # Crear registros vacíos por defecto para entornos y diagnóstico
            ExternalEnvironment.objects.create(plan=plan)
            FinancialEnvironment.objects.create(plan=plan)
            InternalDiagnosis.objects.create(plan=plan)
            # Crear matrices vacías por defecto
            StrategicMatrix.objects.create(plan=plan, matrix_type='FODA')
            StrategicMatrix.objects.create(plan=plan, matrix_type='EFI')
            StrategicMatrix.objects.create(plan=plan, matrix_type='EFE')
            StrategicMatrix.objects.create(plan=plan, matrix_type='MPC')
            BusinessModelCanvas.objects.create(plan=plan)
            CorporatePhilosophy.objects.create(plan=plan)
            # Crear perspectivas por defecto
            for i, name in enumerate(['Financiera', 'Clientes', 'Procesos Internos', 'Aprendizaje y Crecimiento']):
                StrategicPerspective.objects.create(plan=plan, name=name, order=i)
            request.session['active_strategic_plan_id'] = plan.id
            messages.success(request, 'Plan Estratégico creado exitosamente.')
            return redirect('strategic_risk:dashboard')
    else:
        form = StrategicPlanForm()
    
    context = {
        'page_title': 'Crear Plan Estratégico',
        'form': form
    }
    return render(request, 'strategic_risk/plan_form.html', context)

@login_required
@check_module_access('Estrategia y Objetivos')
def plan_update(request, pk):
    plan = get_object_or_404(StrategicPlan, pk=pk)
    if request.method == 'POST':
        form = StrategicPlanForm(request.POST, instance=plan)
        if form.is_valid():
            form.save()
            messages.success(request, 'Plan Estratégico actualizado exitosamente.')
            return redirect('strategic_risk:dashboard')
    else:
        form = StrategicPlanForm(instance=plan)
    
    context = {'page_title': 'Editar Plan Estratégico', 'form': form, 'plan': plan}
    return render(request, 'strategic_risk/plan_form.html', context)

@login_required
def set_active_plan(request, pk):
    plan = get_object_or_404(StrategicPlan, pk=pk)
    request.session['active_strategic_plan_id'] = plan.id
    return redirect('strategic_risk:strat_data')

@login_required
@check_module_access('Estrategia y Objetivos')
def strat_data(request):
    plan_id = request.session.get('active_strategic_plan_id')
    if plan_id:
        plan = StrategicPlan.objects.filter(id=plan_id).first()
    else:
        plan = StrategicPlan.objects.order_by('-start_year').first()
        
    active_tab = 'externo'
    
    if plan:
        ext_env = getattr(plan, 'external_environment', None)
        fin_env = getattr(plan, 'financial_environment', None)
        int_diag = getattr(plan, 'internal_diagnosis', None)

        if request.method == 'POST':
            if 'save_external' in request.POST:
                ext_form = ExternalEnvironmentForm(request.POST, instance=ext_env)
                if ext_form.is_valid():
                    ext_form.save()
                    messages.success(request, 'Entorno Externo actualizado correctamente.')
                active_tab = 'externo'
            elif 'save_financial' in request.POST:
                fin_form = FinancialEnvironmentForm(request.POST, instance=fin_env)
                if fin_form.is_valid():
                    fin_form.save()
                    messages.success(request, 'Entorno Financiero actualizado correctamente.')
                active_tab = 'financiero'
            elif 'save_internal' in request.POST:
                int_form = InternalDiagnosisForm(request.POST, instance=int_diag)
                if int_form.is_valid():
                    int_form.save()
                    messages.success(request, 'Diagnóstico Interno actualizado correctamente.')
                active_tab = 'interno'

        ext_form = ExternalEnvironmentForm(instance=ext_env)
        fin_form = FinancialEnvironmentForm(instance=fin_env)
        int_form = InternalDiagnosisForm(instance=int_diag)
    else:
        ext_form = fin_form = int_form = None

    context = {
        'page_title': 'Planificación Estratégica - Diagnóstico y Entorno',
        'plan': plan,
        'ext_form': ext_form,
        'fin_form': fin_form,
        'int_form': int_form,
        'active_tab': active_tab
    }
    return render(request, 'strategic_risk/strat_data.html', context)

@login_required
@check_module_access('Estrategia y Objetivos')
def methodologies(request):
    plan_id = request.session.get('active_strategic_plan_id')
    if plan_id:
        plan = StrategicPlan.objects.filter(id=plan_id).first()
    else:
        plan = StrategicPlan.objects.order_by('-start_year').first()
        
    if not plan:
        messages.warning(request, "Debe seleccionar o crear un plan estratégico primero.")
        return redirect('strategic_risk:dashboard')

    foda = StrategicMatrix.objects.filter(plan=plan, matrix_type='FODA').first()
    efi = StrategicMatrix.objects.filter(plan=plan, matrix_type='EFI').first()
    efe = StrategicMatrix.objects.filter(plan=plan, matrix_type='EFE').first()
    mpc = StrategicMatrix.objects.filter(plan=plan, matrix_type='MPC').first()
    canvas_actual = BusinessModelCanvas.objects.filter(plan=plan, version__in=['1.0', 'Actual']).first()
    if canvas_actual and canvas_actual.version == '1.0':
        canvas_actual.version = 'Actual'
        canvas_actual.save()
        
    if not canvas_actual or (not canvas_actual.key_partners and not canvas_actual.customer_segments):
        if not canvas_actual:
            canvas_actual = BusinessModelCanvas(plan=plan, version='Actual')
        
        canvas_actual.key_partners = "AFILIACIÓN SBS\nALIANZAS ESTRATÉGICAS CON REPRESENTANTES DE RED DE SALUD, UGEL Y MUNICIPALIDADES\nSENTINEL, EQUIFAX"
        canvas_actual.key_activities = "PROMOCIÓN DE PRODUCTOS ACTIVOS Y PASIVOS\nGENERACIÓN DE CONVENIOS DE DTO.\nSEGUIMIENTO Y GESTIÓN DE CARTERA\nEVALUACIÓN DE CARTERA"
        canvas_actual.key_resources = "PERSONAL CAPACITADO\nINFRAESTRUCTURA, HERRAMIENTAS Y EQUIPOS EN RED DE AGENCIAS"
        canvas_actual.value_proposition = "PRODUCTOS ACTIVOS\n- CONVENIOS\n- CRÉDITO PERSONAL\n\nPRODUCTOS PASIVOS\n- APORTES\n- AHORROS CORRIENTES\n- DEPÓSITOS A PLAZO FIJO\n\nPRODUCTOS Y SERVICIO NO FINANCIERO\n- GIROS\n- PREVISIÓN SOCIAL"
        canvas_actual.customer_relationships = "REDES SOCIALES\nPUBLICIDAD ESCRITA\nPUBLICIDAD RADIAL\nGIGANTOGRAFÍAS"
        canvas_actual.channels = "RED DE OFICINAS INFORMATIVAS LIMA, TARAPOTO, AREQUIPA, IQUITOS\nASESORES DE CRÉDITOS\nASESORES DE COBRANZAS"
        canvas_actual.customer_segments = "PERSONAS NATURALES ( 18 - 65 AÑOS)\nMILITARES O CASTRENCES\nSECTOR PÚBLICO (RED SALUD, UGEL, MUNICIPALIDADES, ETC.)\nAGROPECUARIO"
        canvas_actual.cost_structure = "GASTOS ADMINISTRATIVOS Y DE GESTIÓN\nALQUILERES DE AGENCIAS, SERVICIOS, CORE FINANCIERO, ETC.\nOBLIGACIONES POR AHORROS Y DEPÓSITOS\nOBLIGACIONES CON ENTIDADES FINANCIERAS\nTRIBUTOS\nPROVISIONES POR CRÉDITOS\nCOMISIONES\nCUOTA DE SUPERVISIÓN SBS"
        canvas_actual.revenue_streams = "INGRESO POR INTERESES POR CARTERA CRÉDITOS POR CONVENIO (80%)\nINGRESO POR OTROS PRODUCTOS O SERVICIOS (20%)\nINGRESO POR COMISIONES (DERECHO DE DESEMBOLSO, INSCRIPCIÓN POR GIROS)\nMORAS\nOTROS INGRESOS POR VENTAS DE PRODUCTOS PRENDADOS"
        canvas_actual.save()
        
    canvas_futuro = BusinessModelCanvas.objects.filter(plan=plan, version='Futuro').first()
    if not canvas_futuro:
        canvas_futuro = BusinessModelCanvas(plan=plan, version='Futuro')
        canvas_futuro.save()
        
    philosophy, _ = CorporatePhilosophy.objects.get_or_create(plan=plan)
    
    context = {
        'page_title': 'Planificación Estratégica - Matrices Estratégicas',
        'plan': plan,
        'foda_data': json.dumps(foda.data) if foda and foda.data else '{}',
        'efi_data': json.dumps(efi.data) if efi and efi.data else '[]',
        'efe_data': json.dumps(efe.data) if efe and efe.data else '[]',
        'mpc_data': json.dumps(mpc.data) if mpc and mpc.data else '{}',
        'canvas_actual': canvas_actual,
        'canvas_futuro': canvas_futuro,
        'philosophy': philosophy
    }
    return render(request, 'strategic_risk/methodologies.html', context)

@login_required
def save_matrix(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            plan_id = data.get('plan_id')
            matrix_type = data.get('matrix_type')
            matrix_data = data.get('data')
            
            plan = get_object_or_404(StrategicPlan, id=plan_id)
            matrix, created = StrategicMatrix.objects.get_or_create(plan=plan, matrix_type=matrix_type)
            matrix.data = matrix_data
            matrix.save()
            
            return JsonResponse({'status': 'success', 'message': f'Matriz {matrix_type} guardada correctamente.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

@login_required
def save_canvas(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            plan_id = data.get('plan_id')
            version = data.get('version', 'Actual')
            
            plan = get_object_or_404(StrategicPlan, id=plan_id)
            canvas, created = BusinessModelCanvas.objects.get_or_create(plan=plan, version=version)
            
            canvas.key_partners = data.get('key_partners', '')
            canvas.key_activities = data.get('key_activities', '')
            canvas.key_resources = data.get('key_resources', '')
            canvas.value_proposition = data.get('value_proposition', '')
            canvas.customer_relationships = data.get('customer_relationships', '')
            canvas.channels = data.get('channels', '')
            canvas.customer_segments = data.get('customer_segments', '')
            canvas.cost_structure = data.get('cost_structure', '')
            canvas.revenue_streams = data.get('revenue_streams', '')
            canvas.save()
            
            return JsonResponse({'status': 'success', 'message': f'Business Model Canvas ({version}) guardado correctamente.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

@login_required
def save_mpc(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            plan_id = data.get('plan_id')
            matrix_data = data.get('data')
            
            plan = get_object_or_404(StrategicPlan, id=plan_id)
            matrix, created = StrategicMatrix.objects.get_or_create(plan=plan, matrix_type='MPC')
            matrix.data = matrix_data
            matrix.save()
            
            return JsonResponse({'status': 'success', 'message': 'Matriz Perfil Competitivo (MPC) guardada correctamente.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

@login_required
def save_metas_planeadas(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            plan_id = data.get('plan_id')
            metas_data = data.get('data')
            
            plan = get_object_or_404(StrategicPlan, id=plan_id)
            matrix, created = StrategicMatrix.objects.get_or_create(plan=plan, matrix_type='METAS')
            matrix.data = metas_data
            matrix.save()
            
            return JsonResponse({'status': 'success', 'message': 'Metas Planeadas guardadas correctamente.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

@login_required
def save_philosophy(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            plan_id = request.session.get('active_strategic_plan_id')
            if not plan_id:
                plan_id = StrategicPlan.objects.order_by('-start_year').first().id
                
            plan = get_object_or_404(StrategicPlan, id=plan_id)
            philosophy, _ = CorporatePhilosophy.objects.get_or_create(plan=plan)
            
            field_type = data.get('type')
            text = data.get('text', '')
            
            if field_type == 'mision':
                philosophy.mission = text
                msg = 'Misión guardada correctamente.'
            elif field_type == 'vision':
                philosophy.vision = text
                msg = 'Visión guardada correctamente.'
            elif field_type == 'valores':
                philosophy.values = text
                msg = 'Valores guardados correctamente.'
            else:
                return JsonResponse({'status': 'error', 'message': 'Tipo inválido.'})
                
            philosophy.save()
            return JsonResponse({'status': 'success', 'message': msg})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

@login_required
@check_module_access('Estrategia y Objetivos')
def controls(request):
    plan_id = request.session.get('active_strategic_plan_id')
    if plan_id:
        plan = StrategicPlan.objects.filter(id=plan_id).first()
    else:
        plan = StrategicPlan.objects.order_by('-start_year').first()
        
    perspectives = StrategicPerspective.objects.filter(plan=plan).prefetch_related('objectives__kpis') if plan else []
    metas_matrix = StrategicMatrix.objects.filter(plan=plan, matrix_type='METAS').first() if plan else None
    
    context = {
        'page_title': 'Planificación Estratégica - Balanced Scorecard',
        'plan': plan,
        'perspectives': perspectives,
        'metas_data': metas_matrix.data if metas_matrix and metas_matrix.data else []
    }
    return render(request, 'strategic_risk/controls.html', context)

@login_required
def add_objective(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            perspective_id = data.get('perspective_id')
            name = data.get('name')
            description = data.get('description', '')
            
            perspective = get_object_or_404(StrategicPerspective, id=perspective_id)
            StrategicObjective.objects.create(perspective=perspective, name=name, description=description)
            
            return JsonResponse({'status': 'success', 'message': 'Objetivo añadido correctamente.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

@login_required
def add_kpi(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            objective_id = data.get('objective_id')
            name = data.get('name')
            target = data.get('target', 0)
            frequency = data.get('frequency', 'Mensual')
            
            objective = get_object_or_404(StrategicObjective, id=objective_id)
            KPI.objects.create(
                objective=objective, 
                name=name, 
                target=target, 
                frequency=frequency
            )
            
            return JsonResponse({'status': 'success', 'message': 'KPI añadido correctamente.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

@login_required
@check_module_access('Estrategia y Objetivos')
def reports(request):
    plan_id = request.session.get('active_strategic_plan_id')
    if plan_id:
        plan = StrategicPlan.objects.filter(id=plan_id).first()
    else:
        plan = StrategicPlan.objects.order_by('-start_year').first()
    
    context = {
        'page_title': 'Planificación Estratégica - Reporte Final',
        'plan': plan
    }
    
    if plan:
        context['ext_env'] = getattr(plan, 'external_environment', None)
        context['fin_env'] = getattr(plan, 'financial_environment', None)
        context['int_diag'] = getattr(plan, 'internal_diagnosis', None)
        context['canvas'] = plan.canvas.filter(version='Futuro').first() or plan.canvas.filter(version='Actual').first()
        
        foda = plan.matrices.filter(matrix_type='FODA').first()
        if foda and foda.data:
            normalized_foda = {}
            for q in ['fortalezas', 'debilidades', 'oportunidades', 'amenazas']:
                val = foda.data.get(q, [])
                if isinstance(val, str):
                    normalized_foda[q] = [{'text': v.lstrip('0123456789. ').strip(), 'weight': 5} for v in val.split('\n') if v.strip()]
                else:
                    normalized_foda[q] = val
            
            # Calculate metrics for the combined view
            # Internal
            total_internal_weight = sum(int(item.get('weight', 0)) for item in normalized_foda.get('fortalezas', []) + normalized_foda.get('debilidades', []))
            for item in normalized_foda.get('fortalezas', []):
                w = int(item.get('weight', 0))
                item['pct'] = round((w / total_internal_weight * 100) if total_internal_weight else 0, 1)
                item['rating_label'] = 'MF' if w >= 8 else ('F' if w >= 5 else 'M')
                item['rating_val'] = 4 if w >= 8 else (3 if w >= 5 else 2)
                item['score'] = round((item['pct'] / 100) * item['rating_val'], 2)
                
            mefi_total = 0
            for item in normalized_foda.get('debilidades', []):
                w = int(item.get('weight', 0))
                item['pct'] = round((w / total_internal_weight * 100) if total_internal_weight else 0, 1)
                item['rating_label'] = 'MD' if w >= 8 else ('D' if w >= 5 else 'M')
                item['rating_val'] = 1 if w >= 8 else (2 if w >= 5 else 3)
                item['score'] = round((item['pct'] / 100) * item['rating_val'], 2)
                mefi_total += item['score']

            for item in normalized_foda.get('fortalezas', []):
                mefi_total += item['score']

            normalized_foda['mefi_total'] = round(mefi_total, 2)
            if normalized_foda['mefi_total'] >= 2.5:
                normalized_foda['mefi_analisis'] = f"El puntaje total ponderado de la matriz MEFI es de {normalized_foda['mefi_total']}. Este resultado, al ser mayor que el promedio de 2.5, indica que la organización posee una posición interna fuerte. En general, las fortalezas superan a las debilidades, lo que sugiere que la entidad está capitalizando sus recursos y ventajas internas de forma adecuada."
            else:
                normalized_foda['mefi_analisis'] = f"El puntaje total ponderado de la matriz MEFI es de {normalized_foda['mefi_total']}. Este resultado, al ser menor al promedio de 2.5, revela una posición interna débil. Las debilidades organizacionales están afectando el desempeño general, requiriendo acciones correctivas inmediatas para mejorar las capacidades operativas y estratégicas."

            # External
            total_external_weight = sum(int(item.get('weight', 0)) for item in normalized_foda.get('oportunidades', []) + normalized_foda.get('amenazas', []))
            for item in normalized_foda.get('oportunidades', []):
                w = int(item.get('weight', 0))
                item['pct'] = round((w / total_external_weight * 100) if total_external_weight else 0, 1)
                item['rating_label'] = 'MF' if w >= 8 else ('F' if w >= 5 else 'M')
                item['rating_val'] = 4 if w >= 8 else (3 if w >= 5 else 2)
                item['score'] = round((item['pct'] / 100) * item['rating_val'], 2)

            mefe_total = 0
            for item in normalized_foda.get('amenazas', []):
                w = int(item.get('weight', 0))
                item['pct'] = round((w / total_external_weight * 100) if total_external_weight else 0, 1)
                item['rating_label'] = 'MD' if w >= 8 else ('D' if w >= 5 else 'M')
                item['rating_val'] = 1 if w >= 8 else (2 if w >= 5 else 3)
                item['score'] = round((item['pct'] / 100) * item['rating_val'], 2)
                mefe_total += item['score']
                
            for item in normalized_foda.get('oportunidades', []):
                mefe_total += item['score']

            normalized_foda['mefe_total'] = round(mefe_total, 2)
            if normalized_foda['mefe_total'] >= 2.5:
                normalized_foda['mefe_analisis'] = f"El puntaje total ponderado de la matriz MEFE es de {normalized_foda['mefe_total']}. Al estar por encima de la media (2.5), se deduce que la entidad está respondiendo favorablemente a su entorno. Las estrategias actuales aprovechan eficazmente las oportunidades existentes mientras mitigan los efectos adversos de las amenazas externas."
            else:
                normalized_foda['mefe_analisis'] = f"El puntaje total ponderado de la matriz MEFE es de {normalized_foda['mefe_total']}. Este valor, por debajo de la media (2.5), indica que la entidad no está respondiendo eficientemente a los factores externos. Las estrategias actuales deben replantearse para capitalizar mejor las oportunidades y crear un escudo robusto ante las amenazas del entorno."

            normalized_foda['estrategias_fo'] = foda.data.get('estrategias_fo', '')
            normalized_foda['estrategias_fa'] = foda.data.get('estrategias_fa', '')
            normalized_foda['estrategias_do'] = foda.data.get('estrategias_do', '')
            normalized_foda['estrategias_da'] = foda.data.get('estrategias_da', '')

            foda.data = normalized_foda
        context['foda'] = foda
        
        mpc = plan.matrices.filter(matrix_type='MPC').first()
        if mpc and mpc.data and 'factors' in mpc.data:
            comps = mpc.data.get('competitors', [])
            factors = mpc.data.get('factors', [])
            num_comps = len(comps)
            totals = [0] * (num_comps + 1)
            
            for factor in factors:
                w = factor.get('weight', 0)
                factor['weight_pct'] = round(w * 100, 1)
                ratings = factor.get('ratings', [])
                scores = []
                for i in range(num_comps + 1):
                    r = ratings[i] if i < len(ratings) else 0
                    score = round(w * r, 2)
                    scores.append({'rating': r, 'score': score})
                    totals[i] += score
                factor['scores'] = scores
                
            mpc.data['totals'] = [round(t, 2) for t in totals]
            
        context['mpc'] = mpc

        context['perspectives'] = plan.perspectives.prefetch_related('objectives__kpis').all()

    return render(request, 'strategic_risk/reports.html', context)
