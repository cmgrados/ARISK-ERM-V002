from django.shortcuts import render
from django.http import JsonResponse

def dashboard(request):
    context = {'page_title': 'Agente Inteligente de Riesgos - IA'}
    return render(request, 'ai_assistant/dashboard.html', context)

def ask_ai(request):
    if request.method == 'POST':
        query = request.POST.get('query', '').lower()
        if 'apetito' in query or 'kri' in query or 'tolerancia' in query:
            response_text = "Analizando KRIs... He detectado que el Indicador de Alertas PLAFT ha excedido el límite crítico de tolerancia (12 alertas vs límite de 10). Se recomienda escalar al Comité de Riesgos y revisar los procesos de debida diligencia intensificada."
        elif 'crédito' in query or 'mora' in query:
            response_text = "El ratio de mora total se encuentra en 8.4%, superando el apetito objetivo del 6%. Sin embargo, aún está dentro del margen de tolerancia amarillo. Sugiera monitorear la cosecha de Marzo para identificar desviaciones por producto."
        else:
            response_text = f"Analizando '{query}'... Según los datos consolidados, la exposición global de la entidad se mantiene en un nivel moderado, con una utilización del apetito al riesgo del 65%."
        
        return JsonResponse({'response': response_text})
    return JsonResponse({'error': 'Invalid request'}, status=400)
