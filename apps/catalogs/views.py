import io
import pandas as pd
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import OrganizationalUnit, Process, Subprocess
from .forms import OrganizationalUnitForm, ProcessForm, SubprocessForm


def catalogs_dashboard(request):
    units = OrganizationalUnit.objects.all().select_related('parent')
    processes = Process.objects.all().select_related('owner')
    subprocesses = Subprocess.objects.all().select_related('process')
    
    context = {
        'units': units,
        'processes': processes,
        'subprocesses': subprocesses,
    }
    return render(request, 'catalogs/dashboard.html', context)

# --- Organizational Unit CRUD ---

def create_unit(request):
    if request.method == 'POST':
        form = OrganizationalUnitForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Unidad creada exitosamente.")
            return redirect('catalogs:dashboard')
    else:
        form = OrganizationalUnitForm()
    return render(request, 'catalogs/form_generic.html', {'form': form, 'title': 'Nueva Unidad Organizacional'})


def edit_unit(request, pk):
    unit = get_object_or_404(OrganizationalUnit, pk=pk)
    if request.method == 'POST':
        form = OrganizationalUnitForm(request.POST, instance=unit)
        if form.is_valid():
            form.save()
            messages.success(request, "Unidad actualizada exitosamente.")
            return redirect('catalogs:dashboard')
    else:
        form = OrganizationalUnitForm(instance=unit)
    return render(request, 'catalogs/form_generic.html', {'form': form, 'title': 'Editar Unidad Organizacional'})


def delete_unit(request, pk):
    unit = get_object_or_404(OrganizationalUnit, pk=pk)
    if request.method == 'POST':
        unit.delete()
        messages.success(request, "Unidad eliminada exitosamente.")
        return redirect('catalogs:dashboard')
    return render(request, 'catalogs/confirm_delete.html', {'object': unit, 'title': 'Eliminar Unidad', 'cancel_url': 'catalogs:dashboard'})

# --- Process CRUD ---

def create_process(request):
    if request.method == 'POST':
        form = ProcessForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Proceso creado exitosamente.")
            return redirect('catalogs:dashboard')
    else:
        form = ProcessForm()
    return render(request, 'catalogs/form_generic.html', {'form': form, 'title': 'Nuevo Proceso'})


def edit_process(request, pk):
    process = get_object_or_404(Process, pk=pk)
    if request.method == 'POST':
        form = ProcessForm(request.POST, instance=process)
        if form.is_valid():
            form.save()
            messages.success(request, "Proceso actualizado exitosamente.")
            return redirect('catalogs:dashboard')
    else:
        form = ProcessForm(instance=process)
    return render(request, 'catalogs/form_generic.html', {'form': form, 'title': 'Editar Proceso'})


def delete_process(request, pk):
    process = get_object_or_404(Process, pk=pk)
    if request.method == 'POST':
        process.delete()
        messages.success(request, "Proceso eliminado exitosamente.")
        return redirect('catalogs:dashboard')
    return render(request, 'catalogs/confirm_delete.html', {'object': process, 'title': 'Eliminar Proceso', 'cancel_url': 'catalogs:dashboard'})

# --- Subprocess CRUD ---

def create_subprocess(request):
    if request.method == 'POST':
        form = SubprocessForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Subproceso creado exitosamente.")
            return redirect('catalogs:dashboard')
    else:
        form = SubprocessForm()
    return render(request, 'catalogs/form_generic.html', {'form': form, 'title': 'Nuevo Subproceso'})


def edit_subprocess(request, pk):
    subprocess = get_object_or_404(Subprocess, pk=pk)
    if request.method == 'POST':
        form = SubprocessForm(request.POST, instance=subprocess)
        if form.is_valid():
            form.save()
            messages.success(request, "Subproceso actualizado exitosamente.")
            return redirect('catalogs:dashboard')
    else:
        form = SubprocessForm(instance=subprocess)
    return render(request, 'catalogs/form_generic.html', {'form': form, 'title': 'Editar Subproceso'})


def delete_subprocess(request, pk):
    subprocess = get_object_or_404(Subprocess, pk=pk)
    if request.method == 'POST':
        subprocess.delete()
        messages.success(request, "Subproceso eliminado exitosamente.")
        return redirect('catalogs:dashboard')
    return render(request, 'catalogs/confirm_delete.html', {'object': subprocess, 'title': 'Eliminar Subproceso', 'cancel_url': 'catalogs:dashboard'})

# --- Bulk Load (Excel) ---

