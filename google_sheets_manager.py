import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import time
import os
import json
import streamlit as st

class GoogleSheetManager:
    def __init__(self, credentials_file, spreadsheet_name):
        self.credentials_file = credentials_file
        self.spreadsheet_name = spreadsheet_name
        self.client = None
        self.spreadsheet = None
        self.candidates_df = pd.DataFrame()
        self.jobs_df = pd.DataFrame()
        self.preferences = {}
        self.last_load_time = 0
        self.is_connected = False
        
    def connect(self):
        """Connects to Google Sheets API"""
        # Try to load credentials from Streamlit secrets first (for cloud deployment)
        try:
            if hasattr(st, 'secrets') and 'gcp_service_account' in st.secrets:
                # Running on Streamlit Cloud - use secrets
                credentials_dict = dict(st.secrets["gcp_service_account"])
                scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
                creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
                self.client = gspread.authorize(creds)
            elif os.path.exists(self.credentials_file):
                # Running locally - use credentials file
                scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
                creds = ServiceAccountCredentials.from_json_keyfile_name(self.credentials_file, scope)
                self.client = gspread.authorize(creds)
            else:
                return False, f"File credenziali '{self.credentials_file}' non trovato e nessun secret configurato."
                
            try:
                if self.spreadsheet_name.startswith("https://"):
                    self.spreadsheet = self.client.open_by_url(self.spreadsheet_name)
                else:
                    self.spreadsheet = self.client.open(self.spreadsheet_name)
                
                self.is_connected = True
                return True, "Connesso a Google Sheets con successo."
            except gspread.SpreadsheetNotFound:
                return False, f"Foglio Google '{self.spreadsheet_name}' non trovato. Assicurati di averlo condiviso con l'email del bot."
            except gspread.exceptions.APIError as e:
                if "403" in str(e) and "Drive API" in str(e):
                    return False, "Errore: Google Drive API non abilitata. Usa l'URL del foglio invece del nome."
                return False, f"Errore API Google: {e}"
                
        except Exception as e:
            return False, f"Errore di connessione: {e}"

    def load_data(self):
        """Loads data from Google Sheets"""
        if not self.is_connected:
            success, msg = self.connect()
            if not success:
                return False, msg

        try:
            # 1. Load Candidates
            try:
                ws_candidates = self.spreadsheet.worksheet("Candidates")
                # Use get_all_values to avoid header duplicate issues
                all_values = ws_candidates.get_all_values()
                if len(all_values) > 1:
                    # First row is headers, rest is data
                    headers = all_values[0]
                    data = all_values[1:]
                    self.candidates_df = pd.DataFrame(data, columns=headers)
                    # Remove completely empty rows
                    self.candidates_df = self.candidates_df.replace('', pd.NA).dropna(how='all')
                    
                    # Apply column mapping (from data_manager.py)
                    column_mapping = {
                        "RECRUITMENT PHASE\n(Pipeline)": "STATUS",
                        "JOB APPLIED FOR": "POSITION",
                        "APPLIED DATE": "APPLICATION DATE",
                        "RECIEVED APPLICATION COMMENTS": "RECEIVED APPLICATION COMMENTS"
                    }
                    self.candidates_df = self.candidates_df.rename(columns=column_mapping)
                    
                    # Convert data types (all values are strings from GSheets)
                    # Convert date columns
                    date_columns = ["APPLICATION DATE", "APPLIED DATE"]
                    for col in date_columns:
                        if col in self.candidates_df.columns:
                            self.candidates_df[col] = pd.to_datetime(self.candidates_df[col], errors='coerce')
                else:
                    self.candidates_df = pd.DataFrame()
                    
            except gspread.WorksheetNotFound:
                self.candidates_df = pd.DataFrame()

            # 2. Load Job Openings
            try:
                ws_jobs = self.spreadsheet.worksheet("JobOpenings")
                all_values = ws_jobs.get_all_values()
                if len(all_values) > 1:
                    headers = all_values[0]
                    data = all_values[1:]
                    self.jobs_df = pd.DataFrame(data, columns=headers)
                    self.jobs_df = self.jobs_df.replace('', pd.NA).dropna(how='all')
                    
                    # Convert data types
                    # Convert date columns
                    date_columns = ["OPENING DATE", "NEW HIRE START DATE"]
                    for col in date_columns:
                        if col in self.jobs_df.columns:
                            self.jobs_df[col] = pd.to_datetime(self.jobs_df[col], errors='coerce')
                    
                    # Convert numeric columns
                    if "HIRING COST" in self.jobs_df.columns:
                        self.jobs_df["HIRING COST"] = pd.to_numeric(self.jobs_df["HIRING COST"], errors='coerce')
                else:
                    self.jobs_df = pd.DataFrame()
            except gspread.WorksheetNotFound:
                self.jobs_df = pd.DataFrame()

            # 3. Load Preferences
            self.preferences = {
                "Status": [],
                "Recruiters": [],
                "Sources": [],
                "Positions": [],
                "Departments": [],
                "Decision Comments": [],
                "Job Statuses": ["Vacant", "Filled", "Suspended", "Cancelled"]
            }
            
            try:
                ws_prefs = self.spreadsheet.worksheet("Preferences")
                # This is trickier as preferences structure is custom
                # We might need a simpler structure for GSheets or parse it similarly
                # Or we read the whole sheet and parse
                prefs_values = ws_prefs.get_all_values()
                df_prefs = pd.DataFrame(prefs_values)
                
                # Extract logic similar to Excel... 
                # For now, let's implement a simplified version or rely on defaults
                # Ideally, we should restructure Preferences in GSheets to be more database-like
                
                # Extract Recruiters (col C, index 2)
                if len(df_prefs.columns) > 2:
                    self.preferences["Recruiters"] = [x for x in df_prefs.iloc[7:, 2].tolist() if x and x.strip()]
                
                # Extract Status (col L, index 11)
                if len(df_prefs.columns) > 11:
                    self.preferences["Status"] = [x for x in df_prefs.iloc[7:, 11].tolist() if x and x.strip()]
                    
            except gspread.WorksheetNotFound:
                pass

            # Extract derived lists
            if not self.jobs_df.empty and "DEPARTMENT" in self.jobs_df.columns:
                self.preferences["Departments"] = self.jobs_df["DEPARTMENT"].dropna().unique().tolist()
            
            if not self.jobs_df.empty and "JOB TITLE" in self.jobs_df.columns:
                self.preferences["Positions"] = self.jobs_df["JOB TITLE"].dropna().unique().tolist()
                
            if not self.candidates_df.empty and "SOURCE" in self.candidates_df.columns:
                current_sources = self.candidates_df["SOURCE"].dropna().unique().tolist()
                self.preferences["Sources"] = list(set(self.preferences.get("Sources", []) + current_sources))

            self.last_load_time = time.time()
            return True, "Dati caricati da Google Sheets."

        except Exception as e:
            return False, f"Errore caricamento dati GSheets: {e}"

    def save_candidate(self, candidate_dict):
        """Appends a new candidate"""
        if not self.is_connected:
            self.connect()
            
        try:
            ws = self.spreadsheet.worksheet("Candidates")
            # Get headers to ensure order
            headers = ws.row_values(1)
            
            row_to_append = []
            for header in headers:
                row_to_append.append(candidate_dict.get(header, ""))
                
            ws.append_row(row_to_append)
            self.load_data() # Refresh
            return True, "Candidato salvato su Google Sheets!"
        except Exception as e:
            return False, f"Errore salvataggio GSheets: {e}"

    def save_job_opening(self, job_dict):
        """Appends a new job opening"""
        if not self.is_connected:
            self.connect()
            
        try:
            ws = self.spreadsheet.worksheet("JobOpenings")
            headers = ws.row_values(1)
            
            row_to_append = []
            for header in headers:
                # Handle dates for JSON serialization if needed, but gspread handles strings
                val = job_dict.get(header, "")
                if hasattr(val, 'strftime'):
                    val = val.strftime('%Y-%m-%d')
                row_to_append.append(val)
                
            ws.append_row(row_to_append)
            self.load_data()
            return True, "Posizione salvata su Google Sheets!"
        except Exception as e:
            return False, f"Errore salvataggio GSheets: {e}"
