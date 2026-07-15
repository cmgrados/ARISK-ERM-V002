import os
import sys
import django

sys.path.append(r"c:\Users\USER\Desktop\ARISK V002")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import RequestFactory
from utilities.views import download_credit_template

rf = RequestFactory()
request = rf.get('/utilidades/descargar-plantilla/')

try:
    response = download_credit_template(request)
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {response.headers}")
    print(f"Content Length: {len(response.content)} bytes")
except Exception as e:
    import traceback
    traceback.print_exc()
