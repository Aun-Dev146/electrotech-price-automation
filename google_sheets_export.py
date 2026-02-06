#!/usr/bin/env python3
"""
GOOGLE SHEETS EXPORT
Export vendor list to Google Sheets for CEO access
Supports both online sharing and local Excel export
"""

import sqlite3
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

logger = logging.getLogger("GoogleSheetsExport")

# ============================================
# OPTION 1: EXPORT TO GOOGLE SHEETS (ONLINE)
# ============================================

def export_to_google_sheets(spreadsheet_id: str = None, credentials_path: str = None):
    """
    Export vendors to Google Sheets
    
    Setup Instructions:
    1. Go to https://console.cloud.google.com/
    2. Create a new project
    3. Enable Google Sheets API
    4. Create OAuth 2.0 credentials (Desktop application)
    5. Download JSON credentials file
    6. Save as 'google_credentials.json' in project root
    7. Share the spreadsheet with your CEO's email
    
    Args:
        spreadsheet_id: Google Sheet ID (from URL)
        credentials_path: Path to credentials JSON file
    """
    try:
        from google.oauth2.service_account import Credentials
        from googleapiclient.discovery import build
    except ImportError:
        print("ERROR: Google libraries not installed!")
        print("Run: pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client")
        return False
    
    if not credentials_path:
        credentials_path = Path(__file__).parent / "google_credentials.json"
    
    if not Path(credentials_path).exists():
        print(f"\nERROR: Credentials file not found: {credentials_path}")
        print("\nSetup steps:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create project 'Electro Tech Vendors'")
        print("3. Enable 'Google Sheets API'")
        print("4. Create Service Account credentials")
        print("5. Download JSON key")
        print(f"6. Save to: {credentials_path}")
        return False
    
    if not spreadsheet_id:
        print("\nERROR: Spreadsheet ID required!")
        print("Get ID from Google Sheet URL: https://docs.google.com/spreadsheets/d/{ID}/edit")
        return False
    
    try:
        # Load vendors from database
        vendors = load_vendors_from_db()
        if not vendors:
            print("ERROR: No vendors found in database!")
            return False
        
        # Authenticate with Google
        creds = Credentials.from_service_account_file(
            credentials_path,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        
        service = build('sheets', 'v4', credentials=creds)
        
        # Prepare data
        headers = [
            'Vendor ID', 'Vendor Name', 'Mobile', 'WhatsApp Number', 
            'Email', 'Address', 'Type', 'Products', 'Status', 'Added Date'
        ]
        
        rows = [headers]
        for vendor in vendors:
            rows.append([
                vendor['vendor_id'],
                vendor['vendor_name'],
                vendor['mobile'],
                vendor['whatsapp_number'],
                vendor['email'] or '',
                vendor['address'] or '',
                vendor['vendor_type'] or '',
                vendor['products'] or '',
                vendor['status'],
                vendor['created_at']
            ])
        
        # Clear existing data
        service.spreadsheets().values().clear(
            spreadsheetId=spreadsheet_id,
            range='Vendors!A:J'
        ).execute()
        
        # Write new data
        body = {'values': rows}
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='Vendors!A1',
            valueInputOption='RAW',
            body=body
        ).execute()
        
        print(f"✓ Exported {len(vendors)} vendors to Google Sheets!")
        print(f"Spreadsheet ID: {spreadsheet_id}")
        print(f"Share with your CEO using: https://docs.google.com/spreadsheets/d/{spreadsheet_id}/")
        
        return True
    
    except Exception as e:
        print(f"ERROR: Export failed: {e}")
        return False

# ============================================
# OPTION 2: EXPORT TO EXCEL (LOCAL)
# ============================================

def export_to_excel(output_path: str = None) -> bool:
    """
    Export vendors to Excel file
    
    Usage:
        python google_sheets_export.py --export-excel
    """
    try:
        import pandas as pd
    except ImportError:
        print("ERROR: pandas not installed!")
        print("Run: pip install pandas openpyxl")
        return False
    
    if not output_path:
        output_path = Path(__file__).parent / "vendor_list.xlsx"
    
    try:
        # Load vendors from database
        vendors = load_vendors_from_db()
        if not vendors:
            print("ERROR: No vendors found in database!")
            return False
        
        # Create DataFrame
        df = pd.DataFrame(vendors)
        
        # Reorder columns
        column_order = [
            'vendor_id', 'vendor_name', 'mobile', 'whatsapp_number',
            'email', 'address', 'vendor_type', 'products', 'status', 'created_at'
        ]
        df = df[column_order]
        
        # Rename columns to user-friendly names
        df.columns = [
            'Vendor ID', 'Vendor Name', 'Mobile', 'WhatsApp Number',
            'Email', 'Address', 'Type', 'Products', 'Status', 'Added Date'
        ]
        
        # Write to Excel with formatting
        df.to_excel(output_path, index=False, sheet_name='Vendors')
        
        print(f"✓ Exported {len(vendors)} vendors to Excel!")
        print(f"File: {output_path}")
        print(f"\nShare this file with your CEO: {output_path}")
        
        return True
    
    except Exception as e:
        print(f"ERROR: Export to Excel failed: {e}")
        return False

# ============================================
# OPTION 3: EXPORT TO CSV (UNIVERSAL FORMAT)
# ============================================

