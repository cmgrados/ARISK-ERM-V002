import os
import sys
import django
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from credit_risk.models import CarteraCreditoCarga
import pandas as pd
import io

start_time = time.time()
print("Starting query...")
qs = CarteraCreditoCarga.objects.all()

cols = ['N', 'NCL', 'FNAC', 'GEN', 'EC', 'EMP', 'CSOC', 'PR', 'TID', 'NID', 'TPER', 'DOM', 'RCO', 'CAL', 'CALINT', 'CAGE', 'MON', 'CCR', 'TCR', 'STCR', 'FOT', 'MORG', 'TEA', 'SKCR', 'CC', 'KVI', 'KRE', 'KRF', 'KVE', 'KJU', 'KCO', 'CCO', 'DAK', 'SGP', 'SGA', 'PVR', 'PCI', 'SCC', 'CCC', 'SIN', 'SIS', 'SID', 'TPR', 'NCPR', 'NCPA', 'PCUO', 'DGR', 'FVGO', 'FVGA', 'SSC', 'SSG', 'SCR', 'SKCO', 'SCOR', 'SINC', 'SCS']

records = qs.values_list(
    'n', 'ncl', 'fnac', 'gen', 'ec', 'emp', 'csoc', 'pr', 'tid', 'nid', 'tper', 'dom', 'rco', 'cal', 'calint', 'cage', 'mon', 'ccr', 'tcr', 'stcr', 'fot', 'morg', 'tea', 'skcr', 'cc', 'kvi', 'kre', 'krf', 'kve', 'kju', 'kco', 'cco', 'dak', 'sgp', 'sga', 'pvr', 'pci', 'scc', 'ccc', 'sin', 'sis', 'sid', 'tpr', 'ncpr', 'ncpa', 'pcuo', 'dgr', 'fvgo', 'fvga', 'ssc', 'ssg', 'scr', 'skco', 'scor', 'sinc', 'scs'
)

print(f"Query prep took {time.time() - start_time:.2f} seconds")
t1 = time.time()
df = pd.DataFrame.from_records(records, columns=cols)
print(f"DataFrame prep took {time.time() - t1:.2f} seconds. Shape: {df.shape}")

t2 = time.time()
output = io.BytesIO()
with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
    df.to_excel(writer, index=False, sheet_name='Cartera_Creditos')
print(f"Excel creation took {time.time() - t2:.2f} seconds")

print(f"Total time: {time.time() - start_time:.2f} seconds")
