import re

with open(r'c:\Users\VICTUS\Desktop\A.RISK ERM\apps\financial_planning\views.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Fix ml_montecarlo_projection
old_mc = """        budget_data = plan.budget_data
        
        if not budget_data or 'income_statement' not in budget_data:
            return JsonResponse({'status': 'error', 'msg': 'No hay datos hist\u00f3ricos.'}, status=400)
            
        selected_periods = budget_data.get('selected_periods', [])
        if not selected_periods:
            return JsonResponse({'status': 'error', 'msg': 'No hay periodos seleccionados.'}, status=400)
            
        trends = {}
        
        for item in budget_data['income_statement']:"""
new_mc = """        budget_data = plan.budget_data
        hist_data = plan.historical_data or {}
        source_data = budget_data if budget_data and 'income_statement' in budget_data else hist_data
        
        if not source_data or 'income_statement' not in source_data:
            return JsonResponse({'status': 'error', 'msg': 'No hay datos históricos.'}, status=400)
            
        selected_periods = source_data.get('selected_periods', [])
        if not selected_periods:
            selected_periods = hist_data.get('selected_periods', [])
        if not selected_periods:
            return JsonResponse({'status': 'error', 'msg': 'No hay periodos seleccionados.'}, status=400)
            
        trends = {}
        
        for item in source_data['income_statement']:"""
text = text.replace(old_mc, new_mc)

# Fix ml_trend_projection
old_trend = """    budget_data = plan.budget_data
    
    if not budget_data or 'income_statement' not in budget_data:
        return JsonResponse({'status': 'error', 'msg': 'No hay datos base hist\u00f3ricos.'}, status=400)
        
    selected_periods = budget_data.get('selected_periods', [])
    if not selected_periods:
        return JsonResponse({'status': 'error', 'msg': 'No hay periodos seleccionados.'}, status=400)
        
    trends = {}
    
    for item in budget_data['income_statement']:"""
new_trend = """    budget_data = plan.budget_data
    hist_data = plan.historical_data or {}
    source_data = budget_data if budget_data and 'income_statement' in budget_data else hist_data
    
    if not source_data or 'income_statement' not in source_data:
        return JsonResponse({'status': 'error', 'msg': 'No hay datos históricos.'}, status=400)
        
    selected_periods = source_data.get('selected_periods', [])
    if not selected_periods:
        selected_periods = hist_data.get('selected_periods', [])
    if not selected_periods:
        return JsonResponse({'status': 'error', 'msg': 'No hay periodos seleccionados.'}, status=400)
        
    trends = {}
    
    for item in source_data['income_statement']:"""
text = text.replace(old_trend, new_trend)

with open(r'c:\Users\VICTUS\Desktop\A.RISK ERM\apps\financial_planning\views.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("views patched")
