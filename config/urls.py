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
from django.http import JsonResponse
from django.db import connection
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

from django.conf import settings
from django.conf.urls.static import static

# Import viewsets
from apps.users.api_views import UserViewSet
from apps.risks.api_views import RiskViewSet, RiskCauseViewSet, RiskConsequenceViewSet, RiskAssessmentViewSet
from apps.credit_risk.api_views import CustomerViewSet, CreditOperationViewSet


def health_check(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return JsonResponse({"status": "ok", "database": "connected"})
    except Exception as e:
        return JsonResponse({"status": "error", "database": str(e)}, status=503)


# API Router
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'risks', RiskViewSet, basename='risk')
router.register(r'risk-causes', RiskCauseViewSet, basename='risk-cause')
router.register(r'risk-consequences', RiskConsequenceViewSet, basename='risk-consequence')
router.register(r'risk-assessments', RiskAssessmentViewSet, basename='risk-assessment')
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'credit-operations', CreditOperationViewSet, basename='credit-operation')

urlpatterns = [
    path('health', health_check),
    path('admin/', admin.site.urls),

    # API endpoints
    path('api/v1/', include(router.urls)),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Web UI
    path('', include('dashboards.urls')),
    path('utilities/', RedirectView.as_view(url='/utilitarios/', permanent=True)),
    path('utilities/bulk-load/liability/', RedirectView.as_view(url='/utilitarios/carga-masiva-pasivos/', permanent=True)),
    path('credito/', include('credit_risk.urls')),
    path('riesgos/', include('risks.urls')),
    path('controles/', include('controls.urls')),
    path('catalogos/', include('catalogs.urls')),
    path('planes-accion/', include('action_plans.urls')),
    path('reportes/', include('reports.urls')),
    path('agente-ia/', include('ai_assistant.urls')),
    path('utilitarios/', include('utilities.urls')),
    path('usuarios/', include('users.urls')),
    path('modulo-riesgo/', include('modulo_riesgo_credito.urls')),
    path('liquidez/', include('liquidity_risk.urls', namespace='liquidity_risk')),
    path('auditoria/', include('audit.urls')),
    path('riesgo-operacional/', include('apps.op_risk.urls')),
    path('mercado/', include('apps.market_risk.urls', namespace='market_risk')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