def download_catalogs_template(request):
    import xlsxwriter
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    
    # Formats
    header_format = workbook.add_format({
        'bold': True, 'bg_color': '#D9E1F2', 'border': 1, 'align': 'center', 'valign': 'vcenter'
    })
    
    # Sheet 1: Unidades
    sheet_units = workbook.add_worksheet("Unidades")
    headers_units = ['Nombre Unidad', 'Dependencia (Padre)', 'Es Agencia (SI/NO)', 'Descripción']
    for col_num, data in enumerate(headers_units):
        sheet_units.write(0, col_num, data, header_format)
        sheet_units.set_column(col_num, col_num, 25)
    
    # Pre-fill units based on user chart
    example_units = [
        ['CONSEJO DE ADMINISTRACION', '', 'NO', 'Nivel máximo directivo'],
        ['COMITE DE RIESGOS', 'CONSEJO DE ADMINISTRACION', 'NO', ''],
        ['GERENTE GENERAL', 'CONSEJO DE ADMINISTRACION', 'NO', ''],
        ['UNIDAD DE OPERACIONES', 'GERENTE GENERAL', 'NO', ''],
        ['OF. AREQUIPA', 'GERENTE GENERAL', 'SI', 'Agencia Arequipa'],
    ]
    for row_num, row_data in enumerate(example_units, start=1):
        for col_num, value in enumerate(row_data):
            sheet_units.write(row_num, col_num, value)

    # Sheet 2: Procesos
    sheet_processes = workbook.add_worksheet("Procesos")
    headers_processes = ['Nombre Proceso', 'Username Responsable', 'Descripción']
    for col_num, data in enumerate(headers_processes):
        sheet_processes.write(0, col_num, data, header_format)
        sheet_processes.set_column(col_num, col_num, 30)

    # Sheet 3: Subprocesos
    sheet_subprocesses = workbook.add_worksheet("Subprocesos")
    headers_subprocesses = ['Proceso Padre', 'Nombre Subproceso', 'Descripción']
    for col_num, data in enumerate(headers_subprocesses):
        sheet_subprocesses.write(0, col_num, data, header_format)
        sheet_subprocesses.set_column(col_num, col_num, 30)
        
    workbook.close()
    output.seek(0)
    
    _content = output.getvalue() if hasattr(output, "getvalue") else output.read()
    response = HttpResponse(_content, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="Plantilla_Catalogos_A_RISK.xlsx"'
    return response

def import_catalogs_excel(request):
    if request.method == 'POST':
        excel_file = request.FILES.get('excel_file')
        if not excel_file:
            messages.error(request, "Debe seleccionar un archivo Excel.")
            return redirect('catalogs:dashboard')

        try:
            # 1. Unidades de Área
            try:
                df_units = pd.read_excel(excel_file, sheet_name='Unidades')
                # Process units in two passes to handle dependencies
                # Pass 1: Create all without parents
                created_units = {}
                for index, row in df_units.iterrows():
                    name = str(row.get('Nombre Unidad', '')).strip()
                    if pd.isna(name) or name == '' or name == 'nan':
                        continue
                        
                    is_agency = str(row.get('Es Agencia (SI/NO)', 'NO')).strip().upper() == 'SI'
                    desc = str(row.get('Descripción', ''))
                    if pd.isna(desc) or desc == 'nan': desc = ''
                        
                    unit, created = OrganizationalUnit.objects.get_or_create(
                        name=name,
                        defaults={'description': desc, 'is_agency': is_agency}
                    )
                    created_units[name] = unit
                    
                # Pass 2: Link parents
                for index, row in df_units.iterrows():
                    name = str(row.get('Nombre Unidad', '')).strip()
                    parent_name = str(row.get('Dependencia (Padre)', '')).strip()
                    if parent_name and parent_name != 'nan' and name in created_units:
                        # Find parent
                        parent_unit = OrganizationalUnit.objects.filter(name__iexact=parent_name).first()
                        if parent_unit:
                            unit = created_units[name]
                            unit.parent = parent_unit
                            unit.save()
            except Exception as e:
                print("Skipping units:", e)
                pass # Maybe the sheet was missing

            # 2. Procesos
            try:
                df_procs = pd.read_excel(excel_file, sheet_name='Procesos')
                for index, row in df_procs.iterrows():
                    name = str(row.get('Nombre Proceso', '')).strip()
                    if pd.isna(name) or name == '' or name == 'nan': continue
                        
                    desc = str(row.get('Descripción', ''))
                    if pd.isna(desc) or desc == 'nan': desc = ''
                    
                    username = str(row.get('Username Responsable', '')).strip()
                    owner = None
                    if username and username != 'nan':
                        from django.contrib.auth import get_user_model
                        User = get_user_model()
                        owner = User.objects.filter(username=username).first()
                        
                    Process.objects.get_or_create(
                        name=name,
                        defaults={'description': desc, 'owner': owner}
                    )
            except Exception as e:
                print("Skipping processes:", e)
                pass
                
            # 3. Subprocesos
            try:
                df_subprocs = pd.read_excel(excel_file, sheet_name='Subprocesos')
                for index, row in df_subprocs.iterrows():
                    process_name = str(row.get('Proceso Padre', '')).strip()
                    name = str(row.get('Nombre Subproceso', '')).strip()
                    if pd.isna(name) or name == '' or name == 'nan': continue
                        
                    desc = str(row.get('Descripción', ''))
                    if pd.isna(desc) or desc == 'nan': desc = ''
                        
                    parent_process = Process.objects.filter(name__iexact=process_name).first()
                    if parent_process:
                        Subprocess.objects.get_or_create(
                            process=parent_process,
                            name=name,
                            defaults={'description': desc}
                        )
            except Exception as e:
                print("Skipping subprocesses:", e)
                pass

            messages.success(request, "Importación masiva completada exitosamente.")
            
        except Exception as e:
            messages.error(request, f"Error al procesar el archivo: {str(e)}")

from risks.models import Risk

from operational_risk.models import OpRiskIncident

def process_detail(request, pk):
    process = get_object_or_404(Process, pk=pk)
    risks = Risk.objects.filter(process=process)
    subprocesses = Subprocess.objects.filter(process=process)
    incidents = OpRiskIncident.objects.filter(process=process).order_by('-incident_date')
    related_processes = process.related_processes.all()
    
    context = {
        'process': process,
        'risks': risks,
        'subprocesses': subprocesses,
        'incidents': incidents,
        'related_processes': related_processes,
        'title': f"Detalle de Proceso: {process.name}"
    }
    return render(request, 'catalogs/process_detail.html', context)