def export_to_csv(output_path: str = None) -> bool:
    """
    Export vendors to CSV file
    
    Usage:
        python google_sheets_export.py --export-csv
    """
    import csv
    
    if not output_path:
        output_path = Path(__file__).parent / "vendor_list.csv"
    
    try:
        # Load vendors from database
        vendors = load_vendors_from_db()
        if not vendors:
            print("ERROR: No vendors found in database!")
            return False
        
        # Write to CSV
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'vendor_id', 'vendor_name', 'mobile', 'whatsapp_number',
                'email', 'address', 'vendor_type', 'products', 'status', 'created_at'
            ]
            
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(vendors)
        
        print(f"✓ Exported {len(vendors)} vendors to CSV!")
        print(f"File: {output_path}")
        print(f"\nShare this file with your CEO: {output_path}")
        
        return True
    
    except Exception as e:
        print(f"ERROR: Export to CSV failed: {e}")
        return False

# ============================================
# HELPER FUNCTIONS
# ============================================

def load_vendors_from_db() -> List[Dict]:
    """Load all vendors from database"""
    db_path = Path(__file__).parent / "data" / "electro_tech.db"
    
    if not db_path.exists():
        print(f"ERROR: Database not found: {db_path}")
        return []
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        
        cursor = conn.execute("""
            SELECT * FROM vendors
            ORDER BY vendor_id
        """)
        
        vendors = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return vendors
    
    except Exception as e:
        print(f"ERROR: Failed to load vendors: {e}")
        return []

def create_google_sheet_template(sheet_name: str = "Electro Tech Vendors") -> str:
    """
    Instructions for creating a new Google Sheet
    """
    instructions = f"""
    ╔════════════════════════════════════════════════════════════════════════════╗
    ║                   CREATE NEW GOOGLE SHEET - STEP BY STEP                   ║
    ╚════════════════════════════════════════════════════════════════════════════╝
    
    1. Go to https://docs.google.com/spreadsheets/create
    
    2. Name it: "{sheet_name}"
    
    3. Create columns in Row 1:
       A: Vendor ID
       B: Vendor Name
       C: Mobile
       D: WhatsApp Number
       E: Email
       F: Address
       G: Type
       H: Products
       I: Status
       J: Added Date
    
    4. Get your Spreadsheet ID:
       - Copy the ID from URL: https://docs.google.com/spreadsheets/d/[ID]/edit
       - Save this ID for export: {sheet_name}
    
    5. Share with CEO:
       - Click "Share" button
       - Add CEO email
       - Give "Viewer" permission
       - Send them the link
    
    6. Export vendors:
       python google_sheets_export.py --google {sheet_name}
    """
    
    return instructions

# ============================================
# MAIN CLI
# ============================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Export vendor list to Google Sheets or Excel'
    )
    
    parser.add_argument(
        '--google',
        metavar='SHEET_ID',
        help='Export to Google Sheets (provide Spreadsheet ID)'
    )
    
    parser.add_argument(
        '--excel',
        metavar='OUTPUT_PATH',
        nargs='?',
        const='vendor_list.xlsx',
        help='Export to Excel file (default: vendor_list.xlsx)'
    )
    
    parser.add_argument(
        '--csv',
        metavar='OUTPUT_PATH',
        nargs='?',
        const='vendor_list.csv',
        help='Export to CSV file (default: vendor_list.csv)'
    )
    
    parser.add_argument(
        '--setup-google',
        action='store_true',
        help='Show Google Sheets setup instructions'
    )
    
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all vendors from database'
    )
    
    args = parser.parse_args()
    
    if args.setup_google:
        print(create_google_sheet_template())
    
    elif args.google:
        print("\n" + "="*80)
        print("EXPORTING TO GOOGLE SHEETS...")
        print("="*80 + "\n")
        export_to_google_sheets(spreadsheet_id=args.google)
    
    elif args.excel:
        print("\n" + "="*80)
        print("EXPORTING TO EXCEL...")
        print("="*80 + "\n")
        export_to_excel(output_path=args.excel)
    
    elif args.csv:
        print("\n" + "="*80)
        print("EXPORTING TO CSV...")
        print("="*80 + "\n")
        export_to_csv(output_path=args.csv)
    
    elif args.list:
        print("\n" + "="*80)
        print("VENDOR LIST")
        print("="*80 + "\n")
        
        vendors = load_vendors_from_db()
        
        if not vendors:
            print("No vendors found in database!")
            return
        
        print(f"{'ID':<10} {'Name':<25} {'WhatsApp':<18} {'Type':<10} {'Status':<8}")
        print("-" * 80)
        
        for vendor in vendors:
            print(f"{vendor['vendor_id']:<10} {vendor['vendor_name']:<25} "
                  f"{vendor['whatsapp_number']:<18} {vendor['vendor_type']:<10} "
                  f"{vendor['status']:<8}")
        
        print("-" * 80)
        print(f"Total: {len(vendors)} vendors\n")
    
    else:
        parser.print_help()
        print("\n" + "="*80)
        print("QUICK START OPTIONS")
        print("="*80)
        print("\n1. EXPORT TO EXCEL (Recommended for sharing):")
        print("   python google_sheets_export.py --excel")
        print("   Then share the file with your CEO\n")
        
        print("2. EXPORT TO GOOGLE SHEETS (Online, real-time):")
        print("   a) python google_sheets_export.py --setup-google")
        print("   b) Create sheet and get ID from URL")
        print("   c) python google_sheets_export.py --google <SHEET_ID>\n")
        
        print("3. EXPORT TO CSV (Universal format):")
        print("   python google_sheets_export.py --csv\n")
        
        print("4. LIST VENDORS IN DATABASE:")
        print("   python google_sheets_export.py --list\n")

if __name__ == "__main__":
    main()
