# 👥 Professional Recruitment Tracker

A comprehensive HR management application built with Streamlit and Google Sheets integration.

## 🚀 Features

- **Dashboard** - Real-time KPIs and analytics
- **Job Openings Management** - Track open positions, costs, and hiring progress
- **Candidate Tracking** - Complete recruitment pipeline management
- **Analytics** - Time-to-hire, cost-per-hire, conversion rates
- **Google Sheets Integration** - Cloud-based data storage with real-time sync
- **Multi-stakeholder Workflows** - HR, Hiring Manager, and Decision Maker views

## 📋 Requirements

- Python 3.8+
- Google Cloud Service Account (for Sheets API)
- Dependencies listed in `requirements.txt`

## 🔧 Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Google Sheets
1. Create a Google Cloud project
2. Enable Google Sheets API
3. Create a Service Account and download credentials
4. Share your Google Sheet with the service account email
5. Add credentials to Streamlit secrets (see below)

### 3. Run Locally
```bash
streamlit run app.py
```

## ☁️ Deployment (Streamlit Cloud)

### Configuration
Add your Google Sheets credentials to Streamlit Cloud secrets:

1. Go to your app settings on Streamlit Cloud
2. Navigate to "Secrets"
3. Add the following (paste your entire credentials.json content):

```toml
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "your-cert-url"
```

### Environment Variables
Set the Google Sheet URL in your app or as a secret:
```toml
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit"
```

## 📊 Data Structure

The application uses three main sheets:
- **Candidates** - Applicant information and pipeline status
- **JobOpenings** - Open positions and hiring details
- **Preferences** - Configuration (recruiters, departments, sources, statuses)

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **Backend**: Python, Pandas
- **Database**: Google Sheets (via gspread)
- **Analytics**: Custom analytics module
- **Authentication**: Google Service Account

## 📝 License

Private project - All rights reserved

## 👨‍💻 Author

Dylan - Professional HR Management System
