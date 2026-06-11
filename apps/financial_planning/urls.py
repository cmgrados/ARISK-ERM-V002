from django.urls import path
from . import views

app_name = 'financial_planning'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('balance-comprobacion/', views.trial_balance_viewer_no_id, name='trial_balance_viewer_no_id'),
    path('budget-wizard/new/', views.budget_wizard_new, name='budget_wizard_new'),
]
