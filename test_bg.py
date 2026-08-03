import os, django, json
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.test import RequestFactory
from financial_planning.views import api_get_projected_balance_data
from django.contrib.auth import get_user_model
CustomUser = get_user_model()

request = RequestFactory().get('/planificacion-financiera/plan/3/api/projected-balance/?scenario=BASE')
request.user = CustomUser.objects.first()

response = api_get_projected_balance_data(request, 3)
data = json.loads(response.content)
accounts = data['accounts']
# I need a way to get proj_cartera, it's not in the response payload.
# I'll just look at what the backend does.


for acc in accounts:
    if acc['code'] in ['14', '1401', '1405', '1409']:
        print(f"{acc['code']}: Base={acc['base']}, Ene={acc['m1_12'][0]}")

base_14 = sum(acc['base'] for acc in accounts if acc['code'].startswith('14') and not any(other['code'].startswith(acc['code']) and other['code'] != acc['code'] for other in accounts))
base_1405 = sum(acc['base'] for acc in accounts if acc['code'].startswith('1405') and not any(other['code'].startswith(acc['code']) and other['code'] != acc['code'] for other in accounts))
base_1409 = sum(acc['base'] for acc in accounts if acc['code'].startswith('1409') and not any(other['code'].startswith(acc['code']) and other['code'] != acc['code'] for other in accounts))
print("base_cartera calculated =", base_14 - base_1405 - base_1409)
