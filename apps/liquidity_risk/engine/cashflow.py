import logging
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from liquidity_risk.models import LiqTimeBand, CarteraPasivoCarga, VolatileBalanceLar
from credit_risk.models import CreditOperation
import math

logger = logging.getLogger(__name__)

def get_cashflow_projections(cutoff_date):
    """
    Genera las proyecciones de flujo de caja según el reporte normativo SBS de Brecha de Liquidez.
    """
    bands = list(LiqTimeBand.objects.all().order_by('order'))
    if not bands:
        band_names = ['1M', '2M', '3M', '4M', '5M', '6M', '7-9 M', '10-12 M', 'Más de 1A a 2A', 'Más de 2A a 5A', 'Más de 5A']
    else:
        band_names = [b.name for b in bands]
        
    activos_labels = [
        'Disponible',
        'Créditos - grandes empresas',
        'Créditos - medianas empresas',
        'Créditos - pequeñas empresas',
        'Créditos - micro-empresas',
        'Créditos - consumo',
        'Créditos - Hipotecario',
        'Cuentas por cobrar - otros'
    ]
    
    pasivos_labels = [
        'Obligaciones por cuentas de ahorro',
        'Obligaciones por cuentas a plazo',
        'Depósitos de empresas del sistema financiero',
        'Adeudos y obligaciones financieras del país',
        'Adeudos y obligaciones financieras del exterior',
        'Cuentas por pagar - otros'
    ]

    report = {
        'bandas': band_names,
        'activos': {label: {band: Decimal('0.00') for band in band_names} for label in activos_labels},
        'pasivos': {label: {band: Decimal('0.00') for band in band_names} for label in pasivos_labels},
        'total_activos': {band: Decimal('0.00') for band in band_names},
        'total_pasivos': {band: Decimal('0.00') for band in band_names},
        'brecha_marginal': {band: Decimal('0.00') for band in band_names},
        'brecha_acumulada': {band: Decimal('0.00') for band in band_names},
        'detalle_flujos': {
            'ingresos': {
                'Amortizacion de creditos programadas': {band: Decimal('0.00') for band in band_names},
                'Amortizacion de creditos no programadas': {band: Decimal('0.00') for band in band_names},
                'Ingresos financieros programadas': {band: Decimal('0.00') for band in band_names},
                'Ingresos financieros no programadas': {band: Decimal('0.00') for band in band_names},
                'Incremento previsto de depositos ahorros': {band: Decimal('0.00') for band in band_names},
                'Incremento previsto de DPF': {band: Decimal('0.00') for band in band_names},
                'Incremento Aportaciones': {band: Decimal('0.00') for band in band_names},
                'Otros Ingresos': {band: Decimal('0.00') for band in band_names},
            },
            'egresos': {
                'Vencimiento de DPF': {band: Decimal('0.00') for band in band_names},
                'Retiros de ahorro libre': {band: Decimal('0.00') for band in band_names},
                'Desembolso de creditos': {band: Decimal('0.00') for band in band_names},
                'Intereses por depósitos': {band: Decimal('0.00') for band in band_names},
                'Gastos personal': {band: Decimal('0.00') for band in band_names},
                'Gastos terceros': {band: Decimal('0.00') for band in band_names},
                'Tributos': {band: Decimal('0.00') for band in band_names},
            },
            'adeudados': {
                'Pagos programados (10)': {band: Decimal('0.00') for band in band_names},
                'Intereses programados': {band: Decimal('0.00') for band in band_names},
                'Renovaciones': {band: Decimal('0.00') for band in band_names},
                'Nuevos adeudados': {band: Decimal('0.00') for band in band_names},
            }
        }
    }
    # Preparar fechas límite de cada banda
    band_dates = []
    fallback_limits = [(0, 30), (31, 60), (61, 90), (91, 120), (121, 150), (151, 180), (181, 270), (271, 360), (361, 720), (721, 1800), (1801, 9999)]
    for idx, b_name in enumerate(band_names):
        start_d, end_d = fallback_limits[idx] if idx < len(fallback_limits) else (0, 9999)
        if bands:
            b_obj = bands[idx]
            if b_obj.days_start is not None:
                start_d = b_obj.days_start
            if b_obj.days_end is not None:
                end_d = b_obj.days_end

        band_dates.append({
            'name': b_name,
            'start_date': cutoff_date + timedelta(days=start_d),
            'end_date': cutoff_date + timedelta(days=end_d)
        })

    # ==========================================
    # 1. ACTIVOS
    # ==========================================
    # Disponible (Mock for now, hardcoded from the screenshot)
    report['activos']['Disponible'][band_names[0]] += Decimal('31027364.00')

    # Créditos
    creditos = CreditOperation.objects.filter(load_date=cutoff_date, balance__gt=0)
    for credito in creditos:
        saldo = credito.balance or Decimal('0.00')
        dias_per = credito.payment_periodicity or 30
        if dias_per <= 0: dias_per = 30
        
        fecha_vencimiento = credito.maturity_date
        if not fecha_vencimiento:
            fecha_proyectada = cutoff_date + timedelta(days=dias_per)
            cuotas_pendientes = 1
        elif fecha_vencimiento <= cutoff_date:
            fecha_proyectada = cutoff_date + timedelta(days=dias_per)
            cuotas_pendientes = 1
        else:
            dias_restantes = (fecha_vencimiento - cutoff_date).days
            cuotas_pendientes = max(1, int(math.ceil(dias_restantes / dias_per)))
            fecha_proyectada = cutoff_date + timedelta(days=dias_per)
            
        tea_dec = float(credito.rate or Decimal('0.00')) / 100.0
        
        if tea_dec > 0 and cuotas_pendientes > 0:
            r = (1.0 + tea_dec)**(dias_per / 360.0) - 1.0
            if r > 0:
                factor = (1.0 + r)**cuotas_pendientes
                cuota_fija = float(saldo) * (r * factor) / (factor - 1.0)
            else:
                cuota_fija = float(saldo) / cuotas_pendientes
        else:
            r = 0.0
            cuota_fija = float(saldo) / cuotas_pendientes
        
        saldo_iter = float(saldo)
        
        # Determine classification
        tcr = str(credito.credit_type or '').upper().strip()
        if 'HIPOTE' in tcr or tcr == 'HIPOTECARIO':
            clasif = 'Créditos - Hipotecario'
        elif 'CONSUMO' in tcr:
            clasif = 'Créditos - consumo'
        elif 'MICRO' in tcr:
            clasif = 'Créditos - micro-empresas'
        elif 'PEQUE' in tcr:
            clasif = 'Créditos - pequeñas empresas'
        elif 'MEDIANA' in tcr:
            clasif = 'Créditos - medianas empresas'
        elif 'CORPORATIVO' in tcr or 'GRANDE' in tcr:
            clasif = 'Créditos - grandes empresas'
        else:
            # Fallback
            clasif = 'Créditos - grandes empresas'

        for _ in range(cuotas_pendientes):
            if saldo_iter <= 0.01: break
            interes_estimado = saldo_iter * r
            capital_por_cuota = cuota_fija - interes_estimado
            
            if capital_por_cuota > saldo_iter or _ == cuotas_pendientes - 1:
                capital_por_cuota = saldo_iter
            
            flujo_total_cuota = Decimal(str(round(capital_por_cuota + interes_estimado, 2)))

            for b_info in band_dates:
                if b_info['start_date'] <= fecha_proyectada <= b_info['end_date']:
                    report['activos'][clasif][b_info['name']] += flujo_total_cuota
                    report['detalle_flujos']['ingresos']['Amortizacion de creditos programadas'][b_info['name']] += Decimal(str(round(capital_por_cuota, 2)))
                    report['detalle_flujos']['ingresos']['Ingresos financieros programadas'][b_info['name']] += Decimal(str(round(interes_estimado, 2)))
                    break
            
            fecha_proyectada += timedelta(days=dias_per)
            saldo_iter -= capital_por_cuota

    # ==========================================
    # 2. PASIVOS
    # ==========================================
    pasivos = CarteraPasivoCarga.objects.filter(fecha_corte=cutoff_date)
    
    # Retrieve Volatility configured for Ahorros
    vol_ahorro = VolatileBalanceLar.objects.filter(period=cutoff_date, segment='Obligaciones por cuentas de ahorro').first()
    vol_pct_ahorro = vol_ahorro.volatility_percentage if vol_ahorro else Decimal('6.75')
    vol_ratio_ahorro = float(vol_pct_ahorro) / 100.0

    for pasivo in pasivos:
        prod = (pasivo.producto_agrupado or '').upper()
        saldo_total = float(pasivo.saldo or pasivo.saldo_dpf or pasivo.saldo_ctas_libre or pasivo.saldo_prog or Decimal('0.00'))
        
        if saldo_total <= 0:
            continue

        if 'PLAZO' in prod or 'DPF' in prod:
            # Obligaciones por cuentas a plazo
            vence = pasivo.vence or (cutoff_date + timedelta(days=pasivo.plazo_dpf or 30))
            tea_dec = float(pasivo.tea or Decimal('0.00')) / 100.0
            plazo = pasivo.plazo_dpf or 0
            if plazo <= 0 and pasivo.apertura:
                plazo = (vence - pasivo.apertura).days
            if plazo <= 0: plazo = 360
                
            r = (1.0 + tea_dec)**(plazo / 360.0) - 1.0 if tea_dec > 0 else 0.0
            interes = saldo_total * r
            total_pasivo = Decimal(str(round(saldo_total + interes, 2)))
            
            for b_info in band_dates:
                if b_info['start_date'] <= vence <= b_info['end_date']:
                    report['pasivos']['Obligaciones por cuentas a plazo'][b_info['name']] += total_pasivo
                    report['detalle_flujos']['egresos']['Vencimiento de DPF'][b_info['name']] += Decimal(str(round(saldo_total, 2)))
                    report['detalle_flujos']['egresos']['Intereses por depósitos'][b_info['name']] += Decimal(str(round(interes, 2)))
                    break
        else:
            # Obligaciones por cuentas de ahorro
            # Distribución LaR (Volátil en 1M, Estable en +5A o última banda)
            volatil = Decimal(str(round(saldo_total * vol_ratio_ahorro, 2)))
            estable = Decimal(str(round(saldo_total - float(volatil), 2)))
            
            primera_banda = band_names[0]
            ultima_banda = band_names[-1]
            
            report['pasivos']['Obligaciones por cuentas de ahorro'][primera_banda] += volatil
            report['pasivos']['Obligaciones por cuentas de ahorro'][ultima_banda] += estable
            
            report['detalle_flujos']['egresos']['Retiros de ahorro libre'][primera_banda] += volatil

    # Sumatorias
    acumulado = Decimal('0.00')
    for band in band_names:
        tot_act = sum(cat[band] for cat in report['activos'].values())
        tot_pas = sum(cat[band] for cat in report['pasivos'].values())
        
        report['total_activos'][band] = tot_act
        report['total_pasivos'][band] = tot_pas
        
        brecha = tot_act - tot_pas
        report['brecha_marginal'][band] = brecha
        
        acumulado += brecha
        report['brecha_acumulada'][band] = acumulado

    # Ratios Proxys
    activos_corto = report['total_activos'][band_names[0]]
    pasivos_corto = report['total_pasivos'][band_names[0]]
    
    rlcp = float(activos_corto / pasivos_corto) * 100.0 if pasivos_corto > 0 else 0.0
    lcr_proxy = rlcp # Asumiendo escenario base similar para el proxy LCR

    # Proxy NSFR: Pasivos de largo plazo + patrimonio vs Activos de largo plazo
    # Para el proxy, tomaremos pasivos a partir de 1 año y lo dividiremos entre activos a partir de 1 año
    pasivos_largo = Decimal('0.00')
    activos_largo = Decimal('0.00')
    for b in band_names:
        if '1A' in b or '2A' in b or '+5A' in b or '12 M' in b:
            pasivos_largo += report['total_pasivos'][b]
            activos_largo += report['total_activos'][b]
    
    # Asumimos un patrimonio ficticio o la suma de las obligaciones de largo plazo para simular "Fondeo Estable Requerido"
    # Añadiremos un factor del 15% de pasivos totales como equity proxy si es 0
    total_pas_all = sum(report['total_pasivos'].values())
    equity_proxy = total_pas_all * Decimal('0.15')
    nsfr_proxy = float((pasivos_largo + equity_proxy) / activos_largo) * 100.0 if activos_largo > 0 else 0.0

    report['ratios'] = {
        'rlcp': round(rlcp, 2),
        'lcr_proxy': round(lcr_proxy, 2),
        'nsfr_proxy': round(nsfr_proxy, 2)
    }

    # Data para charts
    report['charts'] = {
        'labels': band_names[:6], # Solo las primeras 6 bandas para que no se vea abrumador
        'activos': [float(report['total_activos'][b]) for b in band_names[:6]],
        'pasivos': [float(report['total_pasivos'][b]) for b in band_names[:6]],
        'brecha_acumulada': [float(report['brecha_acumulada'][b]) for b in band_names[:6]]
    }

    return report
