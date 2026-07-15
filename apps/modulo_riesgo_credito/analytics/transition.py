import pandas as pd
from django.db.models import F

def calculate_transition_matrix(date_t_minus_1, date_t, filters=None):
    """
    Calcula la matriz de transición entre el mes T-1 y el mes T.
    Utiliza pandas.crosstab para comparar la clasificación SBS o Buckets.
    Devuelve porcentajes, montos y análisis automatizado.
    """
    from credit_risk.models import CreditOperation
    import numpy as np
    
    if filters is None:
        filters = {}
    
    # Map SBS classification from DB (e.g., '0'->'NORMAL', etc)
    def normalize_sbs_local(val):
        if not val: return 'NORMAL'
        v = str(val).strip().upper()
        if 'PERDIDA' in v or 'PÉRDIDA' in v or 'PRDIDA' in v or v == '4': return 'PÉRDIDA'
        if 'CPP' in v or 'PROBLEMAS' in v or v == '1': return 'CPP'
        if 'DUDOSO' in v or v == '3': return 'DUDOSO'
        if 'DEFICIENTE' in v or v == '2': return 'DEFICIENTE'
        return 'NORMAL'
    
    # Extraer datos de T-1
    data_t1 = list(CreditOperation.objects.filter(
        load_date=date_t_minus_1, **filters
    ).values('operation_code', 'sbs_classification'))
    
    # Extraer datos de T
    data_t = list(CreditOperation.objects.filter(
        load_date=date_t, **filters
    ).values('operation_code', 'sbs_classification', 'balance'))
    
    df_t1 = pd.DataFrame(data_t1)
    df_t = pd.DataFrame(data_t)
    
    if df_t1.empty or df_t.empty:
        return None
        
    df_t1['bucket_t1'] = df_t1['sbs_classification'].apply(normalize_sbs_local)
    df_t['bucket_t'] = df_t['sbs_classification'].apply(normalize_sbs_local)
    df_t['balance'] = pd.to_numeric(df_t['balance'], errors='coerce').fillna(0).astype(float)
    
    # Orden de las categorías SBS
    cat_order = ['NORMAL', 'CPP', 'DEFICIENTE', 'DUDOSO', 'PÉRDIDA']
    
    # Merge por operación
    df_merged = pd.merge(df_t1, df_t, on='operation_code', how='inner')
    
    matrix_percent_df = pd.crosstab(df_merged['bucket_t1'], df_merged['bucket_t'], normalize='index')
    matrix_balance_df = pd.crosstab(df_merged['bucket_t1'], df_merged['bucket_t'], values=df_merged['balance'], aggfunc='sum').fillna(0)
    
    matrix_data = {}
    analysis_text = []
    
    for from_bucket in cat_order:
        matrix_data[from_bucket] = {}
        for to_bucket in cat_order:
            pct = 0.0
            bal = 0.0
            if from_bucket in matrix_percent_df.index and to_bucket in matrix_percent_df.columns:
                pct = float(round(matrix_percent_df.loc[from_bucket, to_bucket] * 100, 2))
                bal = float(round(matrix_balance_df.loc[from_bucket, to_bucket], 2))
            
            matrix_data[from_bucket][to_bucket] = {
                'pct': pct,
                'bal': bal
            }
            
        # Generar análisis de reclasificación SBS
        if from_bucket in matrix_percent_df.index:
            row_pct = matrix_percent_df.loc[from_bucket]
            row_bal = matrix_balance_df.loc[from_bucket]
            
            # Encontrar la mayor migración hacia una categoría PEOR (downgrade)
            idx_from = cat_order.index(from_bucket)
            worst_migs = {}
            pd_value = 0.0
            pd_bal = 0.0
            
            for to_b in row_pct.index:
                if to_b in cat_order:
                    idx_to = cat_order.index(to_b)
                    
                    # Guardar el PD (migración a PÉRDIDA)
                    if to_b == 'PÉRDIDA' and from_bucket != 'PÉRDIDA':
                        pd_value = row_pct[to_b] * 100
                        pd_bal = row_bal[to_b]
                        
                    if idx_to > idx_from and row_pct[to_b] > 0:
                        worst_migs[to_b] = {'pct': row_pct[to_b]*100, 'bal': row_bal[to_b]}
            
            if worst_migs:
                top_mig = max(worst_migs.items(), key=lambda x: x[1]['pct'])
                # Solo mencionar si no es a pérdida (porque a pérdida es el PD que analizaremos aparte)
                if top_mig[0] != 'PÉRDIDA':
                    analysis_text.append(f"Desde la clasificación <strong>{from_bucket}</strong>, se observa una reclasificación (deterioro) hacia <strong>{top_mig[0]}</strong> que afecta a S/ {top_mig[1]['bal']:,.2f} ({top_mig[1]['pct']:.2f}% de la categoría).")
                
            # Análisis de Probabilidad de Default (PD)
            if pd_value > 0:
                severity = "alta y preocupante" if pd_value >= 10.0 else "moderada" if pd_value >= 2.0 else "baja y controlada"
                analysis_text.append(f"El vector de <strong>Probabilidad de Default (PD)</strong> para créditos en <strong>{from_bucket}</strong> es de <strong>{pd_value:.2f}%</strong> (migración directa a Pérdida), lo cual representa un riesgo de default de {severity} que compromete S/ {pd_bal:,.2f} en saldos.")
                
    if not analysis_text:
        analysis_text.append("No se detectaron deterioros significativos (downgrades) ni riesgo inminente de default (PD) en las clasificaciones SBS durante este periodo evaluado.")

    return {
        'matrix': matrix_data,
        'analysis': analysis_text,
        'cat_order': cat_order
    }

