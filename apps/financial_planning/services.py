from django.db.models import Sum
from datetime import date
from django.db import transaction
from catalogs.models import OrganizationalUnit
from credit_risk.models import CreditOperation
from liquidity_risk.models import LiqLiabilityDetail
from .models import FinancialPlan, ProjectedMonthlyData, ProductCatalog

def initialize_plan_base_month(plan_id, period_date):
    """
    Extrae los saldos reales de los módulos auxiliares (Cartera y Pasivos)
    y puebla el Mes 0 (Mes base) del Plan Financiero por Agencia y Producto.
    """
    plan = FinancialPlan.objects.get(id=plan_id)
    
    # 1. Extracción de Cartera (Credit Risk)
    credit_qs = CreditOperation.objects.filter(load_date=period_date)
    # Agrupamos por agencia y tipo de crédito
    credit_aggr = credit_qs.values('agency', 'credit_type').annotate(
        total_balance=Sum('balance'),
        total_provisions=Sum('required_provision')
    )
    
    # 2. Extracción de Depósitos (Liquidity Risk)
    # Asumimos que funding_type es "AHORRO" o "PLAZO"
    liability_qs = LiqLiabilityDetail.objects.filter(period=period_date)
    liability_aggr = liability_qs.values('agency', 'funding_type').annotate(
        total_balance=Sum('balance')
    )
    
    # Diccionario temporal: (agencia, producto_id) -> {'portfolio': 0, 'deposits': 0, 'provisions': 0}
    agencies_data = {}
    
    with transaction.atomic():
        # Limpiar proyecciones previas del mismo mes base
        ProjectedMonthlyData.objects.filter(plan=plan, month=period_date).delete()
        
        # Procesar Cartera
        for row in credit_aggr:
            agency_name = str(row['agency']).strip().upper() if row['agency'] else 'S/N'
            credit_type = str(row['credit_type']).strip().upper() if row['credit_type'] else 'CARTERA COMERCIAL'
            
            # Registrar/obtener el producto
            product, _ = ProductCatalog.objects.get_or_create(
                name=credit_type,
                defaults={'category': 'ASSET', 'credit_type': credit_type}
            )
            
            key = (agency_name, product.id)
            if key not in agencies_data:
                agencies_data[key] = {'portfolio': 0, 'deposits': 0, 'provisions': 0}
                
            agencies_data[key]['portfolio'] += (row['total_balance'] or 0)
            agencies_data[key]['provisions'] += (row['total_provisions'] or 0)
            
        # Procesar Pasivos
        for row in liability_aggr:
            agency_name = str(row['agency']).strip().upper() if row['agency'] else 'S/N'
            funding_type = str(row['funding_type']).strip().upper() if row['funding_type'] else 'DEPÓSITOS'
            
            # Registrar/obtener el producto de captacion
            product, _ = ProductCatalog.objects.get_or_create(
                name=f"PASIVO - {funding_type}",
                defaults={'category': 'LIABILITY', 'credit_type': ''}
            )
            
            key = (agency_name, product.id)
            if key not in agencies_data:
                agencies_data[key] = {'portfolio': 0, 'deposits': 0, 'provisions': 0}
                
            agencies_data[key]['deposits'] += (row['total_balance'] or 0)

        records_created = 0
        
        # Si no hay datos, crear un registro base por defecto para permitir que el motor funcione
        if not agencies_data:
            agencies_data[('AGENCIA PRINCIPAL', 1)] = {'portfolio': 0, 'deposits': 0, 'provisions': 0}
            # Asegurar que exista un producto por defecto
            ProductCatalog.objects.get_or_create(id=1, defaults={'name': 'DEFAULT', 'category': 'ASSET'})
            
        for (agency_str, product_id), data in agencies_data.items():
            unit = OrganizationalUnit.objects.filter(name__iexact=agency_str, is_agency=True).first()
            if not unit:
                unit, _ = OrganizationalUnit.objects.get_or_create(
                    name=agency_str,
                    defaults={'is_agency': True, 'description': 'Auto-generada por ETL'}
                )
                
            ProjectedMonthlyData.objects.create(
                plan=plan,
                unit=unit,
                product_id=product_id,
                month=period_date,
                portfolio_balance=data['portfolio'],
                deposits_balance=data['deposits'],
                provisions_expense=data['provisions'],
                financial_income=0,
                financial_expense=0,
                operating_expense=0,
                net_remanent=0
            )
            records_created += 1
            
    return True, f"Mes base ({period_date.strftime('%Y-%m')}) inicializado exitosamente. {records_created} registros (agencia/producto) creados."

