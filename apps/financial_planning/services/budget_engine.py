from decimal import Decimal
from django.db import transaction
from ..models import (
    BudgetVersion, BudgetItem, BudgetCalculationRule,
    BudgetLine, BudgetLineDetail, SimulacionEscenario, ProyeccionMensual
)


# Mapa canónico de rubros presupuestales ligados al plan de cuentas real.
# Cada entrada define: code, name, category, account_prefix (para buscar en LiqBalanceDetail),
# y cómo proyectar: 'GROWTH_VARIABLE' = usar tasa de crecimiento de SimulacionEscenario,
#                   'INFLATION' = usar inflación del plan, 'MANUAL' = sin auto-cálculo.
DEFAULT_BUDGET_ITEMS = [
    {
        'code': 'ACC_4101',
        'name': 'Intereses y Gastos por Obligaciones Con Los Socios',
        'category': 'GAS_FIN',
        'account_prefix': '4101',
        'calc_type': 'TREND',
        'trend_variable': "dpf",
    },
    {
        'code': 'ACC_4102',
        'name': 'Intereses y Gastos por Fondos  Intercooperativos',
        'category': 'GAS_FIN',
        'account_prefix': '4102',
        'calc_type': 'TREND',
        'trend_variable': "dpf",
    },
    {
        'code': 'ACC_4103',
        'name': 'Intereses y Gastos por Depósitos de Coopac',
        'category': 'GAS_FIN',
        'account_prefix': '4103',
        'calc_type': 'TREND',
        'trend_variable': "dpf",
    },
    {
        'code': 'ACC_4104',
        'name': 'Intereses por Adeudos y Obligaciones Financieras',
        'category': 'GAS_FIN',
        'account_prefix': '4104',
        'calc_type': 'TREND',
        'trend_variable': "dpf",
    },
    {
        'code': 'ACC_4105',
        'name': 'Intereses de Cuentas por Pagar',
        'category': 'GAS_FIN',
        'account_prefix': '4105',
        'calc_type': 'TREND',
        'trend_variable': "dpf",
    },
    {
        'code': 'ACC_4106',
        'name': 'Intereses por Valores, Títulos  y  Obligaciones en Circulacion',
        'category': 'GAS_FIN',
        'account_prefix': '4106',
        'calc_type': 'TREND',
        'trend_variable': "dpf",
    },
    {
        'code': 'ACC_4107',
        'name': 'Comisiones y Otros Cargos por Obligaciones Financieras',
        'category': 'GAS_FIN',
        'account_prefix': '4107',
        'calc_type': 'TREND',
        'trend_variable': "dpf",
    },
    {
        'code': 'ACC_4108',
        'name': 'Diferencia de Cambio',
        'category': 'GAS_FIN',
        'account_prefix': '4108',
        'calc_type': 'TREND',
        'trend_variable': "dpf",
    },
    {
        'code': 'ACC_4109',
        'name': 'Cargas Financieras Diversas',
        'category': 'GAS_FIN',
        'account_prefix': '4109',
        'calc_type': 'TREND',
        'trend_variable': "dpf",
    },
    {
        'code': 'ACC_4201',
        'name': 'Gastos por Operaciones Contingentes',
        'category': 'GAS_SERV',
        'account_prefix': '4201',
        'calc_type': 'TREND',
        'trend_variable': "cartera",
    },
    {
        'code': 'ACC_4202',
        'name': 'Gastos por Servicios Financieros Diversos',
        'category': 'GAS_SERV',
        'account_prefix': '4202',
        'calc_type': 'TREND',
        'trend_variable': "cartera",
    },
    {
        'code': 'ACC_4301',
        'name': 'Pérdida por Deterioro de Inversiones',
        'category': 'PROV',
        'account_prefix': '4301',
        'calc_type': 'TREND',
        'trend_variable': "mora_soles",
    },
    {
        'code': 'ACC_4302',
        'name': 'Provisiones Para Incobrabilidad de Créditos',
        'category': 'PROV',
        'account_prefix': '4302',
        'calc_type': 'TREND',
        'trend_variable': "mora_soles",
    },
    {
        'code': 'ACC_4303',
        'name': 'Provisiones Para Incobrabilidad de Cuentas por Cobrar',
        'category': 'PROV',
        'account_prefix': '4303',
        'calc_type': 'TREND',
        'trend_variable': "mora_soles",
    },
    {
        'code': 'ACC_4304',
        'name': 'Provisiones  Para  Bienes Realizables, Recibidos  en  Pago y Adjudicados y Activos No Corrientes Mantenidos Para La Venta',
        'category': 'PROV',
        'account_prefix': '4304',
        'calc_type': 'TREND',
        'trend_variable': "mora_soles",
    },
    {
        'code': 'ACC_4305',
        'name': 'Provisiones Para Contingencias y Otras',
        'category': 'PROV',
        'account_prefix': '4305',
        'calc_type': 'TREND',
        'trend_variable': "mora_soles",
    },
    {
        'code': 'ACC_4401',
        'name': 'Depreciación de Inmuebles, Mobiliario y Equipo',
        'category': 'DEP_AMORT',
        'account_prefix': '4401',
        'calc_type': 'HISTORICAL',
        'trend_variable': None,
    },
    {
        'code': 'ACC_4403',
        'name': 'Amortización de Intangibles',
        'category': 'DEP_AMORT',
        'account_prefix': '4403',
        'calc_type': 'HISTORICAL',
        'trend_variable': None,
    },
    {
        'code': 'ACC_4404',
        'name': 'Deterioro de Valor de Inmuebles, Mobiliario y Equipo',
        'category': 'DEP_AMORT',
        'account_prefix': '4404',
        'calc_type': 'HISTORICAL',
        'trend_variable': None,
    },
    {
        'code': 'ACC_4405',
        'name': 'Deterioro de Valor de Activos Intangibles',
        'category': 'DEP_AMORT',
        'account_prefix': '4405',
        'calc_type': 'HISTORICAL',
        'trend_variable': None,
    },
    {
        'code': 'ACC_4501',
        'name': 'Gastos de Personal',
        'category': 'GAS_ADMIN',
        'account_prefix': '4501',
        'calc_type': 'TREND',
        'trend_variable': "socios",
    },
    {
        'code': 'ACC_4502',
        'name': 'Gastos de Directivos',
        'category': 'GAS_ADMIN',
        'account_prefix': '4502',
        'calc_type': 'HISTORICAL',
        'trend_variable': None,
    },
    {
        'code': 'ACC_4503',
        'name': 'Gastos por Servicios Recibidos de Terceros',
        'category': 'GAS_ADMIN',
        'account_prefix': '4503',
        'calc_type': 'TREND',
        'trend_variable': "cartera",
    },
    {
        'code': 'ACC_4504',
        'name': 'Tributos',
        'category': 'GAS_ADMIN',
        'account_prefix': '4504',
        'calc_type': 'HISTORICAL',
        'trend_variable': None,
    },
    {
        'code': 'ACC_4505',
        'name': 'Gastos de Actividades Asociativas',
        'category': 'GAS_ADMIN',
        'account_prefix': '4505',
        'calc_type': 'TREND',
        'trend_variable': "socios",
    },
    {
        'code': 'ACC_4601',
        'name': 'Pérdida en Venta de Inmuebles, Mobiliario y Equipo',
        'category': 'OTROS_EG',
        'account_prefix': '4601',
        'calc_type': 'HISTORICAL',
        'trend_variable': None,
    },
    {
        'code': 'ACC_4602',
        'name': 'Pérdida en Bienes Adjudicados y Recuperados',
        'category': 'OTROS_EG',
        'account_prefix': '4602',
        'calc_type': 'HISTORICAL',
        'trend_variable': None,
    },
    {
        'code': 'ACC_4604',
        'name': 'Pérdida en Venta de Activos No Corrientes Mantenidos Para La Venta',
        'category': 'OTROS_EG',
        'account_prefix': '4604',
        'calc_type': 'HISTORICAL',
        'trend_variable': None,
    },
    {
        'code': 'ACC_4605',
        'name': 'Sanciones Administrativas y Fiscales',
        'category': 'OTROS_EG',
        'account_prefix': '4605',
        'calc_type': 'HISTORICAL',
        'trend_variable': None,
    },
    {
        'code': 'ACC_4606',
        'name': 'Pérdidas No Cubiertas por Seguros',
        'category': 'OTROS_EG',
        'account_prefix': '4606',
        'calc_type': 'HISTORICAL',
        'trend_variable': None,
    },
    {
        'code': 'ACC_4607',
        'name': 'Donaciones Efectuadas',
        'category': 'OTROS_EG',
        'account_prefix': '4607',
        'calc_type': 'HISTORICAL',
        'trend_variable': None,
    },
    {
        'code': 'ACC_4609',
        'name': 'Otros Gastos',
        'category': 'OTROS_EG',
        'account_prefix': '4609',
        'calc_type': 'HISTORICAL',
        'trend_variable': None,
    },
    {
        'code': 'ACC_4901',
        'name': 'Costo de Ventas de Bienes',
        'category': 'OTROS_EG',
        'account_prefix': '4901',
        'calc_type': 'HISTORICAL',
        'trend_variable': None,
    },
    {
        'code': 'ACC_4902',
        'name': 'Costo de Ventas de Servicios',
        'category': 'OTROS_EG',
        'account_prefix': '4902',
        'calc_type': 'HISTORICAL',
        'trend_variable': None,
    },
    {
        'code': 'ACC_5101',
        'name': 'Intereses y Rendimientos por  Disponibles',
        'category': 'ING_FIN',
        'account_prefix': '5101',
        'calc_type': 'TREND',
        'trend_variable': "cartera",
    },
    {
        'code': 'ACC_5102',
        'name': 'Intereses y Rendimientos por Fondos Intercooperativos',
        'category': 'ING_FIN',
        'account_prefix': '5102',
        'calc_type': 'TREND',
        'trend_variable': "cartera",
    },
    {
        'code': 'ACC_5103',
        'name': 'Ingresos  por  Inversiones  Negociables y A Vencimiento',
        'category': 'ING_FIN',
        'account_prefix': '5103',
        'calc_type': 'TREND',
        'trend_variable': "cartera",
    },
    {
        'code': 'ACC_5104',
        'name': 'Intereses por Créditos',
        'category': 'ING_FIN',
        'account_prefix': '5104',
        'calc_type': 'TREND',
        'trend_variable': "rendimiento_cartera",
    },
    {
        'code': 'ACC_5105',
        'name': 'Ingresos de Cuentas por Cobrar',
        'category': 'ING_FIN',
        'account_prefix': '5105',
        'calc_type': 'TREND',
        'trend_variable': "cartera",
    },
    {
        'code': 'ACC_5107',
        'name': 'Comisiones y Otros Rendimientos por Creditos Directos',
        'category': 'ING_FIN',
        'account_prefix': '5107',
        'calc_type': 'TREND',
        'trend_variable': "cartera",
    },
    {
        'code': 'ACC_5108',
        'name': 'Diferencia de Cambio',
        'category': 'ING_FIN',
        'account_prefix': '5108',
        'calc_type': 'TREND',
        'trend_variable': "cartera",
    },
    {
        'code': 'ACC_5109',
        'name': 'Ingresos Financieros Diversos',
        'category': 'ING_FIN',
        'account_prefix': '5109',
        'calc_type': 'TREND',
        'trend_variable': "cartera",
    },
    {
        'code': 'ACC_5201',
        'name': 'Ingresos por Créditos Indirectos',
        'category': 'ING_SERV',
        'account_prefix': '5201',
        'calc_type': 'TREND',
        'trend_variable': "cartera",
    },
    {
        'code': 'ACC_5202',
        'name': 'Ingresos por Servicios Diversos',
        'category': 'ING_SERV',
        'account_prefix': '5202',
        'calc_type': 'TREND',
        'trend_variable': "cartera",
    },
    {
        'code': 'ACC_5203',
        'name': 'Ingresos por Arrendamientos',
        'category': 'ING_SERV',
        'account_prefix': '5203',
        'calc_type': 'TREND',
        'trend_variable': "cartera",
    },
    {
        'code': 'ACC_5301',
        'name': 'Reversión por Deterioro de Inversiones Negociables y A Vencimiento',
        'category': 'OTROS_ING',
        'account_prefix': '5301',
        'calc_type': 'HISTORICAL',
        'trend_variable': None,
    },
    {
        'code': 'ACC_5302',
        'name': 'Recuperación de Deterioro en Inmuebles, Mobiliario y Equipo',
        'category': 'OTROS_ING',
        'account_prefix': '5302',
        'calc_type': 'HISTORICAL',
        'trend_variable': None,
    },
    {
        'code': 'ACC_5303',
        'name': 'Recuperación de Deterioro de Activos Intangibles',
        'category': 'OTROS_ING',
        'account_prefix': '5303',
        'calc_type': 'HISTORICAL',
        'trend_variable': None,
    },
    {
        'code': 'ACC_5404',
        'name': 'Reversión de Provisiones por Créditos',
        'category': 'OTROS_ING',
        'account_prefix': '5404',
        'calc_type': 'HISTORICAL',
        'trend_variable': None,
    },
    {
        'code': 'ACC_5405',
        'name': 'Reversión de Provisiones por Cuentas por Cobrar',
        'category': 'OTROS_ING',
        'account_prefix': '5405',
        'calc_type': 'HISTORICAL',
        'trend_variable': None,
    },
    {
        'code': 'ACC_5406',
        'name': 'Reversión de Provisiones por Bienes Realizables, Recuperados y Recibidos en Pago y Adjudicados',
        'category': 'OTROS_ING',
        'account_prefix': '5406',
        'calc_type': 'HISTORICAL',
        'trend_variable': None,
    },
    {
        'code': 'ACC_5601',
        'name': 'Utilidad en Venta de Inmuebles, Mobiliario y Equipo',
        'category': 'OTROS_ING',
        'account_prefix': '5601',
        'calc_type': 'HISTORICAL',
        'trend_variable': None,
    },
    {
        'code': 'ACC_5602',
        'name': 'Utilidad en Venta de Bienes Adjudicados y Recuperados',
        'category': 'OTROS_ING',
        'account_prefix': '5602',
        'calc_type': 'HISTORICAL',
        'trend_variable': None,
    },
    {
        'code': 'ACC_5604',
        'name': 'Utilidad en Venta de Activos No Corrientes Mantenidos Para La Venta',
        'category': 'OTROS_ING',
        'account_prefix': '5604',
        'calc_type': 'HISTORICAL',
        'trend_variable': None,
    },
    {
        'code': 'ACC_5607',
        'name': 'Donaciones Recibidas Para Cobertura de Gastos',
        'category': 'OTROS_ING',
        'account_prefix': '5607',
        'calc_type': 'HISTORICAL',
        'trend_variable': None,
    },
    {
        'code': 'ACC_5609',
        'name': 'Otros Ingresos',
        'category': 'OTROS_ING',
        'account_prefix': '5609',
        'calc_type': 'HISTORICAL',
        'trend_variable': None,
    },
    {
        'code': 'ACC_5701',
        'name': 'Bienes',
        'category': 'OTROS_ING',
        'account_prefix': '5701',
        'calc_type': 'HISTORICAL',
        'trend_variable': None,
    },
    {
        'code': 'ACC_5702',
        'name': 'Servicios',
        'category': 'OTROS_ING',
        'account_prefix': '5702',
        'calc_type': 'HISTORICAL',
        'trend_variable': None,
    },
    {
        'code': 'ACC_5901',
        'name': 'Cargas Imputables',
        'category': 'OTROS_ING',
        'account_prefix': '5901',
        'calc_type': 'HISTORICAL',
        'trend_variable': None,
    },
]


