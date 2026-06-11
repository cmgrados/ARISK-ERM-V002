from django.shortcuts import render
from django.http import HttpResponse

def dashboard(request):
    return HttpResponse("Módulo de Planeamiento Financiero (En Desarrollo)")

def trial_balance_viewer_no_id(request):
    return HttpResponse("Balance de Comprobación (En Desarrollo)")

def budget_wizard_new(request):
    return HttpResponse("Asistente Presupuesto (En Desarrollo)")
