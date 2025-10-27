import gspread
import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials
from database import finance_db
from datetime import datetime, date

# Google Sheets auth
scopes = ["https://www.googleapis.com/auth/spreadsheets"]

def get_google_credentials():
    """Get Google credentials from Streamlit secrets or fallback to local file"""
    try:
        # Try to get credentials from Streamlit secrets
        google_creds = st.secrets["google_credentials"]
        
        # Convert to dict format for Google API
        creds_dict = {
            "type": google_creds["type"],
            "project_id": google_creds["project_id"],
            "private_key_id": google_creds["private_key_id"],
            "private_key": google_creds["private_key"],
            "client_email": google_creds["client_email"],
            "client_id": google_creds["client_id"],
            "auth_uri": google_creds["auth_uri"],
            "token_uri": google_creds["token_uri"],
            "auth_provider_x509_cert_url": google_creds["auth_provider_x509_cert_url"],
            "client_x509_cert_url": google_creds["client_x509_cert_url"],
            "universe_domain": google_creds["universe_domain"]
        }
        
        return Credentials.from_service_account_info(creds_dict, scopes=scopes)
        
    except Exception as e:
        # Fallback to local credentials file for development
        print(f"Using local credentials file (Streamlit secrets not available): {e}")
        return Credentials.from_service_account_file("credentials.json", scopes=scopes)

creds = get_google_credentials()
client = gspread.authorize(creds)

# Open sheet
sheet_id = "1O_tL9kVtNlGbZkfKsmHY3FqWeNd1vuYDNKOP9sFXqm0"
workbook = client.open_by_key(sheet_id)
sheet = workbook.worksheet("Página1")

def clean_currency_value(value):
    """Clean currency values and convert to float"""
    if pd.isna(value) or str(value).strip() == "":
        return 0.0
    
    value_str = str(value).strip()
    
    try:
        # Remove currency symbols and convert to float
        cleaned_value = value_str.replace('R$', '').replace('$', '').replace(',', '.').strip()
        return float(cleaned_value)
    except Exception:
        return 0.0

def fetch_and_process_data():
    """Fetch and process data from Google Sheets"""
    try:
        # Fetch all rows once
        rows = sheet.get_all_values()
        
        if not rows or len(rows) < 2:
            print("No data found in Google Sheets")
            return pd.DataFrame()
        
        # Transform fetched data into DataFrame
        df = pd.DataFrame(rows[1:], columns=rows[0])
        
        print(f"Fetched {len(df)} rows from Google Sheets")
        print(f"Columns: {df.columns.tolist()}")
        
        # Clean and convert data types
        if 'Value' in df.columns:
            df['Value'] = df['Value'].apply(clean_currency_value)
            print(f"Cleaned Value column, total amount: R$ {df['Value'].sum():.2f}")
        
        # Convert Date column to datetime
        if 'Data' in df.columns:
            df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
            # Filter out rows with invalid dates
            df = df.dropna(subset=['Data'])
            print(f"Converted dates, remaining rows: {len(df)}")
        
        # Filter for current month only
        if 'Data' in df.columns and not df.empty:
            current_month = datetime.now().strftime("%Y-%m")
            df['Month'] = df['Data'].dt.strftime("%Y-%m")
            current_month_df = df[df['Month'] == current_month].copy()
            print(f"Current month ({current_month}) expenses: {len(current_month_df)} rows")
            return current_month_df
        
        return df
        
    except Exception as e:
        print(f"Error fetching data from Google Sheets: {e}")
        return pd.DataFrame()

# Initialize with fetched data
df = fetch_and_process_data()

def get_processed_data():
    """Get processed DataFrame with current expense data"""
    # Always fetch fresh data from Google Sheets
    fresh_df = fetch_and_process_data()
    
    if not fresh_df.empty:
        # Automatically save fresh data to database
        save_current_data_to_db(fresh_df)
    
    return fresh_df

def save_current_data_to_db(data_df=None):
    """Save current data to database"""
    try:
        # Use provided dataframe or fetch fresh data
        if data_df is None:
            data_df = fetch_and_process_data()
        
        if data_df.empty:
            print("No data to save")
            return False
        
        # Save today's expenses to database
        today = date.today().isoformat()
        success = finance_db.save_daily_expenses(data_df, today)
        if success:
            print(f"Data saved successfully for {today}")
        else:
            print("Failed to save data")
        return success
    except Exception as e:
        print(f"Error saving data: {e}")
        return False

def get_monthly_expense_summary():
    """Get current month expense summary with comparisons to expected amounts"""
    try:
        summary = finance_db.get_current_month_summary()
        return summary
    except Exception as e:
        print(f"Error getting monthly summary: {e}")
        return {}

# Print current data status
print("Data Source Module Initialized")
if not df.empty:
    print(f"Found {len(df)} current month expenses")
    print(f"Total value: R$ {df['Value'].sum():.2f}" if 'Value' in df.columns else "No Value column")
    print(f"Date range: {df['Data'].min()} to {df['Data'].max()}" if 'Data' in df.columns else "No Data column")
else:
    print("No current month data found")

# Automatically save to database when module is imported
if __name__ == "__main__":
    save_current_data_to_db()