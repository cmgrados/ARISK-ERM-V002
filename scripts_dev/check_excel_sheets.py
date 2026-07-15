import pandas as pd
import os

file_path = 'c:/Users/VICTUS/Desktop/A.RISK ERM/data_prueba_liquidez_2026.xlsx'
if os.path.exists(file_path):
    xl = pd.ExcelFile(file_path)
    print(f"Sheets in {file_path}:")
    for sheet in xl.sheet_names:
        df = xl.parse(sheet)
        print(f" - {sheet}: {len(df)} rows, columns: {list(df.columns[:5])}...")
else:
    print(f"File {file_path} not found.")
