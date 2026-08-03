from django.core.management.base import BaseCommand
from django.test import RequestFactory
from django.contrib.auth import get_user_model
from financial_planning.views import api_sync_core_trends_bg, api_apply_other_trends
import traceback

class Command(BaseCommand):
    def handle(self, *args, **options):
        User = get_user_model()
        user = User.objects.first()
        plan_id = 3

        factory = RequestFactory()
        request = factory.post(f'/planificacion-financiera/plan/{plan_id}/api/sync_core_trends_bg/', '{"scenario": "BASE"}', content_type='application/json')
        request.user = user
        request.session = {}

        print("Testing api_sync_core_trends_bg...")
        try:
            response = api_sync_core_trends_bg(request, plan_id)
            print(f"Status code: {response.status_code}")
            print(f"Response content: {response.content}")
        except Exception as e:
            traceback.print_exc()

        print("\nTesting api_apply_other_trends...")
        request_apply = factory.post(f'/planificacion-financiera/plan/{plan_id}/api/apply_other_trends/', '{"scenario": "BASE"}', content_type='application/json')
        request_apply.user = user
        request_apply.session = {}
        try:
            response = api_apply_other_trends(request_apply, plan_id)
            print(f"Status code: {response.status_code}")
            print(f"Response content: {response.content}")
        except Exception as e:
            traceback.print_exc()
            
        print("\nTesting api_save_bg_snapshot...")
        from financial_planning.views import api_save_bg_snapshot
        req_save = factory.post(f'/planificacion-financiera/plan/{plan_id}/api/save_bg_snapshot/', '{"scenario": "BASE"}', content_type='application/json')
        req_save.user = user
        req_save.session = {}
        try:
            response = api_save_bg_snapshot(req_save, plan_id)
            print(f"Status code: {response.status_code}")
            print(f"Response content: {response.content}")
        except Exception as e:
            traceback.print_exc()
