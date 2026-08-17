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
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

from django.conf import settings
from django.conf.urls.static import static

from strategic_risk import views as strategic_views

# Initialize DRF Router
router = DefaultRouter()

# Register User ViewSets
from users.api_views import UserViewSet, OrganizationViewSet, RoleViewSet
router.register(r'users', UserViewSet, basename='user')
router.register(r'organizations', OrganizationViewSet, basename='organization')
router.register(r'roles', RoleViewSet, basename='role')

# Register Risk ViewSets
from risks.api_views import (
    RiskViewSet, RiskCauseViewSet, RiskConsequenceViewSet,
    RiskAssessmentViewSet, ProbabilityScaleViewSet, ImpactScaleViewSet,
    RiskMatrixConfigurationViewSet
)
router.register(r'risks', RiskViewSet, basename='risk')
router.register(r'risk-causes', RiskCauseViewSet, basename='risk-cause')
router.register(r'risk-consequences', RiskConsequenceViewSet, basename='risk-consequence')
router.register(r'risk-assessments', RiskAssessmentViewSet, basename='risk-assessment')
router.register(r'probability-scales', ProbabilityScaleViewSet, basename='probability-scale')
router.register(r'impact-scales', ImpactScaleViewSet, basename='impact-scale')
router.register(r'risk-matrix-configs', RiskMatrixConfigurationViewSet, basename='risk-matrix-config')

# Register Credit Risk ViewSets
from credit_risk.api_views import (
    CustomerViewSet, CreditOperationViewSet, CreditRiskMetricsViewSet,
    CreditRiskPeriodParameterViewSet
)
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'credit-operations', CreditOperationViewSet, basename='credit-operation')
router.register(r'credit-risk-metrics', CreditRiskMetricsViewSet, basename='credit-risk-metric')
router.register(r'credit-risk-parameters', CreditRiskPeriodParameterViewSet, basename='credit-risk-parameter')

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # API v1 - DRF Router
    path('api/v1/', include(router.urls)),

    # OpenAPI / Swagger Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Traditional URLs
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
    path('reportes-regulatorios/', include('apps.regulatory_reports.urls')),
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
