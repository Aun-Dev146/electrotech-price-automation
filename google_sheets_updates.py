#!/usr/bin/env python3
"""
GOOGLE SHEETS UPDATES MODULE
Push final automation updates directly to Google Sheets
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import configparser

logger = logging.getLogger("GoogleSheetsUpdates")

# ============================================
# CONFIGURATION
# ============================================

def load_config():
    """Load configuration from config.ini"""
    config = configparser.ConfigParser()
    config_path = Path(__file__).parent / "config.ini"
    config.read(config_path)
    return config


def get_spreadsheet_id():
    """Get Google Sheets ID from config"""
    config = load_config()
    return config.get('google_sheets', 'spreadsheet_id', fallback=None)


def get_credentials_path():
    """Get credentials file path from config"""
    config = load_config()
    cred_file = config.get('google_sheets', 'credentials_file', fallback='./google_credentials.json')
    return Path(__file__).parent / cred_file


# ============================================
# GOOGLE SHEETS SERVICE
# ============================================

def get_sheets_service():
    """Initialize and return Google Sheets API service"""
    try:
        from google.oauth2.service_account import Credentials
        from googleapiclient.discovery import build
    except ImportError:
        logger.error("Google libraries not installed!")
        logger.error("Run: pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client")
        return None
    
    credentials_path = get_credentials_path()
    
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
# APPEND PRICE UPDATES
# ============================================

def append_price_update(vendor_name: str, product: str, price: float, 
                        category: str = "", status: str = "Active") -> bool:
    """
    Append a price update to the Daily Report sheet
    
    Args:
        vendor_name: Name of the vendor
        product: Product name/model
        price: Price in PKR
        category: Product category
        status: Status (Active/Inactive/Error)
    
    Returns:
        True if successful, False otherwise
    """
    service = get_sheets_service()
    if not service:
        logger.warning("Cannot connect to Google Sheets")
        return False
    
    spreadsheet_id = get_spreadsheet_id()
    if not spreadsheet_id:
        logger.error("Spreadsheet ID not configured")
        return False
    
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        date = datetime.now().strftime("%Y-%m-%d")
        time = datetime.now().strftime("%H:%M:%S")
        
        row = [
            date,
            time,
            vendor_name,
            product,
            f"{price}",
            category,
            status,
            timestamp
        ]
        
        body = {'values': [row]}
        result = service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range="'Daily Report'!A2",
            valueInputOption='RAW',
            body=body
        ).execute()
        
        logger.info(f"✓ Appended: {vendor_name} - {product} - Rs {price}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to append price update: {e}")
        return False


# ============================================
# BATCH APPEND UPDATES
# ============================================

def append_batch_updates(updates: List[Dict]) -> Tuple[int, int]:
    """
    Append multiple updates to Google Sheet
    
    Args:
        updates: List of dicts with keys:
                 - vendor_name, product, price, category, status
    
    Returns:
        Tuple of (successful_count, failed_count)
    """
    service = get_sheets_service()
    if not service:
        logger.warning("Cannot connect to Google Sheets")
        return 0, len(updates)
    
    spreadsheet_id = get_spreadsheet_id()
    if not spreadsheet_id:
        logger.error("Spreadsheet ID not configured")
        return 0, len(updates)
    
    successful = 0
    failed = 0
    
    try:
        rows = []
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        for update in updates:
            row = [
                datetime.now().strftime("%Y-%m-%d"),
                datetime.now().strftime("%H:%M:%S"),
                update.get('vendor_name', ''),
                update.get('product', ''),
                f"{update.get('price', 0)}",
                update.get('category', ''),
                update.get('status', 'Active'),
                timestamp
            ]
            rows.append(row)
        
        if rows:
            body = {'values': rows}
            result = service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range="'Daily Report'!A2",
                valueInputOption='RAW',
                body=body
            ).execute()
            
            successful = len(rows)
            logger.info(f"✓ Appended {successful} updates to Google Sheet")
        
        return successful, failed
        
    except Exception as e:
        logger.error(f"Failed to append batch updates: {e}")
        return 0, len(updates)


# ============================================
# UPDATE VENDOR LIST
# ============================================

def update_vendor_list(vendors: List[Dict]) -> bool:
    """
    Update the Vendor List sheet with current vendors
    
    Args:
        vendors: List of vendor dictionaries
    
    Returns:
        True if successful, False otherwise
    """
    service = get_sheets_service()
    if not service:
        logger.warning("Cannot connect to Google Sheets")
        return False
    
    spreadsheet_id = get_spreadsheet_id()
    if not spreadsheet_id:
        logger.error("Spreadsheet ID not configured")
        return False
    
    try:
        # Prepare headers
        headers = [
            "Vendor ID", "Vendor Name", "Mobile", "WhatsApp", 
            "Email", "Status", "Last Contact"
        ]
        
        # Prepare rows
        rows = [headers]
        for vendor in vendors:
            row = [
                vendor.get('vendor_id', ''),
                vendor.get('vendor_name', ''),
                vendor.get('mobile', ''),
                vendor.get('whatsapp_number', ''),
                vendor.get('email', ''),
                vendor.get('status', ''),
                vendor.get('last_contact', datetime.now().strftime("%Y-%m-%d"))
            ]
            rows.append(row)
        
        # Clear and update
        service.spreadsheets().values().clear(
            spreadsheetId=spreadsheet_id,
            range="'Vendor List'!A:G"
        ).execute()
        
        body = {'values': rows}
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range="'Vendor List'!A1",
            valueInputOption='RAW',
            body=body
        ).execute()
        
        logger.info(f"✓ Updated vendor list with {len(vendors)} vendors")
        return True
        
    except Exception as e:
        logger.error(f"Failed to update vendor list: {e}")
        return False


# ============================================
# APPEND PRICE CHANGES
# ============================================

def append_price_change(product: str, old_price: float, new_price: float, 
                       vendor: str = "", notes: str = "") -> bool:
    """
    Log price changes to Price Updates sheet
    
    Args:
        product: Product name
        old_price: Previous price
        new_price: New price
        vendor: Vendor name
        notes: Additional notes
    
    Returns:
        True if successful, False otherwise
    """
    service = get_sheets_service()
    if not service:
        logger.warning("Cannot connect to Google Sheets")
        return False
    
    spreadsheet_id = get_spreadsheet_id()
    if not spreadsheet_id:
        logger.error("Spreadsheet ID not configured")
        return False
    
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        change = new_price - old_price
        change_percent = (change / old_price * 100) if old_price > 0 else 0
        
        row = [
            timestamp,
            product,
            f"{old_price}",
            f"{new_price}",
            f"{change_percent:.2f}%",
            vendor,
            notes
        ]
        
        body = {'values': [row]}
        service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range="'Price Updates'!A2",
            valueInputOption='RAW',
            body=body
        ).execute()
        
        logger.info(f"✓ Logged price change: {product} Rs {old_price} → Rs {new_price}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to log price change: {e}")
        return False


# ============================================
# GET LATEST DATA
# ============================================

def get_latest_updates(sheet_name: str = "Daily Report", max_rows: int = 100) -> List[Dict]:
    """
    Retrieve latest updates from Google Sheet
    
    Args:
        sheet_name: Sheet tab name
        max_rows: Maximum rows to retrieve
    
    Returns:
        List of rows as dictionaries
    """
    service = get_sheets_service()
    if not service:
        logger.warning("Cannot connect to Google Sheets")
        return []
    
    spreadsheet_id = get_spreadsheet_id()
    if not spreadsheet_id:
        logger.error("Spreadsheet ID not configured")
        return []
    
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=f"'{sheet_name}'!A1:H{max_rows}"
        ).execute()
        
        rows = result.get('values', [])
        if not rows:
            return []
        
        # Convert to list of dicts
        headers = rows[0]
        data = []
        for row in rows[1:]:
            # Pad row if necessary
            while len(row) < len(headers):
                row.append('')
            data.append(dict(zip(headers, row)))
        
        return data
        
    except Exception as e:
        logger.error(f"Failed to retrieve updates: {e}")
        return []


# ============================================
# MAIN TEST
# ============================================

if __name__ == "__main__":
    # Test connection
    print("\n" + "="*60)
    print("GOOGLE SHEETS UPDATES - TEST CONNECTION")
    print("="*60)
    
    spreadsheet_id = get_spreadsheet_id()
    credentials_path = get_credentials_path()
    
    print(f"\nSpreadsheet ID: {spreadsheet_id}")
    print(f"Credentials Path: {credentials_path}")
    print(f"Credentials Exists: {credentials_path.exists()}")
    
    service = get_sheets_service()
    if service:
        print("\n✅ Connection successful!")
        
        # Test append
        print("\nTesting price update append...")
        result = append_price_update(
            vendor_name="Test Vendor",
            product="Test Product",
            price=5000,
            category="Electronics",
            status="Test"
        )
        print(f"Result: {result}")
    else:
        print("\n❌ Connection failed!")
        print("\nRun setup first:")
        print("  python setup_google_sheets.py")
