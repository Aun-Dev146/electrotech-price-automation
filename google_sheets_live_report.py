#!/usr/bin/env python3
"""
GOOGLE SHEETS LIVE REPORT CONNECTOR
Push scraped price data directly to Google Sheets for CEO viewing
"""

import sqlite3
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import json

logger = logging.getLogger("GoogleSheetsLiveReport")

# ============================================
# GOOGLE SHEETS API SETUP
# ============================================

def get_sheets_service():
    """
    Initialize Google Sheets API service
    
    Setup Instructions:
    1. Go to https://console.cloud.google.com/
    2. Create a new project
    3. Enable Google Sheets API + Google Drive API
    4. Create OAuth 2.0 credentials (Desktop app)
    5. Download JSON credentials
    6. Save as 'google_credentials.json' in project root
    7. Share the Google Sheet with the service account email
    """
    try:
        from google.oauth2.service_account import Credentials
        from googleapiclient.discovery import build
    except ImportError:
        logger.error("Google libraries not installed!")
        print("Run: pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client")
        return None
    
    credentials_path = Path(__file__).parent / "google_credentials.json"
    
    if not credentials_path.exists():
        logger.error(f"Credentials file not found: {credentials_path}")
        return None
    
    try:
        creds = Credentials.from_service_account_file(
            credentials_path,
            scopes=[
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
        )
        service = build('sheets', 'v4', credentials=creds)
        return service
    except Exception as e:
        logger.error(f"Failed to initialize Google Sheets: {e}")
        return None

# ============================================
# SETUP PROFESSIONAL HEADERS
# ============================================

def setup_sheet_headers(sheet_id: str, sheet_name: str = "Daily Report") -> bool:
    """
    Setup professional column headers in Google Sheet
    
    Args:
        sheet_id: Google Sheet ID from URL
        sheet_name: Sheet tab name
    """
    service = get_sheets_service()
    if not service:
        return False
    
    try:
        # Headers with proper formatting
        headers = [
            "Date",
            "Time",
            "Vendor Name",
            "Product Category",
            "Product Model",
            "Product Company",
            "Price (PKR)",
            "Unit",
            "Source",
            "Status"
        ]
        
        # Create requests for formatting
        requests = [
            # Add headers
            {
                "values": [headers],
                "range": f"{sheet_name}!A1:J1"
            }
        ]
        
        # Write headers
        body = {"values": requests[0]["values"]}
        service.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range=f"{sheet_name}!A1:J1",
            valueInputOption="RAW",
            body=body
        ).execute()
        
        # Format headers (bold, colored background)
        format_requests = [
            {
                "repeatCell": {
                    "range": {
                        "sheetId": 0,  # Assuming first sheet
                        "rowIndex": 0,
                        "columnIndex": 0,
                        "endColumnIndex": 10
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "backgroundColor": {
                                "red": 0.2,
                                "green": 0.5,
                                "blue": 0.9
                            },
                            "textFormat": {
                                "bold": True,
                                "fontSize": 11,
                                "foregroundColor": {
                                    "red": 1,
                                    "green": 1,
                                    "blue": 1
                                }
                            },
                            "horizontalAlignment": "CENTER",
                            "verticalAlignment": "MIDDLE"
                        }
                    },
                    "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment)"
                }
            },
            {
                "setBasicFilter": {
                    "filter": {
                        "range": {
                            "sheetId": 0,
                            "rowIndex": 0,
                            "columnIndex": 0,
                            "endColumnIndex": 10
                        }
                    }
                }
            },
            {
                "updateSheetProperties": {
                    "fields": "gridProperties.frozenRowCount",
                    "properties": {
                        "sheetId": 0,
                        "gridProperties": {
                            "frozenRowCount": 1
                        }
                    }
                }
            }
        ]
        
        body = {"requests": format_requests}
        service.spreadsheets().batchUpdate(
            spreadsheetId=sheet_id,
            body=body
        ).execute()
        
        print(f"✓ Headers setup complete for sheet: {sheet_name}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to setup headers: {e}")
        print(f"ERROR: {e}")
        return False

# ============================================
# PUSH DATA TO GOOGLE SHEETS
# ============================================