def calculate_roll_rates_matrix(date_t_minus_1, date_t, filters=None):
    """
    Calcula la matriz de Roll Rates entre el mes T-1 y el mes T
    basado en los días de atraso (days_past_due).
    Devuelve porcentajes, montos y análisis automatizado.
    """
    from credit_risk.models import CreditOperation
    import numpy as np
    
    if filters is None:
        filters = {}

    def get_bucket(days):
        if pd.isna(days) or days <= 0: return '0 días'
        if days <= 30: return '1-30 días'
        if days <= 60: return '31-60 días'
        if days <= 90: return '61-90 días'
        if days <= 120: return '91-120 días'
        return '+120 días'
    
    bucket_order = ['0 días', '1-30 días', '31-60 días', '61-90 días', '91-120 días', '+120 días']
    
    data_t1 = list(CreditOperation.objects.filter(
        load_date=date_t_minus_1, **filters
    ).values('operation_code', 'days_past_due'))
    
    data_t = list(CreditOperation.objects.filter(
        load_date=date_t, **filters
    ).values('operation_code', 'days_past_due', 'balance'))
    
    df_t1 = pd.DataFrame(data_t1)
    df_t = pd.DataFrame(data_t)
    
    if df_t1.empty or df_t.empty:
        return None
        
    df_t1['bucket_t1'] = df_t1['days_past_due'].apply(get_bucket)
    df_t['bucket_t'] = df_t['days_past_due'].apply(get_bucket)
    df_t['balance'] = pd.to_numeric(df_t['balance'], errors='coerce').fillna(0).astype(float)
    
    bucket_order = ['0 días', '1-30 días', '31-60 días', '61-90 días', '+90 días']
    
    df_merged = pd.merge(df_t1, df_t, on='operation_code', how='inner')
    
    matrix_percent_df = pd.crosstab(df_merged['bucket_t1'], df_merged['bucket_t'], normalize='index')
    matrix_balance_df = pd.crosstab(df_merged['bucket_t1'], df_merged['bucket_t'], values=df_merged['balance'], aggfunc='sum').fillna(0)
    
    matrix_data = {}
    analysis_text = []
    
    for from_bucket in bucket_order:
        matrix_data[from_bucket] = {}
        for to_bucket in bucket_order:
            pct = 0.0
            bal = 0.0
            if from_bucket in matrix_percent_df.index and to_bucket in matrix_percent_df.columns:
                pct = float(round(matrix_percent_df.loc[from_bucket, to_bucket] * 100, 2))
                bal = float(round(matrix_balance_df.loc[from_bucket, to_bucket], 2))
            
            matrix_data[from_bucket][to_bucket] = {
                'pct': pct,
                'bal': bal
            }
            
        # Generar análisis
        if from_bucket in matrix_percent_df.index:
            row_pct = matrix_percent_df.loc[from_bucket]
            row_bal = matrix_balance_df.loc[from_bucket]
            
            # Encontrar la mayor migración hacia un bucket PEOR
            idx_from = bucket_order.index(from_bucket)
            worst_migs = {}
            for to_b in row_pct.index:
                if to_b in bucket_order:
                    idx_to = bucket_order.index(to_b)
                    if idx_to > idx_from and row_pct[to_b] > 0:
                        worst_migs[to_b] = {'pct': row_pct[to_b]*100, 'bal': row_bal[to_b]}
            
            if worst_migs:
                top_mig = max(worst_migs.items(), key=lambda x: x[1]['pct'])
                analysis_text.append(f"Desde el tramo <strong>{from_bucket}</strong>, se observa un deterioro operativo o 'roll' hacia <strong>{top_mig[0]}</strong> que afecta a S/ {top_mig[1]['bal']:,.2f} ({top_mig[1]['pct']:.2f}% del tramo).")
                
    if not analysis_text:
        analysis_text.append("No se detectaron deterioros significativos (rollove) hacia tramos de mayor mora en este periodo evaluado. La cartera muestra una alta tasa de contención o mejora.")

    return {
        'matrix': matrix_data,
        'analysis': analysis_text,
        'bucket_order': bucket_order
    }
