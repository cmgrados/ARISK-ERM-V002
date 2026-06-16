import json
from django.test import RequestFactory
from django.contrib.auth import get_user_model
from apps.strategic_risk.api_views import PortafolioPOAViewSet

User = get_user_model()
user = User.objects.first() # get any user with an organization
factory = RequestFactory()
data = {
    'anio': '2026',
    'nombre_proyecto': 'Prueba test',
    'descripcion': 'cascasdcas',
    'presupuesto': '5000',
    'estrategia': 1, # replace with valid ID if needed, 
    'lider_proyecto': ''
}
request = factory.post('/api/portafolio-poa/', data=json.dumps(data), content_type='application/json')
request.user = user

view = PortafolioPOAViewSet.as_view({'post': 'create'})
try:
    response = view(request)
    print("Status:", response.status_code)
    print("Data:", response.data)
except Exception as e:
    import traceback
    traceback.print_exc()
