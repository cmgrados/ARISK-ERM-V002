from django.core.management.base import BaseCommand
from django.test import RequestFactory

class Command(BaseCommand):
    def handle(self, *args, **options):
        from apps.financial_planning.views import api_get_projected_balance_data
        from users.models import User
        
        user = User.objects.filter(is_superuser=True).first()
        factory = RequestFactory()
        request = factory.get('/planificacion-financiera/plan/1/api/api_get_projected_balance_data/?scenario=BASE')
        request.user = user

        try:
            response = api_get_projected_balance_data(request, 1)
            print("STATUS:", response.status_code)
            print("CONTENT:", response.content.decode('utf-8')[:1500])
        except Exception as e:
            import traceback
            traceback.print_exc()
