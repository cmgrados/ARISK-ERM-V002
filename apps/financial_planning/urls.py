from django.urls import path
from . import views

app_name = 'financial_planning'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('balance-comprobacion/', views.trial_balance_viewer_no_id, name='trial_balance_viewer_no_id'),
    path('plan/nuevo/', views.plan_wizard_new, name='plan_wizard_new'),
    path('plan/<int:plan_id>/eliminar/', views.delete_plan, name='delete_plan'),
    path('plan/<int:plan_id>/wizard/', views.budget_wizard_new, name='plan_wizard'),
    path('plan/<int:plan_id>/balance/', views.trial_balance_viewer_no_id, name='trial_balance_viewer'),
    path('budget-wizard/new/', views.budget_wizard_new, name='budget_wizard_new'),
    path('api/api_historical_portfolio_data/', views.api_historical_portfolio_data, name='api_historical_portfolio_data'),
    path('api/api_available_portfolio_dates/', views.api_available_portfolio_dates, name='api_available_portfolio_dates'),
    path('api/api_historical_passive_data/', views.api_historical_passive_data, name='api_historical_passive_data'),
    path('api/api_available_passive_dates/', views.api_available_passive_dates, name='api_available_passive_dates'),
    path('api/api_available_historical_dates/', views.api_available_historical_dates, name='api_available_historical_dates'),
    path('api/api_trial_balance_data/', views.api_trial_balance_data, name='api_trial_balance_data'),
    path('plan/<int:plan_id>/api/api_get_trend_data/', views.api_get_trend_data, name='api_get_trend_data'),
    path('plan/<int:plan_id>/api/manage_assumptions/', views.manage_assumptions, name='manage_assumptions'),
    path('plan/<int:plan_id>/api/api_save_step_periods/', views.api_save_step_periods, name='api_save_step_periods'),
    path('plan/<int:plan_id>/api/api_run_montecarlo/', views.api_run_montecarlo, name='api_run_montecarlo'),
    path('plan/<int:plan_id>/api/save_institutional_assumptions/', views.save_institutional_assumptions, name='save_institutional_assumptions'),
    path('plan/<int:plan_id>/api/api_unlock_step6/', views.api_unlock_step6, name='api_unlock_step6'),
    path('plan/<int:plan_id>/api/api_save_trend_scenarios/', views.api_save_trend_scenarios, name='api_save_trend_scenarios'),
    path('plan/<int:plan_id>/api/toggle_step_lock/', views.toggle_step_lock, name='toggle_step_lock'),
    path('plan/<int:plan_id>/api/ml_trend_projection/', views.ml_trend_projection, name='ml_trend_projection'),
    path('plan/<int:plan_id>/api/ml_montecarlo_projection/', views.ml_montecarlo_projection, name='ml_montecarlo_projection'),
    path('plan/<int:plan_id>/api/api_lock_step6/', views.api_lock_step6, name='api_lock_step6'),
    path('plan/<int:plan_id>/api/projected_results/', views.projected_results, name='projected_results'),
    path('api/assign_trial_balance_to_plan/', views.assign_trial_balance_to_plan, name='assign_trial_balance_to_plan'),
]
