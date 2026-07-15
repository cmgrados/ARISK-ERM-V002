with open('apps/financial_planning/views.py', 'r', encoding='utf-8') as f:
    in_func = False
    for line in f:
        if 'def assign_institutional_budget_to_plan(' in line:
            in_func = True
        if in_func:
            print(line, end='')
            if 'return JsonResponse' in line and 'success' in line:
                break
