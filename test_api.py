import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from financial_planning.views import api_get_budget_data
from django.test import RequestFactory
from users.models import User
req = RequestFactory().get('/?scenario=Base')
req.user = User.objects.first()
try:
    res = api_get_budget_data(req, 3)
    print("STATUS CODE:", res.status_code)
    print(res.content.decode('utf-8')[:500])
except Exception as e:
    import traceback; traceback.print_exc()
