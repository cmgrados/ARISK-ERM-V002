from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

import openpyxl
from openpyxl.styles import Font, Alignment

from financial_planning.models import PeriodoFinanciero
@login_required
def portal_anexos(request):
    return render(request, 'regulatory_reports/portal_anexos.html')

@login_required
def reporte_13(request):
    return render(request, 'regulatory_reports/reporte_13.html')

# --- Placeholder Views for Other Annexes ---
@login_required
def anexo_2a(request):
    return render(request, 'regulatory_reports/anexo_2a.html')

@login_required
def anexo_2d(request):
    return render(request, 'regulatory_reports/en_construccion.html', {'titulo': 'Anexo 2D'})

@login_required
def anexo_13(request):
    return render(request, 'regulatory_reports/en_construccion.html', {'titulo': 'Anexo 13'})

@login_required
def anexo_15(request):
    return render(request, 'regulatory_reports/en_construccion.html', {'titulo': 'Anexo 15'})

@login_required
def anexo_17b(request):
    return render(request, 'regulatory_reports/en_construccion.html', {'titulo': 'Anexo 17-B'})

@login_required
def anexo_15a(request):
    return render(request, 'regulatory_reports/en_construccion.html', {'titulo': 'Anexo 15A'})

@login_required
def anexo_5(request):
    return render(request, 'regulatory_reports/en_construccion.html', {'titulo': 'Anexo 5'})

@login_required
def anexo_17a(request):
    return render(request, 'regulatory_reports/en_construccion.html', {'titulo': 'Anexo 17-A'})
