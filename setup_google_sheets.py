#!/usr/bin/env python3
"""
GOOGLE SHEETS SETUP - Connect to provided spreadsheet
Sets up the automation to push final updates to the specified Google Sheet
"""

import configparser
from pathlib import Path
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SetupGoogleSheets")

# ============================================
# SPREADSHEET CONFIGURATION
# ============================================

SPREADSHEET_ID = "1PcC2KdA3VHf9EnyA4XzU_zWS7hLVpxDjkqwcCJGgFBs"
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1PcC2KdA3VHf9EnyA4XzU_zWS7hLVpxDjkqwcCJGgFBs/edit?usp=sharing&pli=1&authuser=0"

# ============================================
# SETUP INSTRUCTIONS
# ============================================

def print_setup_instructions():
    """Print setup instructions for Google Sheets API"""
    print("\n" + "="*60)
    print("GOOGLE SHEETS CONNECTION SETUP")
    print("="*60)
    print(f"\nTarget Spreadsheet: {SPREADSHEET_URL}")
    print(f"Spreadsheet ID: {SPREADSHEET_ID}")
    print("\n[STEP 1] Create Google Cloud Project")
    print("-" * 60)
    print("1. Go to https://console.cloud.google.com/")
    print("2. Click on 'Select a Project' → 'NEW PROJECT'")
    print("3. Name: 'Electro Tech Automation'")
    print("4. Click 'CREATE'")
    
    print("\n[STEP 2] Enable Google Sheets API")
    print("-" * 60)
    print("1. In Google Cloud Console, go to 'APIs & Services' → 'Library'")
    print("2. Search for 'Google Sheets API'")
    print("3. Click on it and click 'ENABLE'")
    print("4. Repeat for 'Google Drive API'")
    
    print("\n[STEP 3] Create Service Account")
    print("-" * 60)
    print("1. Go to 'APIs & Services' → 'Credentials'")
    print("2. Click 'CREATE CREDENTIALS' → 'Service Account'")
    print("3. Fill in the details:")
    print("   - Service account name: electro-tech-automation")
    print("   - Service account ID: (auto-filled)")
    print("4. Click 'CREATE AND CONTINUE'")
    print("5. Grant these roles:")
    print("   - Editor")
    print("6. Click 'CONTINUE' → 'DONE'")
    
    print("\n[STEP 4] Create API Key")
    print("-" * 60)
    print("1. Go to 'APIs & Services' → 'Credentials'")
    print("2. Find the service account you created")
    print("3. Under 'Keys', click 'ADD KEY' → 'Create new key'")
    print("4. Select 'JSON' format")
    print("5. Click 'CREATE' (file will download)")
    print("6. Save the JSON file as 'google_credentials.json' in this directory")
    print(f"   Location: {Path(__file__).parent / 'google_credentials.json'}")
    
    print("\n[STEP 5] Share Spreadsheet with Service Account")
    print("-" * 60)
    print(f"1. Open the spreadsheet: {SPREADSHEET_URL}")
    print("2. Click 'Share' button (top right)")
    print("3. In the credentials JSON, find the 'client_email' field")
    print("4. Copy that email address")
    print("5. Paste it in the Share dialog")
    print("6. Give it 'Editor' access")
    print("7. Click 'Share'")
    
    print("\n[STEP 6] Verify Connection")
    print("-" * 60)
    print("After completing steps 1-5, run:")
    print("  python setup_google_sheets.py --verify")
    print("\n" + "="*60 + "\n")


def verify_connection():
    """Verify Google Sheets connection"""
    try:
        from google.oauth2.service_account import Credentials
        from googleapiclient.discovery import build
    except ImportError:
        print("ERROR: Google libraries not installed!")
        print("Run: pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client")
        return False
    
    credentials_path = Path(__file__).parent / "google_credentials.json"
    
    if not credentials_path.exists():
        print(f"\n❌ ERROR: Credentials file not found!")
        print(f"   Expected location: {credentials_path}")
        print("\n   Please complete STEP 4 above to download the credentials file.")
        return False
    
    try:
        # Load and test credentials
        creds = Credentials.from_service_account_file(
            credentials_path,
            scopes=[
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
        )
        
        # Try to access the spreadsheet
        service = build('sheets', 'v4', credentials=creds)
        result = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
        
        print("\n✅ CONNECTION SUCCESSFUL!")
        print(f"   Spreadsheet: {result.get('properties', {}).get('title')}")
        print(f"   Spreadsheet ID: {SPREADSHEET_ID}")
        print(f"   Service Account: {creds.service_account_email}")
        print("\n✅ Ready to push updates to Google Sheets!\n")
        return True
        
    except FileNotFoundError:
        print(f"\n❌ ERROR: Credentials file not found: {credentials_path}")
        return False
    except Exception as e:
        print(f"\n❌ CONNECTION FAILED: {e}")
        print("\nTroubleshooting:")
        print("1. Verify credentials JSON is valid")
        print("2. Check that service account email is added with 'Editor' access")
        print("3. Verify spreadsheet ID is correct")
        return False


def setup_sheet_structure():
    """Setup recommended sheet structure"""
    try:
        from google.oauth2.service_account import Credentials
        from googleapiclient.discovery import build
    except ImportError:
        print("ERROR: Google libraries not installed!")
        return False
    
    credentials_path = Path(__file__).parent / "google_credentials.json"
    if not credentials_path.exists():
        print("ERROR: Credentials file not found!")
        return False
    
    try:
        creds = Credentials.from_service_account_file(
            credentials_path,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        service = build('sheets', 'v4', credentials=creds)
        
        # Define sheets structure
        sheets_config = [
            {
                "name": "Daily Report",
                "headers": [
                    "Date", "Time", "Vendor Name", "Product", "Price (PKR)",
                    "Category", "Status", "Last Updated"
                ]
            },
            {
                "name": "Vendor List",
                "headers": [
                    "Vendor ID", "Vendor Name", "Mobile", "WhatsApp", "Email",
                    "Status", "Last Contact"
                ]
            },
            {
                "name": "Price Updates",
                "headers": [
                    "Timestamp", "Product", "Old Price", "New Price", "Change %",
                    "Vendor", "Notes"
                ]
            }
        ]
        
        # Create or update sheets
        for sheet_config in sheets_config:
            sheet_name = sheet_config["name"]
            headers = sheet_config["headers"]
            
            try:
                # Clear existing data
                service.spreadsheets().values().clear(
                    spreadsheetId=SPREADSHEET_ID,
                    range=f"'{sheet_name}'!A:Z"
                ).execute()
                
                # Add headers
                body = {'values': [headers]}
                service.spreadsheets().values().update(
                    spreadsheetId=SPREADSHEET_ID,
                    range=f"'{sheet_name}'!A1",
                    valueInputOption='RAW',
                    body=body
                ).execute()
                
                print(f"✓ Sheet '{sheet_name}' configured")
            except Exception as e:
                print(f"⚠ Could not configure sheet '{sheet_name}': {e}")
        
        print("\n✅ Sheet structure ready!")
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False


def main():
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--verify":
        print("\nVerifying Google Sheets connection...")
        verify_connection()
    elif len(sys.argv) > 1 and sys.argv[1] == "--setup-sheets":
        print("\nSetting up sheet structure...")
        setup_sheet_structure()
    else:
        print_setup_instructions()


if __name__ == "__main__":
    main()