class BudgetEngine:
    def __init__(self, plan, organization, user):
        self.plan = plan
        self.organization = organization
        self.user = user

    def get_or_create_draft_version(self, scenario='BASE'):
        version = BudgetVersion.objects.filter(
            plan_financiero=self.plan,
            organization=self.organization,
            status='DRAFT',
            scenario=scenario
        ).first()
        
        if not version:
            from django.db.models import Max
            max_v = BudgetVersion.objects.filter(
                plan_financiero=self.plan,
                organization=self.organization,
                scenario=scenario
            ).aggregate(Max('version_number'))['version_number__max'] or 0
            
            version = BudgetVersion.objects.create(
                plan_financiero=self.plan,
                organization=self.organization,
                status='DRAFT',
                scenario=scenario,
                version_number=max_v + 1,
                created_by=self.user
            )
        return version

    # ------------------------------------------------------------------
    # PRIVATE: read Dec-YYYY YTD balance from LiqBalanceDetail
    # ------------------------------------------------------------------
    def _get_historical_er_totals(self):
        """
        Returns a dict {account_prefix: annual_total} using the December
        balance (YTD/acumulado) from the historical year stored in the plan.
        Falls back to summing all months when December is missing.
        """
        from liquidity_risk.models import LiqBalanceDetail
        from django.db.models import Q, Sum, Max

        hist_data = self.plan.historical_data or {}
        selected_periods = hist_data.get('selected_periods', [])

        if selected_periods:
            years = sorted({p.split('-')[0] for p in selected_periods}, reverse=True)
            base_year = int(years[0])
        else:
            base_year = self.plan.anio_base - 1

        # Try to get the latest period of that year – which holds YTD for IS accounts
        latest_period = LiqBalanceDetail.objects.filter(
            period__year=base_year,
            upload__status='SUCCESS'
        ).aggregate(Max('period__month'))
        
        latest_month = latest_period.get('period__month__max')
        
        totals = {}
        if latest_month:
            dec_qs = LiqBalanceDetail.objects.filter(
                period__year=base_year,
                period__month=latest_month,
                upload__status='SUCCESS',
            ).filter(
                Q(account_code__startswith='4') | Q(account_code__startswith='5')
            ).values('account_code').annotate(total=Sum('balance'))

            for row in dec_qs:
                code = str(row['account_code'])
                bal = float(row['total'] or 0)
                # Income (5x) stored as negative in DB -> flip to positive
                if code.startswith('5'):
                    bal = abs(bal)
                # Expense (4x) stored as positive in DB already
                totals[code] = bal

        return totals

    def _resolve_historical_total(self, account_prefix, er_totals):
        """
        Given an account_prefix (e.g. '4501', '41', '51') sum all entries
        in er_totals whose key starts with that prefix.
        """
        return sum(v for k, v in er_totals.items() if k.startswith(account_prefix))

    # ------------------------------------------------------------------
    # PUBLIC: ensure default items exist (idempotent)
    # ------------------------------------------------------------------
    @transaction.atomic
    def _ensure_default_items(self):
        """Creates default BudgetItems and Rules if none exist for the organization."""
        # Clean up any dynamically generated items (e.g. from 12-digits experiment)
        valid_codes = [d['code'] for d in DEFAULT_BUDGET_ITEMS]
        BudgetItem.objects.filter(organization=self.organization).exclude(code__in=valid_codes).delete()

        for defn in DEFAULT_BUDGET_ITEMS:
            item, _ = BudgetItem.objects.get_or_create(
                organization=self.organization,
                code=defn['code'],
                defaults={
                    'name': defn['name'],
                    'category': defn['category'],
                }
            )
            # Update name/category if already exists
            if not _:
                BudgetItem.objects.filter(pk=item.pk).update(
                    name=defn['name'],
                    category=defn['category'],
                )

            BudgetCalculationRule.objects.update_or_create(
                organization=self.organization,
                item=item,
                defaults={
                    'calculation_type': defn.get('calc_type', 'HISTORICAL'),
                    'source_trend_variable': defn.get('trend_variable', None),
                    'assumption_driver': defn.get('account_prefix'),
                }
            )

    # ------------------------------------------------------------------
    # PUBLIC: sync_with_trends – the main projection engine
    # ------------------------------------------------------------------
    @transaction.atomic
    def sync_with_trends(self, scenario='BASE'):
        """
        Synchronizes the Budget with the Trend Analysis from Step 6.

        Algorithm:
          1. Read the historical E.R. totals (Dec YYYY YTD) from LiqBalanceDetail.
          2. For each BudgetItem with calc_type = TREND (GROWTH_VARIABLE):
             a. Find the matching SimulacionEscenario by `source_trend_variable`.
             b. Get the growth rate for the chosen scenario.
             c. Distribute the projected annual total across 12 months proportionally
                using the ProyeccionMensual values (which represent volumes/balances).
             d. Save BudgetLine + BudgetLineDetail rows.
          3. For MANUAL items, keep existing values (or initialize to 0).
          4. Compute Y2 and Y3 by compounding the base growth rate year over year.
        """
        self._ensure_default_items()
        version = self.get_or_create_draft_version(scenario)

        er_totals = self._get_historical_er_totals()

        items = BudgetItem.objects.filter(organization=self.organization)
        rules = {
            r.item_id: r
            for r in BudgetCalculationRule.objects.filter(organization=self.organization)
        }

        # Build a cache of SimulacionEscenario by variable_id
        sim_cache = {
            s.variable_id: s
            for s in SimulacionEscenario.objects.filter(
                plan=self.plan,
                organization=self.organization,
                agencia='Consolidado'
            )
        }

        # Build monthly projections cache: {variable_id: [val_m1, val_m2, ..., val_m12]}
        proj_cache = {}
        for sim in sim_cache.values():
            projs = list(
                ProyeccionMensual.objects
                    .filter(escenario=sim)
                    .order_by('mes_proyeccion')
                    .values('mes_proyeccion', 'valor_base', 'valor_pesimista', 'valor_optimista', 'valor_tendencia', 
                            'mc_valor_base', 'mc_valor_pesimista', 'mc_valor_optimista')
            )
            # First 12 months = Year 1
            if scenario == 'OPTIMISTIC':
                vals_y1 = [float(p['valor_optimista']) for p in projs[:12]]
                vals_y2 = [float(p['valor_optimista']) for p in projs[12:24]]
                vals_y3 = [float(p['valor_optimista']) for p in projs[24:36]]
            elif scenario == 'PESSIMISTIC':
                vals_y1 = [float(p['valor_pesimista']) for p in projs[:12]]
                vals_y2 = [float(p['valor_pesimista']) for p in projs[12:24]]
                vals_y3 = [float(p['valor_pesimista']) for p in projs[24:36]]
            elif scenario == 'MC_OPTIMISTIC':
                vals_y1 = [float(p['mc_valor_optimista'] or p['valor_optimista']) for p in projs[:12]]
                vals_y2 = [float(p['mc_valor_optimista'] or p['valor_optimista']) for p in projs[12:24]]
                vals_y3 = [float(p['mc_valor_optimista'] or p['valor_optimista']) for p in projs[24:36]]
            elif scenario == 'MC_PESSIMISTIC':
                vals_y1 = [float(p['mc_valor_pesimista'] or p['valor_pesimista']) for p in projs[:12]]
                vals_y2 = [float(p['mc_valor_pesimista'] or p['valor_pesimista']) for p in projs[12:24]]
                vals_y3 = [float(p['mc_valor_pesimista'] or p['valor_pesimista']) for p in projs[24:36]]
            elif scenario == 'MC_BASE':
                vals_y1 = [float(p['mc_valor_base'] or p['valor_base']) for p in projs[:12]]
                vals_y2 = [float(p['mc_valor_base'] or p['valor_base']) for p in projs[12:24]]
                vals_y3 = [float(p['mc_valor_base'] or p['valor_base']) for p in projs[24:36]]
            else:
                vals_y1 = [float(p['valor_base']) for p in projs[:12]]
                vals_y2 = [float(p['valor_base']) for p in projs[12:24]]
                vals_y3 = [float(p['valor_base']) for p in projs[24:36]]

            proj_cache[sim.variable_id] = {
                'y1': vals_y1,
                'y2': vals_y2,
                'y3': vals_y3,
                'base_annual': float(sim.tasa_base),   # growth % for compounding
            }

        for item in items:
            rule = rules.get(item.id)
            if not rule:
                continue

            calc_type = rule.calculation_type
            var_id = rule.source_trend_variable
            account_prefix = rule.assumption_driver  # stored in assumption_driver

            if calc_type == 'HISTORICAL' and var_id:
                account_prefix = var_id

            # Historical base amount for this item
            hist_annual = self._resolve_historical_total(account_prefix or '', er_totals)

            budget_line, _ = BudgetLine.objects.get_or_create(
                organization=self.organization,
                version=version,
                item=item,
                defaults={'applied_calculation_type': calc_type}
            )

            if calc_type == 'MANUAL':
                # Don't overwrite existing manual values; just ensure line exists
                if _:
                    budget_line.applied_calculation_type = 'MANUAL'
                    budget_line.save()
                continue
                
            if calc_type == 'HISTORICAL':
                # Distribute historical flatly for year 1, and grow for Y2 and Y3 based on overall portfolio trend
                default_growth = 0.0
                cartera_sim = sim_cache.get('cartera')
                if cartera_sim and cartera_sim.tasa_tendencia:
                    default_growth = float(cartera_sim.tasa_tendencia)
                else:
                    tasa_list = [float(s.tasa_tendencia) for s in sim_cache.values() if s.tasa_tendencia]
                    if tasa_list:
                        default_growth = sum(tasa_list) / len(tasa_list)

                monthly_val = hist_annual / 12 if hist_annual else Decimal('0')
                total_y1 = Decimal(str(round(hist_annual, 2)))
                self._save_monthly_details(budget_line, [monthly_val] * 12)
                budget_line.total_amount_y1 = total_y1
                
                y2_val = round(float(total_y1) * (1 + default_growth / 100.0), 2)
                y3_val = round(y2_val * (1 + default_growth / 100.0), 2)
                
                budget_line.total_amount_y2 = Decimal(str(y2_val))
                budget_line.total_amount_y3 = Decimal(str(y3_val))
                budget_line.applied_calculation_type = 'HISTORICAL'
                budget_line.save()
                continue

            if calc_type != 'TREND' or not var_id:
                continue

            if var_id == 'rendimiento_cartera':
                self._calculate_rendimiento_cartera(budget_line, scenario, hist_annual, proj_cache)
                continue

            if var_id in ['ahorros', 'dpf', 'ahorros_usd', 'dpf_usd']:
                self._calculate_ahorros_dpf(budget_line, scenario, hist_annual, proj_cache, var_id)
                continue

            proj = proj_cache.get(var_id)
            if not proj:
                # No trend data for this variable; apply default trend growth instead of flat
                default_growth = 0.0
                cartera_sim = sim_cache.get('cartera')
                if cartera_sim and cartera_sim.tasa_tendencia:
                    default_growth = float(cartera_sim.tasa_tendencia)
                else:
                    tasa_list = [float(s.tasa_tendencia) for s in sim_cache.values() if s.tasa_tendencia]
                    if tasa_list:
                        default_growth = sum(tasa_list) / len(tasa_list)

                monthly_val = hist_annual / 12 if hist_annual else Decimal('0')
                total_y1 = Decimal(str(round(hist_annual, 2)))
                self._save_monthly_details(budget_line, [monthly_val] * 12)
                budget_line.total_amount_y1 = total_y1
                
                y2_val = round(float(total_y1) * (1 + default_growth / 100.0), 2)
                y3_val = round(y2_val * (1 + default_growth / 100.0), 2)
                
                budget_line.total_amount_y2 = Decimal(str(y2_val))
                budget_line.total_amount_y3 = Decimal(str(y3_val))
                budget_line.applied_calculation_type = 'TREND'
                budget_line.save()
                continue

            # Compute Y1 monthly values using volume-proportional distribution
            # Growth rate for variable (annual %)
            base_growth = proj['base_annual']  # e.g. 6.95
            y1_vals_raw = proj['y1']
            y2_vals_raw = proj['y2']
            y3_vals_raw = proj['y3']

            # Sum of volumes for proportional distribution
            y1_sum = sum(y1_vals_raw) if y1_vals_raw else 0
            y2_sum = sum(y2_vals_raw) if y2_vals_raw else 0
            y3_sum = sum(y3_vals_raw) if y3_vals_raw else 0

            # Projected annual total = hist_annual * (1 + growth_rate/100)
            growth_factor_y1 = 1 + base_growth / 100
            # Use tasa_tendencia (multi-year trend) for Y2/Y3
            sim_obj = sim_cache.get(var_id)
            trend_growth = float(sim_obj.tasa_tendencia) if sim_obj else base_growth
            growth_factor_y2 = growth_factor_y1 * (1 + trend_growth / 100)
            growth_factor_y3 = growth_factor_y2 * (1 + trend_growth / 100)

            proj_y1_total = hist_annual * growth_factor_y1
            proj_y2_total = hist_annual * growth_factor_y2
            proj_y3_total = hist_annual * growth_factor_y3

            # Monthly values: distribute proportionally to monthly volumes
            def distribute(annual_total, monthly_vols):
                total_vol = sum(monthly_vols) if monthly_vols else 0
                if total_vol == 0 or annual_total == 0:
                    return [annual_total / 12] * 12
                return [(v / total_vol) * annual_total for v in monthly_vols]

            monthly_y1 = distribute(proj_y1_total, y1_vals_raw)

            self._save_monthly_details(budget_line, monthly_y1)

            budget_line.total_amount_y1 = Decimal(str(round(proj_y1_total, 2)))
            budget_line.total_amount_y2 = Decimal(str(round(proj_y2_total, 2)))
            budget_line.total_amount_y3 = Decimal(str(round(proj_y3_total, 2)))
            budget_line.applied_calculation_type = 'TREND'
            budget_line.save()

    def _calculate_rendimiento_cartera(self, budget_line, scenario, hist_annual, proj_cache):
        cartera_proj = proj_cache.get('cartera')
        if not cartera_proj:
            monthly_val = hist_annual / 12 if hist_annual else Decimal('0')
            self._save_monthly_details(budget_line, [monthly_val] * 12)
            budget_line.total_amount_y1 = Decimal(str(round(hist_annual, 2)))
            budget_line.total_amount_y2 = Decimal(str(round(hist_annual, 2)))
            budget_line.total_amount_y3 = Decimal(str(round(hist_annual, 2)))
            budget_line.applied_calculation_type = 'TREND'
            budget_line.save()
            return

        hist_data = self.plan.historical_data or {}
        assump = hist_data.get('institutional_assumptions', {})
        yield_params = assump.get('yieldParams', {}).get('cartera', {})

        y1_vals = cartera_proj.get('y1', [0])
        default_old_vigente = float(y1_vals[0]) if y1_vals else 0.0

        old_vigente = float(yield_params.get('#yield-old-vigente') or default_old_vigente)
        old_ingresos = float(yield_params.get('#yield-old-ingresos') or (hist_annual or 0.0))
        amort_rate = float(yield_params.get('#yield-amort-rate') or 5.0)
        pct_vigente = float(yield_params.get('#yield-pct-vigente') or 95.0)
        rate_new = float(yield_params.get('#yield-rate-new') or 32.0)

        rate_actual = (old_ingresos / old_vigente) * 100 if old_vigente > 0 else 0

        def get_separation(total_val, month_idx):
            vigente = (total_val or 0) * (pct_vigente / 100.0)
            current_old_vigente = old_vigente * ((1 - (amort_rate / 100.0)) ** month_idx)
            
            if vigente > current_old_vigente:
                old_port = current_old_vigente
                new_port = vigente - current_old_vigente
            else:
                old_port = vigente
                new_port = 0
                
            yield_old = old_port * (rate_actual / 100.0) / 12.0
            yield_new = new_port * (rate_new / 100.0) / 12.0
            
            return yield_old + yield_new

        y1_vals = cartera_proj['y1']
        y2_vals = cartera_proj['y2']
        y3_vals = cartera_proj['y3']

        monthly_y1 = []
        for i, val in enumerate(y1_vals):
            monthly_y1.append(Decimal(str(round(get_separation(val, i), 2))))
            
        y1_total = sum(monthly_y1)

        y2_total = 0
        for i, val in enumerate(y2_vals):
            y2_total += get_separation(val, 12 + i)
            
        y3_total = 0
        for i, val in enumerate(y3_vals):
            y3_total += get_separation(val, 24 + i)

        self._save_monthly_details(budget_line, monthly_y1)
        budget_line.total_amount_y1 = Decimal(str(round(y1_total, 2)))
        budget_line.total_amount_y2 = Decimal(str(round(y2_total, 2)))
        budget_line.total_amount_y3 = Decimal(str(round(y3_total, 2)))
        budget_line.applied_calculation_type = 'TREND'
        budget_line.save()

    def _calculate_ahorros_dpf(self, budget_line, scenario, hist_annual, proj_cache, var_id):
        proj = proj_cache.get(var_id)
        if not proj:
            monthly_val = hist_annual / 12 if hist_annual else Decimal('0')
            self._save_monthly_details(budget_line, [monthly_val] * 12)
            budget_line.total_amount_y1 = Decimal(str(round(hist_annual, 2)))
            budget_line.total_amount_y2 = Decimal(str(round(hist_annual, 2)))
            budget_line.total_amount_y3 = Decimal(str(round(hist_annual, 2)))
            budget_line.applied_calculation_type = 'TREND'
            budget_line.save()
            return

        hist_data = self.plan.historical_data or {}
        assump = hist_data.get('institutional_assumptions', {})
        cost_params = assump.get('costParams', {}).get(var_id, {})

        y1_vals = proj.get('y1', [0])
        default_old_vigente = float(y1_vals[0]) if y1_vals else 0.0

        old_vigente = float(cost_params.get('#cost-old-vigente') or default_old_vigente)
        old_gastos = float(cost_params.get('#cost-old-gastos') or (hist_annual or 0.0))
        amort_rate = float(cost_params.get('#cost-amort-rate') or 5.0)
        pct_vigente = float(cost_params.get('#cost-pct-vigente') or 100.0)
        
        # default new rate depends on var_id
        def_new_rate = 5.0 if 'ahorro' in var_id else 7.5
        rate_new = float(cost_params.get('#cost-rate-new') or def_new_rate)

        rate_actual = (old_gastos / old_vigente) * 100 if old_vigente > 0 else 0

        def get_separation(total_val, month_idx):
            vigente = (total_val or 0) * (pct_vigente / 100.0)
            current_old_vigente = old_vigente * ((1 - (amort_rate / 100.0)) ** month_idx)
            
            if vigente > current_old_vigente:
                old_port = current_old_vigente
                new_port = vigente - current_old_vigente
            else:
                old_port = vigente
                new_port = 0
                
            cost_old = old_port * (rate_actual / 100.0) / 12.0
            cost_new = new_port * (rate_new / 100.0) / 12.0
            
            return cost_old + cost_new

        y1_vals = proj['y1']
        y2_vals = proj['y2']
        y3_vals = proj['y3']

        monthly_y1 = []
        for i, val in enumerate(y1_vals):
            monthly_y1.append(Decimal(str(round(get_separation(val, i), 2))))
            
        y1_total = sum(monthly_y1)

        y2_total = 0
        for i, val in enumerate(y2_vals):
            y2_total += get_separation(val, 12 + i)
            
        y3_total = 0
        for i, val in enumerate(y3_vals):
            y3_total += get_separation(val, 24 + i)

        self._save_monthly_details(budget_line, monthly_y1)
        budget_line.total_amount_y1 = Decimal(str(round(y1_total, 2)))
        budget_line.total_amount_y2 = Decimal(str(round(y2_total, 2)))
        budget_line.total_amount_y3 = Decimal(str(round(y3_total, 2)))
        budget_line.applied_calculation_type = 'TREND'
        budget_line.save()


    # ------------------------------------------------------------------
    def _save_monthly_details(self, budget_line, monthly_values):
        """Saves/updates 12 monthly BudgetLineDetail rows."""
        for i, val in enumerate(monthly_values[:12], start=1):
            BudgetLineDetail.objects.update_or_create(
                organization=self.organization,
                budget_line=budget_line,
                period_type='MONTH',
                period_index=i,
                defaults={'amount': Decimal(str(round(val, 2)))}
            )
