with open('apps/financial_planning/urls.py', 'r', encoding='utf-8') as f:
    content = f.read()
content = content.replace(
    "    path('plan/<int:plan_id>/api/save_bg_adjustment/', views.api_save_bg_adjustment, name='api_save_bg_adjustment'),\n]",
    "    path('plan/<int:plan_id>/api/save_bg_adjustment/', views.api_save_bg_adjustment, name='api_save_bg_adjustment'),\n    path('plan/<int:plan_id>/api/apply_other_trends/', views.api_apply_other_trends, name='api_apply_other_trends'),\n]"
)
with open('apps/financial_planning/urls.py', 'w', encoding='utf-8') as f:
    f.write(content)
