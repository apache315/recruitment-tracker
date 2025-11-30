"""
Migration Script: Local Excel -> Google Sheets
Uploads data from the local Excel file to a new Google Sheet
"""

import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import sys

EXCEL_FILE = "Luigi Recruitment-Tracker-Someka-Excel-Template-V9-Free-Version-2.xlsx"
CREDENTIALS_FILE = "credentials.json"
SPREADSHEET_NAME = "https://docs.google.com/spreadsheets/d/1477Q9GMKGSzMlWp6ao7YSt0CYXOsVPx87K8rbDdCfVM/edit?gid=0#gid=0"

def migrate():
    print("Starting migration to Google Sheets...")
    
    # 1. Check files
    if not os.path.exists(EXCEL_FILE):
        print(f"Excel file '{EXCEL_FILE}' not found.")
        return
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"Credentials file '{CREDENTIALS_FILE}' not found.")
        print("   Please download 'credentials.json' from Google Cloud Console.")
        return

    # 2. Connect to Google Sheets
    print("Connecting to Google Sheets API...")
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
        client = gspread.authorize(creds)
    except Exception as e:
        print(f"Connection failed: {e}")
        return

    # 3. Open Spreadsheet (by URL or name)
    try:
        if SPREADSHEET_NAME.startswith("https://"):
            sh = client.open_by_url(SPREADSHEET_NAME)
            print(f"Opened spreadsheet by URL")
        else:
            sh = client.open(SPREADSHEET_NAME)
            print(f"Found existing spreadsheet: '{SPREADSHEET_NAME}'")
    except gspread.SpreadsheetNotFound:
        print(f"Creating new spreadsheet: '{SPREADSHEET_NAME}'...")
        try:
            sh = client.create(SPREADSHEET_NAME)
            print(f"Spreadsheet created! URL: {sh.url}")
            print("IMPORTANT: Share this sheet with your personal email to view it.")
            print(f"   Service Account Email: {creds.service_account_email}")
        except Exception as e:
            print(f"Failed to create spreadsheet: {e}")
            return

    # 4. Read Local Excel Data
    print("Reading local Excel file...")
    try:
        # Helper function to find header row (from data_manager.py logic)
        def find_header_row(df, target_column):
            for i, row in df.head(20).iterrows():
                row_values = [str(val).strip().upper() for val in row.values]
                if target_column in row_values:
                    return i
            return None
        
        # Read raw data to preserve structure
        xls = pd.ExcelFile(EXCEL_FILE, engine='openpyxl')
        
        # --- MIGRATE CANDIDATES ---
        if "Candidates" in xls.sheet_names:
            print("   Processing 'Candidates' sheet...")
            # First, find the header row
            df_raw = pd.read_excel(xls, sheet_name="Candidates", header=None, nrows=20)
            header_row = find_header_row(df_raw, "CANDIDATE NAME")
            
            if header_row is not None:
                # Read again with correct header
                df_candidates = pd.read_excel(xls, sheet_name="Candidates", header=header_row)
                # Remove unnamed columns
                df_candidates = df_candidates.loc[:, ~df_candidates.columns.str.contains('^Unnamed')]
                # Remove empty rows
                df_candidates = df_candidates.dropna(subset=["CANDIDATE NAME"])
                
                try:
                    ws_cand = sh.worksheet("Candidates")
                    ws_cand.clear()
                except gspread.WorksheetNotFound:
                    ws_cand = sh.add_worksheet(title="Candidates", rows=1000, cols=20)
                
                # Convert all values to strings but preserve headers
                headers = df_candidates.columns.tolist()
                df_candidates_str = df_candidates.astype(str)
                df_candidates_str = df_candidates_str.replace('nan', '')
                df_candidates_str = df_candidates_str.replace('NaT', '')
                
                # Upload headers + data
                all_data = [headers] + df_candidates_str.values.tolist()
                ws_cand.update(all_data)
                print("   Candidates uploaded.")

        # --- MIGRATE JOB OPENINGS ---
        if "JobOpenings" in xls.sheet_names:
            print("   Processing 'JobOpenings' sheet...")
            # Find header row
            df_raw = pd.read_excel(xls, sheet_name="JobOpenings", header=None, nrows=20)
            header_row = find_header_row(df_raw, "JOB ID")
            
            if header_row is not None:
                # Read with correct header
                df_jobs = pd.read_excel(xls, sheet_name="JobOpenings", header=header_row)
                df_jobs = df_jobs.loc[:, ~df_jobs.columns.str.contains('^Unnamed')]
                df_jobs = df_jobs.dropna(subset=["JOB ID"])
                
                try:
                    ws_jobs = sh.worksheet("JobOpenings")
                    ws_jobs.clear()
                except gspread.WorksheetNotFound:
                    ws_jobs = sh.add_worksheet(title="JobOpenings", rows=1000, cols=20)
                
                # Convert to strings but preserve headers
                headers = df_jobs.columns.tolist()
                df_jobs_str = df_jobs.astype(str)
                df_jobs_str = df_jobs_str.replace('nan', '')
                df_jobs_str = df_jobs_str.replace('NaT', '')
                
                # Upload headers + data
                all_data = [headers] + df_jobs_str.values.tolist()
                ws_jobs.update(all_data)
                print("   JobOpenings uploaded.")

        # --- MIGRATE PREFERENCES ---
        if "Preferences" in xls.sheet_names:
            print("   Processing 'Preferences' sheet...")
            df_prefs = pd.read_excel(xls, sheet_name="Preferences", header=None)
            
            try:
                ws_prefs = sh.worksheet("Preferences")
                ws_prefs.clear()
            except gspread.WorksheetNotFound:
                ws_prefs = sh.add_worksheet(title="Preferences", rows=100, cols=20)
            
            df_prefs = df_prefs.fillna("")
            ws_prefs.update(df_prefs.values.tolist())
            print("   Preferences uploaded.")
            
        print("\nMIGRATION COMPLETE!")
        print(f"   Access your data here: {sh.url}")
        
    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()
