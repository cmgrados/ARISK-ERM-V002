import os

modules = [
    ('liquidity_risk', 'Riesgo de Liquidez', 'fas fa-water'),
    ('market_risk', 'Riesgo de Mercado', 'fas fa-chart-bar'),
    ('plaft_risk', 'Riesgo PLAFT', 'fas fa-user-secret'),
    ('strategic_risk', 'Riesgo Estratégico', 'fas fa-chess'),
    ('reputational_risk', 'Riesgo Reputacional', 'fas fa-bullhorn'),
    ('reports', 'Reportes e Informes', 'fas fa-file-pdf'),
    ('ai_assistant', 'Agente Inteligente IA', 'fas fa-robot'),
    ('utilities', 'Utilitarios', 'fas fa-tools')
]

urls_template = """from django.urls import path
from . import views

app_name = '{module}'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
]
"""

views_template = """from django.shortcuts import render

def dashboard(request):
    context = {{
        'page_title': '{title}'
    }}
    return render(request, '{module}/dashboard.html', context)
"""

html_template = """{{% extends 'base.html' %}}

{{% block title_header %}}{title}{{% endblock %}}

{{% block content %}}
<div class="row">
    <div class="col-12">
        <div class="callout callout-info badge-light shadow-sm" style="border-left-color: #161065;">
            <h5><i class="{icon} mr-2"></i>Módulo en Construcción</h5>
            <p>Bienvenido al módulo de <strong>{title}</strong>. Las funcionales gráficas y reportes de esta sección se irán activando según el avance del plan de fases de desarrollo.</p>
        </div>
    </div>
</div>

<div class="row mt-4">
    <div class="col-lg-3 col-6">
        <div class="small-box" style="background-color: #161065; color: white;">
            <div class="inner">
                <h3>0</h3>
                <p>Métricas Principales</p>
            </div>
            <div class="icon text-white-50">
                <i class="{icon}"></i>
            </div>
        </div>
    </div>
    <div class="col-lg-3 col-6">
        <div class="small-box" style="background-color: #ffcc00; color: #141313;">
            <div class="inner">
                <h3>S/ 0.00</h3>
                <p>Exposiciones</p>
            </div>
            <div class="icon text-dark" style="opacity: 0.2;">
                <i class="fas fa-chart-line"></i>
            </div>
        </div>
    </div>
</div>
{{% endblock %}}
"""

for module, title, icon in modules:
    # write urls.py
    with open(f"apps/{module}/urls.py", "w", encoding="utf-8") as f:
        f.write(urls_template.format(module=module))
    
    # write views.py
    with open(f"apps/{module}/views.py", "w", encoding="utf-8") as f:
        f.write(views_template.format(module=module, title=title))
    
    # create templates dir and write file
    template_dir = f"templates/{module}"
    os.makedirs(template_dir, exist_ok=True)
    with open(f"{template_dir}/dashboard.html", "w", encoding="utf-8") as f:
        f.write(html_template.format(module=module, title=title, icon=icon))

print("All module views scaffolded successfully!")