def push_daily_prices_to_sheets(sheet_id: str, sheet_name: str = "Daily Report") -> bool:
    """
    Push all daily price data from database to Google Sheets
    
    Args:
        sheet_id: Google Sheet ID from URL
        sheet_name: Sheet tab name to write to
    """
    service = get_sheets_service()
    if not service:
        return False
    
    try:
        # Load data from database
        db_path = Path(__file__).parent / "data" / "electro_tech.db"
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        
        cursor = conn.execute("""
            SELECT 
                d.date,
                d.extracted_at as time,
                v.vendor_name,
                d.product_category,
                d.product_model,
                d.product_company,
                d.price,
                d.unit,
                d.source,
                'Completed' as status
            FROM daily_prices d
            JOIN vendors v ON d.vendor_id = v.vendor_id
            ORDER BY d.date DESC, d.extracted_at DESC
            LIMIT 1000
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            print("No data found in database")
            return False
        
        # Prepare data for Google Sheets
        data_rows = []
        for row in rows:
            data_rows.append([
                row['date'] or '',
                row['time'] or '',
                row['vendor_name'] or '',
                row['product_category'] or '',
                row['product_model'] or '',
                row['product_company'] or '',
                row['price'] or '',
                row['unit'] or '',
                row['source'] or '',
                row['status'] or ''
            ])
        
        # Clear existing data (keep headers)
        service.spreadsheets().values().clear(
            spreadsheetId=sheet_id,
            range=f"{sheet_name}!A2:J1000"
        ).execute()
        
        # Write data
        body = {"values": data_rows}
        result = service.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range=f"{sheet_name}!A2",
            valueInputOption="RAW",
            body=body
        ).execute()
        
        print(f"✓ Pushed {len(data_rows)} price records to Google Sheets")
        return True
    
    except Exception as e:
        logger.error(f"Failed to push data: {e}")
        print(f"ERROR: {e}")
        return False

# ============================================
# PUSH TODAY'S SUMMARY
# ============================================

def push_daily_summary_to_sheets(sheet_id: str, summary_sheet: str = "Summary") -> bool:
    """
    Create summary statistics sheet
    
    Args:
        sheet_id: Google Sheet ID from URL
        summary_sheet: Summary sheet tab name
    """
    service = get_sheets_service()
    if not service:
        return False
    
    try:
        db_path = Path(__file__).parent / "data" / "electro_tech.db"
        conn = sqlite3.connect(db_path)
        
        # Get statistics
        today = datetime.now().strftime("%Y-%m-%d")
        
        stats = {}
        
        # Total vendors
        cursor = conn.execute("SELECT COUNT(*) as count FROM vendors WHERE status='active'")
        stats['total_vendors'] = cursor.fetchone()[0]
        
        # Today's records
        cursor = conn.execute(f"SELECT COUNT(*) as count FROM daily_prices WHERE date='{today}'")
        stats['today_records'] = cursor.fetchone()[0]
        
        # Average price
        cursor = conn.execute(f"SELECT AVG(price) as avg_price FROM daily_prices WHERE date='{today}'")
        avg = cursor.fetchone()[0]
        stats['avg_price'] = round(avg, 2) if avg else 0
        
        # Categories
        cursor = conn.execute(f"SELECT COUNT(DISTINCT product_category) as count FROM daily_prices WHERE date='{today}'")
        stats['categories'] = cursor.fetchone()[0]
        
        conn.close()
        
        # Prepare summary data
        summary_data = [
            ["Daily Report Summary", "", ""],
            ["Date", today, ""],
            ["Total Active Vendors", stats['total_vendors'], ""],
            ["Records Collected Today", stats['today_records'], ""],
            ["Product Categories", stats['categories'], ""],
            ["Average Price (PKR)", stats['avg_price'], ""],
            ["Report Generated", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), ""]
        ]
        
        # Write to summary sheet
        body = {"values": summary_data}
        service.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range=f"{summary_sheet}!A1:C7",
            valueInputOption="RAW",
            body=body
        ).execute()
        
        print(f"✓ Summary updated: {stats['today_records']} records from {stats['total_vendors']} vendors")
        return True
    
    except Exception as e:
        logger.error(f"Failed to push summary: {e}")
        print(f"ERROR: {e}")
        return False

# ============================================
# MAIN CLI
# ============================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Push price data to Google Sheets')
    
    parser.add_argument(
        '--sheet-id',
        required=True,
        help='Google Sheet ID (from URL)'
    )
    
    parser.add_argument(
        '--setup',
        action='store_true',
        help='Setup headers in Google Sheet'
    )
    
    parser.add_argument(
        '--push',
        action='store_true',
        help='Push daily prices to Google Sheet'
    )
    
    parser.add_argument(
        '--summary',
        action='store_true',
        help='Push daily summary to Google Sheet'
    )
    
    parser.add_argument(
        '--all',
        action='store_true',
        help='Setup headers and push all data'
    )
    
    parser.add_argument(
        '--sheet-name',
        default='Daily Report',
        help='Sheet tab name (default: Daily Report)'
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*80)
    print("GOOGLE SHEETS LIVE REPORT CONNECTOR")
    print("="*80 + "\n")
    
    if args.all:
        print("Setting up headers...")
        setup_sheet_headers(args.sheet_id, args.sheet_name)
        print("\nPushing data...")
        push_daily_prices_to_sheets(args.sheet_id, args.sheet_name)
        print("\nUpdating summary...")
        push_daily_summary_to_sheets(args.sheet_id)
    
    elif args.setup:
        setup_sheet_headers(args.sheet_id, args.sheet_name)
    
    elif args.push:
        push_daily_prices_to_sheets(args.sheet_id, args.sheet_name)
    
    elif args.summary:
        push_daily_summary_to_sheets(args.sheet_id)
    
    else:
        parser.print_help()
        print("\nQuick Start:")
        print("1. Setup headers:")
        print(f"   python google_sheets_live_report.py --sheet-id <YOUR_SHEET_ID> --setup")
        print("\n2. Push data:")
        print(f"   python google_sheets_live_report.py --sheet-id <YOUR_SHEET_ID> --push")
        print("\n3. Setup + Push all:")
        print(f"   python google_sheets_live_report.py --sheet-id <YOUR_SHEET_ID> --all")

if __name__ == "__main__":
    main()
