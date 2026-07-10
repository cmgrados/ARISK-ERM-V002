import sys, json
import apps.financial_planning.views as v
from users.models import User
from django.test.client import RequestFactory

u = User.objects.first()
u.organization_id = 1
u.save()
factory = RequestFactory()
request = factory.get('/planificacion-financiera/plan/3/api/api_get_projected_balance_data/?scenario=OPTIMISTIC')
request.user = u

def line_tracer(frame, event, arg):
    if frame.f_code.co_name == 'api_get_projected_balance_data':
        if 'code' in frame.f_locals and frame.f_locals['code'] == '1401':
            if event == 'line':
                val = frame.f_locals.get('val', 'N/A')
                is_fixed = frame.f_locals.get('is_fixed')
                proj_cartera = frame.f_locals.get('proj_cartera')
                if proj_cartera: proj_cartera = proj_cartera[:1]
                print(f'Line {frame.f_lineno}: val={val}, is_fixed={is_fixed}, proj_cartera={proj_cartera}')
    return line_tracer

sys.settrace(line_tracer)
v.api_get_projected_balance_data(request, 3)
sys.settrace(None)
