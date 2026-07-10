from django.test import RequestFactory
from apps.financial_planning.views import api_get_cash_flow_data
from apps.financial_planning.models import PlanFinanciero
from users.models import Organization
import json

try:
    plan = PlanFinanciero.objects.first()
    req = RequestFactory().get('/api/api_get_cash_flow_data/?scenario=BASE')
    req.user = type('User', (), {'organization': Organization.objects.first(), 'is_authenticated': True})()
    
    res = api_get_cash_flow_data(req, plan_id=plan.id)
    print('STATUS', res.status_code)
    data = json.loads(res.content)
    print(json.dumps(data, indent=2))
except Exception as e:
    import traceback
    traceback.print_exc()
