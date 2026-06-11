import re
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

with open(r'c:\Users\VICTUS\Desktop\A.RISK ERM\apps\financial_planning\views.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace ml_montecarlo_projection
old_mc = """def ml_montecarlo_projection(request, plan_id):
    try:
        from .trend_engine import TrendAnalyzer
        import numpy as np

        plan = get_object_or_404(FinancialPlan, id=plan_id)
        budget_data = plan.budget_data
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
        
        for item in source_data['income_statement']:
            code = item.get('code')
            balances = item.get('balances', {})
            
            # We only need to process if there's enough data
            if len(selected_periods) < 2:
                continue
                
            sorted_periods = sorted(selected_periods)
            vals = [balances.get(p, 0.0) for p in sorted_periods]
            
            # Generate Montecarlo for 3 years (36 months)
            num_projected_periods = 36 
            
            pesimista_series, base_series, optimista_series = TrendAnalyzer.apply_montecarlo(
                historical_values=vals,
                periods=sorted_periods,
                num_simulations=1000,
                num_projected_periods=num_projected_periods
            )
            
            # Trends returns 3 series (length = num_projected_periods)
            trends[code] = {
                'pesimista': pesimista_series,
                'base': base_series,
                'optimista': optimista_series
            }
            
        return JsonResponse({
            'status': 'success',
            'trends': trends
        })
    except Exception as e:
        import traceback
        return JsonResponse({'status': 'error', 'msg': str(e), 'traceback': traceback.format_exc()}, status=500)"""

new_mc = """def ml_montecarlo_projection(request, plan_id):
    try:
        from .trend_engine import TrendAnalyzer
        import numpy as np

        plan = get_object_or_404(FinancialPlan, id=plan_id)
        budget_data = plan.budget_data
        hist_data = plan.historical_data or {}
        source_data = budget_data if budget_data and 'income_statement' in budget_data else hist_data
        
        if not source_data or 'income_statement' not in source_data:
            return JsonResponse({'status': 'error', 'msg': 'No hay datos hist\u00f3ricos.'}, status=400)
            
        selected_periods = source_data.get('selected_periods', [])
        if not selected_periods:
            selected_periods = hist_data.get('selected_periods', [])
        if not selected_periods:
            return JsonResponse({'status': 'error', 'msg': 'No hay periodos seleccionados.'}, status=400)
            
        trends = {}
        
        for item in source_data['income_statement']:
            if isinstance(item, dict):
                code = item.get('code')
                balances = item.get('balances', {})
                sorted_periods = sorted(selected_periods)
                vals = [balances.get(p, 0.0) for p in sorted_periods]
            else:
                code_str = str(item[0])
                code = code_str.split(' - ')[0].strip()
                sorted_periods = sorted(selected_periods)
                vals = item[1:]
            
            # We only need to process if there's enough data
            if len(vals) < 2:
                continue
                
            # Generate Montecarlo for 3 years (36 months)
            num_projected_periods = 36 
            
            pesimista_series, base_series, optimista_series = TrendAnalyzer.apply_montecarlo(
                historical_values=vals,
                periods=sorted_periods,
                num_simulations=1000,
                num_projected_periods=num_projected_periods
            )
            
            # Trends returns 3 series (length = num_projected_periods)
            trends[code] = {
                'pesimista': pesimista_series,
                'base': base_series,
                'optimista': optimista_series
            }
            
        return JsonResponse({
            'status': 'success',
            'trends': trends
        })
    except Exception as e:
        import traceback
        return JsonResponse({'status': 'error', 'msg': str(e), 'traceback': traceback.format_exc()}, status=500)"""

text = text.replace(old_mc, new_mc)


# Replace ml_trend_projection
old_trend = """def ml_trend_projection(request, plan_id):
    plan = get_object_or_404(FinancialPlan, id=plan_id)
    budget_data = plan.budget_data
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
    
    for item in source_data['income_statement']:
        code = item.get('code')
        balances = item.get('balances', {})
        
        # We only need to process if there's enough data
        if len(selected_periods) < 2:
            trends[code] = 0.0
            continue
            
        # Fast plain python conversion for this single time series
        # We know selected_periods is sorted chronologically if we sort it once
        
        # Sort periods just in case
        sorted_periods = sorted(selected_periods)
        
        # Extract balances
        vals = [balances.get(p, 0.0) for p in sorted_periods]
        
        # Convert to numpy array for fast vectorized operations
        arr = np.array(vals, dtype=float)
        
        # Get month integers
        months = np.array([int(p.split('-')[1]) for p in sorted_periods])
        
        # Calculate prev_balance (shift by 1)
        prev_arr = np.roll(arr, 1)
        if len(prev_arr) > 0:
            prev_arr[0] = 0.0
            
        # Vectorized monthly flow
        # If month == 1, flow is the YTD balance. Else, flow = balance - prev_balance
        monthly_flow = np.where(months == 1, arr, arr - prev_arr)
        
        # Series extraction for trend calculation
        if len(monthly_flow) >= 24:
            last_12 = monthly_flow[-12:]
            prev_12 = monthly_flow[-24:-12]
            
            sum_last_12 = np.sum(last_12)
            sum_prev_12 = np.sum(prev_12)
            
            if sum_prev_12 != 0:
                trend_pct = ((sum_last_12 - sum_prev_12) / abs(sum_prev_12)) * 100
                trends[code] = float(min(max(trend_pct, -100), 999))
            else:
                trends[code] = 0.0
        else:
            # Fallback for simple calculation if not enough history
            dec_periods = [p for p in sorted_periods if p.endswith('-12')]
            if len(dec_periods) >= 2:
                last_dec = dec_periods[-1]
                prev_dec = dec_periods[-2]
                val_last = balances.get(last_dec, 0.0)
                val_prev = balances.get(prev_dec, 0.0)
                if val_prev != 0:
                    trend_pct = ((val_last - val_prev) / abs(val_prev)) * 100
                    trends[code] = float(min(max(trend_pct, -100), 999))
                else:
                    trends[code] = 0.0
            else:
                trends[code] = 0.0
                
    return JsonResponse({
        'status': 'success',
        'trends': trends
    })"""

new_trend = """def ml_trend_projection(request, plan_id):
    plan = get_object_or_404(FinancialPlan, id=plan_id)
    budget_data = plan.budget_data
    hist_data = plan.historical_data or {}
    source_data = budget_data if budget_data and 'income_statement' in budget_data else hist_data
    
    if not source_data or 'income_statement' not in source_data:
        return JsonResponse({'status': 'error', 'msg': 'No hay datos hist\u00f3ricos.'}, status=400)
        
    selected_periods = source_data.get('selected_periods', [])
    if not selected_periods:
        selected_periods = hist_data.get('selected_periods', [])
    if not selected_periods:
        return JsonResponse({'status': 'error', 'msg': 'No hay periodos seleccionados.'}, status=400)
        
    trends = {}
    
    for item in source_data['income_statement']:
        if isinstance(item, dict):
            code = item.get('code')
            balances = item.get('balances', {})
            sorted_periods = sorted(selected_periods)
            vals = [balances.get(p, 0.0) for p in sorted_periods]
        else:
            code_str = str(item[0])
            code = code_str.split(' - ')[0].strip()
            sorted_periods = sorted(selected_periods)
            vals = item[1:]
        
        # We only need to process if there's enough data
        if len(vals) < 2:
            trends[code] = {'base': 0.0, 'pesimista': 0.0, 'optimista': 0.0}
            continue
            
        arr = np.array(vals, dtype=float)
        months = np.array([int(p.split('-')[1]) for p in sorted_periods])
        prev_arr = np.roll(arr, 1)
        if len(prev_arr) > 0:
            prev_arr[0] = 0.0
            
        monthly_flow = np.where(months == 1, arr, arr - prev_arr)
        
        base_trend = 0.0
        volatility = 5.0 # default 5%
        
        if len(monthly_flow) >= 24:
            last_12 = monthly_flow[-12:]
            prev_12 = monthly_flow[-24:-12]
            sum_last_12 = np.sum(last_12)
            sum_prev_12 = np.sum(prev_12)
            if sum_prev_12 != 0:
                base_trend = ((sum_last_12 - sum_prev_12) / abs(sum_prev_12)) * 100
                base_trend = float(min(max(base_trend, -100), 999))
                # Volatility could be calculated based on historical variance
                # Using a fixed 10% of base or standard deviation
                # A simple approximation: std dev of month-over-month growth if possible
                volatility = np.std(last_12) / (abs(np.mean(last_12)) + 1e-9) * 10.0
                volatility = float(min(max(volatility, 1.0), 15.0)) # bounded between 1% and 15%
        else:
            if isinstance(item, dict):
                balances = item.get('balances', {})
                dec_periods = [p for p in sorted_periods if p.endswith('-12')]
                if len(dec_periods) >= 2:
                    val_last = balances.get(dec_periods[-1], 0.0)
                    val_prev = balances.get(dec_periods[-2], 0.0)
                    if val_prev != 0:
                        base_trend = ((val_last - val_prev) / abs(val_prev)) * 100
                        base_trend = float(min(max(base_trend, -100), 999))
                        volatility = 5.0
            else:
                pass
                
        trends[code] = {
            'base': base_trend,
            'pesimista': base_trend - volatility,
            'optimista': base_trend + volatility
        }
                
    return JsonResponse({
        'status': 'success',
        'trends': trends
    })"""
text = text.replace(old_trend, new_trend)

with open(r'c:\Users\VICTUS\Desktop\A.RISK ERM\apps\financial_planning\views.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("views completely patched")
