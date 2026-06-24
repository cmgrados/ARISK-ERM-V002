from django.core.management.base import BaseCommand
from financial_planning.views import api_available_historical_dates
from django.test import RequestFactory
import json

class Command(BaseCommand):
    def handle(self, *args, **options):
        req = RequestFactory().get('/api/available_historical_dates/')
        req.user = type('User', (), {'organization': None, 'is_authenticated': True})()
        res = api_available_historical_dates(req)
        print(json.dumps(json.loads(res.content), indent=2))
