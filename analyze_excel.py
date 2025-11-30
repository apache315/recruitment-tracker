import pandas as pd
import os

file_path = "Luigi Recruitment-Tracker-Someka-Excel-Template-V9-Free-Version-2.xlsx"

if not os.path.exists(file_path):
    print(f"File not found: {file_path}")
    exit()

print(f"Analyzing {file_path} (Raw Mode)...")

try:
    xls = pd.ExcelFile(file_path, engine='openpyxl')
    
    sheets_to_analyze = ["Candidates", "JobOpenings", "Preferences"]

    for sheet in sheets_to_analyze:
        if sheet in xls.sheet_names:
            print(f"\n--- Sheet: {sheet} (First 10 rows raw) ---")
            df = pd.read_excel(xls, sheet_name=sheet, header=None, nrows=10)
            print(df)
        else:
            print(f"\n--- Sheet: {sheet} NOT FOUND ---")

except Exception as e:
    print(f"Error reading Excel file: {e}")
