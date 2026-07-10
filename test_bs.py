import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.financial_planning.models import PlanFinanciero, SimulacionEscenario, ProyeccionMensual, BudgetVersion, BudgetLine, BudgetLineDetail
from liquidity_risk.models import LiqBalanceDetail
from django.db.models import Sum

plan = PlanFinanciero.objects.first()
if not plan:
    print("No plan found")
    exit()

print(f"Plan: {plan.nombre}")

# 1. Historical Balances
selected_periods = plan.historical_data.get('selected_periods', []) if plan.historical_data else []
years = sorted({p.split('-')[0] for p in selected_periods}, reverse=True)
base_year = int(years[0]) if years else (plan.anio_base - 1)

dec_qs = LiqBalanceDetail.objects.filter(
    period__year=base_year,
    period__month=12,
    upload__status='SUCCESS',
).values('account_code', 'balance')

totals = {}
for row in dec_qs:
    code = str(row['account_code'])
    bal = float(row['balance'])
    # Pasivo/Patrimonio are negative, Activo positive. We will keep them absolute here, and assign sign later
    totals[code] = abs(bal)

def get_sum(prefix, exclude_prefix=None):
    s = 0
    for k, v in totals.items():
        if k.startswith(prefix):
            if exclude_prefix and k.startswith(exclude_prefix):
                continue
            s += v
    return s

base_cartera = get_sum('14', exclude_prefix='149')
base_prov = get_sum('149')
base_cxc = get_sum('16')
base_af = get_sum('18')
base_otros_act = get_sum('1') - (base_cartera + base_prov + base_cxc + base_af)

base_ahorros = get_sum('211')
base_dpf = get_sum('212')
base_adeudos = get_sum('24')
base_otros_pas = get_sum('2') - (base_ahorros + base_dpf + base_adeudos)

base_cap_social = get_sum('31')
base_reservas = get_sum('32')
base_res_acum = get_sum('33')
base_otros_pat = get_sum('3') - (base_cap_social + base_reservas + base_res_acum)

print("--- Base ---")
print(f"Cartera: {base_cartera}, Prov: {base_prov}, Ahorros: {base_ahorros}, DPF: {base_dpf}")