def generate_projections(plan_id, months_to_project):
    """
    Genera las proyecciones financieras para N meses iterando desde el Mes 0,
    a nivel de Agencia y Producto.
    """
    try:
        months_to_project = int(months_to_project)
        if months_to_project < 1 or months_to_project > 60:
            return False, "El número de meses a proyectar debe estar entre 1 y 60."
    except ValueError:
        return False, "Número de meses inválido."
        
    plan = FinancialPlan.objects.get(id=plan_id)
    
    # 1. Obtener el Mes 0 (base) para cada agencia x producto
    base_data_qs = ProjectedMonthlyData.objects.filter(plan=plan).order_by('month')
    if not base_data_qs.exists():
        return False, "No existe un Mes 0 para este plan. Ejecute primero la inicialización (ETL)."
        
    first_month = None
    for item in base_data_qs:
        if first_month is None or item.month < first_month:
            first_month = item.month
            
    # base dict: (unit_id, product_id) -> item
    base_dict = {}
    for item in base_data_qs.filter(month=first_month):
        base_dict[(item.unit_id, item.product_id)] = item
        
    from dateutil.relativedelta import relativedelta
    from decimal import Decimal

    # Precargar supuestos (globales)
    macro = getattr(plan, 'macro_assumptions', None)
    inflation_rate = (macro.inflation_rate / Decimal('100.0')) if macro else Decimal('0.0')

    # Diccionarios de supuestos por (Agencia, Producto)
    portfolio_assumps = {(pa.unit_id, pa.product_id): pa for pa in plan.portfolio_assumptions.all()}
    rate_assumps = {(ra.unit_id, ra.product_id): ra for ra in plan.rate_assumptions.all()}
    risk_assumps = {(r.unit_id, r.product_id): r for r in plan.risk_assumptions.all()}
    
    # Operativos por Agencia
    op_assumps = {oa.unit_id: oa for oa in plan.operating_assumptions.all()}

    records_created = 0
    with transaction.atomic():
        ProjectedMonthlyData.objects.filter(plan=plan, month__gt=first_month).delete()
        
        # Iterar sobre las líneas base
        for (unit_id, product_id), base_item in base_dict.items():
            port = portfolio_assumps.get((unit_id, product_id))
            rate = rate_assumps.get((unit_id, product_id))
            risk = risk_assumps.get((unit_id, product_id))
            oper = op_assumps.get(unit_id)
            
            # Es activo o pasivo?
            is_asset = False
            if base_item.product and base_item.product.category == 'ASSET':
                is_asset = True
                
            monthly_portfolio_growth = Decimal('0.0')
            monthly_deposit_growth = Decimal('0.0')
            
            if port:
                if is_asset:
                    monthly_portfolio_growth = (port.growth_goal / Decimal('12.0'))
                else:
                    monthly_deposit_growth = (port.growth_goal / Decimal('12.0'))
                    
            effective_rate_annual = rate.effective_rate if rate else Decimal('0.0')
            effective_rate_monthly = effective_rate_annual / Decimal('100.0') / Decimal('12.0')
            
            provision_rate_annual = risk.provision_rate_avg if risk else Decimal('0.0')
            provision_rate_monthly = provision_rate_annual / Decimal('100.0') / Decimal('12.0')
            
            # Gastos operativos (solo lo calculamos 1 vez por agencia, si hay múltiples productos lo repartimos? 
            # O mejor se asocia al producto nulo? Para simplificar, lo asociaremos iterativamente, pero OJO:
            # Si una agencia tiene 5 productos, sumar su OP base a cada uno multiplica los gastos.
            # Mejor dividir el gasto operativo inicial entre la cantidad de productos de la agencia en el mes 0,
            # o aplicar el OP solo si el saldo es mayor a 0 y distribuirlo proporcionalmente?
            # En la versión simplificada, asignamos OP equitativamente o mantenemos el base de la iteración.
            
            fixed_costs_monthly = (oper.fixed_costs / Decimal('12.0')) if oper else Decimal('0.0')
            
            # Variables iteración
            current_portfolio = base_item.portfolio_balance
            current_deposits = base_item.deposits_balance
            current_op_expense = base_item.operating_expense
            
            current_date = first_month
            
            for m in range(1, months_to_project + 1):
                current_date = current_date + relativedelta(months=1)
                
                # Dynamic growth from trend_analysis_data if step6 is locked
                locked_steps = plan.locked_steps or {}
                if locked_steps.get('step6') and plan.trend_analysis_data:
                    payload = plan.trend_analysis_data.get('full_payload', {})
                    datasets = payload.get('datasets_by_agency', {})
                    # Find agency name for current unit
                    agency_name = base_item.unit.name.upper() if base_item.unit else 'S/N'
                    agency_data = datasets.get(agency_name, {})
                    variables = agency_data.get('variables', [])
                    
                    if is_asset:
                        var_data = next((v for v in variables if v.get('id') == 'cartera'), None)
                        if var_data:
                            trend_arr = var_data.get('mc_data', {}).get('base') or var_data.get('base', [])
                            if len(trend_arr) > m and trend_arr[m-1]:
                                factor = Decimal(str(trend_arr[m])) / Decimal(str(trend_arr[m-1]))
                                current_portfolio = current_portfolio * factor
                            else:
                                current_portfolio += monthly_portfolio_growth
                    else:
                        var_data = next((v for v in variables if v.get('id') == 'depositos'), None)
                        if var_data:
                            trend_arr = var_data.get('mc_data', {}).get('base') or var_data.get('base', [])
                            if len(trend_arr) > m and trend_arr[m-1]:
                                factor = Decimal(str(trend_arr[m])) / Decimal(str(trend_arr[m-1]))
                                current_deposits = current_deposits * factor
                            else:
                                current_deposits += monthly_deposit_growth
                else:
                    current_portfolio += monthly_portfolio_growth
                    current_deposits += monthly_deposit_growth
                
                financial_income = Decimal('0.0')
                financial_expense = Decimal('0.0')
                
                budget_data = plan.budget_data or {}
                account_assumptions = budget_data.get('account_assumptions', {})
                cost_params = account_assumptions.get('costParams', {})
                yield_params = account_assumptions.get('yieldParams', {})
                
                if is_asset:
                    params = yield_params.get('cartera')
                    if params:
                        old_vigente = float(params.get('#yield-old-vigente', 0))
                        old_ingresos = float(params.get('#yield-old-ingresos', 0))
                        amort_rate = float(params.get('#yield-amort-rate', 0))
                        pct_vigente = float(params.get('#yield-pct-vigente', 100))
                        rate_new = float(params.get('#yield-rate-new', 0))
                        rate_actual = (old_ingresos / old_vigente) * 100 if old_vigente > 0 else 0
                        
                        vigente = float(current_portfolio or 0) * (pct_vigente / 100.0)
                        current_old_vigente = old_vigente * ((1.0 - amort_rate / 100.0) ** (m - 1))
                        
                        if vigente > current_old_vigente:
                            old_port = current_old_vigente
                            new_port = vigente - current_old_vigente
                        else:
                            old_port = vigente
                            new_port = 0
                            
                        cost_old = old_port * (rate_actual / 100.0) / 12.0
                        cost_new = new_port * (rate_new / 100.0) / 12.0
                        financial_income = Decimal(str(cost_old + cost_new))
                    else:
                        financial_income = current_portfolio * effective_rate_monthly
                else:
                    if 'AHORRO' in (base_item.product.name.upper() if base_item.product else ''):
                        var_id = 'ahorros_cte'
                    elif 'PLAZO' in (base_item.product.name.upper() if base_item.product else ''):
                        var_id = 'dpf'
                    else:
                        var_id = 'depositos'
                        
                    params = cost_params.get(var_id)
                    if params:
                        old_vigente = float(params.get('#cost-old-vigente', 0))
                        old_gastos = float(params.get('#cost-old-gastos', 0))
                        amort_rate = float(params.get('#cost-amort-rate', 0))
                        pct_vigente = float(params.get('#cost-pct-vigente', 100))
                        rate_new = float(params.get('#cost-rate-new', 0))
                        rate_actual = (old_gastos / old_vigente) * 100 if old_vigente > 0 else 0
                        
                        vigente = float(current_deposits or 0) * (pct_vigente / 100.0)
                        current_old_vigente = old_vigente * ((1.0 - amort_rate / 100.0) ** (m - 1))
                        
                        if vigente > current_old_vigente:
                            old_port = current_old_vigente
                            new_port = vigente - current_old_vigente
                        else:
                            old_port = vigente
                            new_port = 0
                            
                        cost_old = old_port * (rate_actual / 100.0) / 12.0
                        cost_new = new_port * (rate_new / 100.0) / 12.0
                        financial_expense = Decimal(str(cost_old + cost_new))
                    else:
                        financial_expense = current_deposits * effective_rate_monthly
                    
                # Dynamic provision rate from trend_analysis_data (mora variable)
                if locked_steps.get('step6') and plan.trend_analysis_data:
                    payload = plan.trend_analysis_data.get('full_payload', {})
                    datasets = payload.get('datasets_by_agency', {})
                    agency_name = base_item.unit.name.upper() if base_item.unit else 'S/N'
                    agency_data = datasets.get(agency_name, {})
                    variables = agency_data.get('variables', [])
                    
                    var_mora = next((v for v in variables if v.get('id') == 'mora'), None)
                    if var_mora:
                        trend_arr = var_mora.get('mc_data', {}).get('base') or var_mora.get('base', [])
                        if len(trend_arr) > m:
                            mora_rate = Decimal(str(trend_arr[m]))
                            # Assuming mora is annualized percentage
                            provision_rate_monthly = mora_rate / Decimal('100.0') / Decimal('12.0')

                provisions_expense = current_portfolio * provision_rate_monthly
                
                inflated_base_op = current_op_expense * (Decimal('1.0') + (inflation_rate / Decimal('12.0')))
                projected_op_expense = inflated_base_op + fixed_costs_monthly
                # Ojo, fixed_costs se suman cada mes? Sí, si es un costo fijo mensual.
                
                current_op_expense = inflated_base_op
                
                net_remanent = financial_income - financial_expense - provisions_expense - projected_op_expense
                
                ProjectedMonthlyData.objects.create(
                    plan=plan,
                    unit_id=unit_id,
                    product_id=product_id,
                    month=current_date,
                    portfolio_balance=current_portfolio,
                    deposits_balance=current_deposits,
                    financial_income=financial_income,
                    financial_expense=financial_expense,
                    provisions_expense=provisions_expense,
                    operating_expense=projected_op_expense,
                    net_remanent=net_remanent
                )
                records_created += 1

    return True, f"Proyección generada exitosamente por {months_to_project} meses. {records_created} registros de producto creados."
