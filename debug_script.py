import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from financial_planning.models import PlanFinanciero, BudgetItem

User = get_user_model()
try:
    user = User.objects.get(username='cmgrados')
    plan = PlanFinanciero.objects.get(id=3)
    print('User Org:', getattr(user, 'organization_id', 'NO ORG ATTR'))
    print('Plan Org:', getattr(plan, 'organization_id', 'NO ORG ATTR'))
    items = BudgetItem.objects.filter(organization_id=user.organization_id)
    print('Budget Items user org:', items.count())
    
    all_items = BudgetItem.objects.all()
    print('Total Budget Items:', all_items.count())
    for item in all_items:
        print(f"Item: {item.name}, Org: {item.organization_id}")
except Exception as e:
    import traceback
    traceback.print_exc()
