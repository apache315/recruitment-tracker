import pandas as pd
import os

file_path = "Luigi Recruitment-Tracker-Someka-Excel-Template-V9-Free-Version-2.xlsx"

try:
    xls = pd.ExcelFile(file_path, engine='openpyxl')
    
    print("\n--- JobOpenings (First 20 rows raw) ---")
    df_jobs = pd.read_excel(xls, sheet_name="JobOpenings", header=None, nrows=20)
    print(df_jobs)

    print("\n--- Preferences (First 20 rows raw) ---")
    df_prefs = pd.read_excel(xls, sheet_name="Preferences", header=None, nrows=20)
    print(df_prefs)

except Exception as e:
    print(f"Error: {e}")
