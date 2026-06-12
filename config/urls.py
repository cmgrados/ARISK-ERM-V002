"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

from django.conf import settings
from django.conf.urls.static import static

from apps.strategic_risk import views as strategic_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboards.urls')),
    path('utilities/', RedirectView.as_view(url='/utilitarios/', permanent=True)),
    path('utilities/bulk-load/liability/', RedirectView.as_view(url='/utilitarios/carga-masiva-pasivos/', permanent=True)),
    path('credito/', include('credit_risk.urls')),
    path('riesgo-operacional/', include('operational_risk.urls')),
    path('riesgos/', include('risks.urls')),
    path('controles/', include('controls.urls')),
    path('catalogos/', include('catalogs.urls')),
    path('planes-accion/', include('action_plans.urls')),
    path('riesgo-plaft/', include('plaft_risk.urls')),
    path('riesgo-cumplimiento/', include('compliance_risk.urls')),
    path('liquidez/', include('liquidity_risk.urls')),
    path('mercado/', include('market_risk.urls')),
    path('estrategico/', include('strategic_risk.urls')),
    path('reputacional/', include('reputational_risk.urls')),
    path('reportes/', include('reports.urls')),
    path('agente-ia/', include('ai_assistant.urls')),
    path('utilitarios/', include('utilities.urls')),
    path('apetito/', include('risk_appetite.urls')),
    path('planificacion-financiera/', include('financial_planning.urls')),
    path('usuarios/', include('users.urls')),
    path('encuesta/<str:survey_id>/', strategic_views.public_survey, name='public_survey'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
