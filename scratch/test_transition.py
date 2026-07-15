import os
import django
import sys
import pandas as pd

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from credit_risk.models import CreditOperation

def test_transition():
    t1 = '2020-12-31'
    t2 = '2021-01-31'
    
    ops_t1 = CreditOperation.objects.filter(load_date=t1).values('operation_code', 'sbs_classification')
    ops_t2 = CreditOperation.objects.filter(load_date=t2).values('operation_code', 'sbs_classification')
    
    df_t1 = pd.DataFrame(ops_t1).rename(columns={'sbs_classification': 'T1'})
    df_t2 = pd.DataFrame(ops_t2).rename(columns={'sbs_classification': 'T2'})
    
    print(f"T1 count: {len(df_t1)}")
    print(f"T2 count: {len(df_t2)}")
    
    if not df_t1.empty and not df_t2.empty:
        # Normalize to match 'cats'
        df_t1['T1'] = df_t1['T1'].str.strip().str.title().replace({'Cpp': 'Con Problemas Potenciales', 'Prdida': 'Pérdida', 'Pérdida': 'Pérdida'})
        df_t2['T2'] = df_t2['T2'].str.strip().str.title().replace({'Cpp': 'Con Problemas Potenciales', 'Prdida': 'Pérdida', 'Pérdida': 'Pérdida'})
        
        df_merged = pd.merge(df_t1, df_t2, on='operation_code', how='inner')
        print(f"Merged count: {len(df_merged)}")
        
        cats = ['Normal', 'Con Problemas Potenciales', 'Deficiente', 'Dudoso', 'Pérdida']
        matrix = pd.crosstab(df_merged['T1'], df_merged['T2'], dropna=False)
        matrix = matrix.reindex(index=cats, columns=cats, fill_value=0)
        
        print("Matrix Absolute Values:")
        print(matrix)
        
        total = matrix.values.sum()
        print(f"Total entries in matrix: {total}")

if __name__ == "__main__":
    test_transition()
