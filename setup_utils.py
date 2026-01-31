#!/usr/bin/env python3
"""
QUICK SETUP & UTILITIES
First-time setup and vendor management
"""

import sys
import sqlite3
from pathlib import Path

# ============================================
# VENDOR EXCEL IMPORT
# ============================================

def import_vendors_from_excel(excel_path: str):
    """
    Import vendors from Excel file
    
    Excel format:
    vendor_id | vendor_name | mobile | whatsapp_number | email | address | vendor_type | products
    """
    try:
        import pandas as pd
    except ImportError:
        print("ERROR: pandas not installed!")
        print("Run: pip install pandas openpyxl")
        return False
    
    print(f"Importing vendors from: {excel_path}")
    
    try:
        # Read Excel
        df = pd.read_excel(excel_path)
        
        # Required columns
        required_cols = ['vendor_id', 'vendor_name', 'mobile', 'whatsapp_number']
        for col in required_cols:
            if col not in df.columns:
                print(f"ERROR: Missing column: {col}")
                return False
        
        # Connect to database
        db_path = Path(__file__).parent / "data" / "electro_tech.db"
        conn = sqlite3.connect(db_path)
        
        # Import each vendor
        imported = 0
        skipped = 0
        
        for _, row in df.iterrows():
            try:
                conn.execute("""
                    INSERT OR REPLACE INTO vendors 
                    (vendor_id, vendor_name, mobile, email, whatsapp_number, 
                     address, vendor_type, products, status, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'active', CURRENT_TIMESTAMP)
                """, (
                    row.get('vendor_id'),
                    row.get('vendor_name'),
                    row.get('mobile'),
                    row.get('email', ''),
                    row.get('whatsapp_number'),
                    row.get('address', ''),
                    row.get('vendor_type', 'Trader'),
                    row.get('products', '')
                ))
                imported += 1
            
            except Exception as e:
                print(f"Warning: Failed to import {row.get('vendor_id')}: {e}")
                skipped += 1
        
        conn.commit()
        conn.close()
        
        print(f"\n✓ Import complete!")
        print(f"  Imported: {imported} vendors")
        print(f"  Skipped: {skipped} vendors")
        
        return True
    
    except Exception as e:
        print(f"ERROR: Import failed: {e}")
        return False

# ============================================
# VENDOR CSV IMPORT (Alternative)
# ============================================

def import_vendors_from_csv(csv_path: str):
    """Import vendors from CSV file"""
    import csv
    
    print(f"Importing vendors from: {csv_path}")
    
    try:
        # Connect to database
        db_path = Path(__file__).parent / "data" / "electro_tech.db"
        conn = sqlite3.connect(db_path)
        
        imported = 0
        skipped = 0
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                try:
                    conn.execute("""
                        INSERT OR REPLACE INTO vendors 
                        (vendor_id, vendor_name, mobile, email, whatsapp_number, 
                         address, vendor_type, products, status, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'active', CURRENT_TIMESTAMP)
                    """, (
                        row.get('vendor_id'),
                        row.get('vendor_name'),
                        row.get('mobile'),
                        row.get('email', ''),
                        row.get('whatsapp_number'),
                        row.get('address', ''),
                        row.get('vendor_type', 'Trader'),
                        row.get('products', '')
                    ))
                    imported += 1
                
                except Exception as e:
                    print(f"Warning: Failed to import {row.get('vendor_id')}: {e}")
                    skipped += 1
        
        conn.commit()
        conn.close()
        
        print(f"\n✓ Import complete!")
        print(f"  Imported: {imported} vendors")
        print(f"  Skipped: {skipped} vendors")
        
        return True
    
    except Exception as e:
        print(f"ERROR: Import failed: {e}")
        return False

# ============================================
# LIST VENDORS
# ============================================

def list_vendors():
    """List all vendors in database"""
    db_path = Path(__file__).parent / "data" / "electro_tech.db"
    conn = sqlite3.connect(db_path)
    
    cursor = conn.execute("""
        SELECT vendor_id, vendor_name, mobile, whatsapp_number, vendor_type, status
        FROM vendors
        ORDER BY vendor_id
    """)
    
    print("\n" + "="*80)
    print("VENDOR LIST")
    print("="*80)
    print(f"{'ID':<10} {'Name':<25} {'Mobile':<15} {'WhatsApp':<15} {'Type':<10} {'Status':<10}")
    print("-"*80)
    
    count = 0
    for row in cursor.fetchall():
        print(f"{row[0]:<10} {row[1]:<25} {row[2]:<15} {row[3]:<15} {row[4]:<10} {row[5]:<10}")
        count += 1
    
    print("-"*80)
    print(f"Total: {count} vendors")
    print("="*80 + "\n")
    
    conn.close()

# ============================================
# ADD SINGLE VENDOR
# ============================================

def add_vendor_interactive():
    """Add vendor through interactive CLI"""
    print("\n=== ADD NEW VENDOR ===\n")
    
    vendor_id = input("Vendor ID (e.g., VND006): ").strip()
    vendor_name = input("Vendor Name: ").strip()
    mobile = input("Mobile (e.g., 0300-1234567): ").strip()
    whatsapp = input("WhatsApp Number (e.g., +923001234567): ").strip()
    email = input("Email (optional): ").strip()
    address = input("Address: ").strip()
    vendor_type = input("Type (Importer/Trader): ").strip()
    products = input("Products (comma-separated): ").strip()
    
    # Validate
    if not all([vendor_id, vendor_name, mobile, whatsapp]):
        print("ERROR: Required fields missing!")
        return False
    
    # Insert
    try:
        db_path = Path(__file__).parent / "data" / "electro_tech.db"
        conn = sqlite3.connect(db_path)
        
        conn.execute("""
            INSERT INTO vendors 
            (vendor_id, vendor_name, mobile, email, whatsapp_number, 
             address, vendor_type, products, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'active', CURRENT_TIMESTAMP)
        """, (vendor_id, vendor_name, mobile, email, whatsapp, address, vendor_type, products))
        
        conn.commit()
        conn.close()
        
        print(f"\n✓ Vendor {vendor_id} added successfully!")
        return True
    
    except sqlite3.IntegrityError:
        print(f"\nERROR: Vendor {vendor_id} already exists!")
        return False
    except Exception as e:
        print(f"\nERROR: Failed to add vendor: {e}")
        return False

# ============================================
# GENERATE SAMPLE EXCEL TEMPLATE
# ============================================

def generate_excel_template():
    """Generate Excel template for vendor import"""
    try:
        import pandas as pd
    except ImportError:
        print("ERROR: pandas not installed!")
        return False
    
    # Sample data
    template_data = {
        'vendor_id': ['VND001', 'VND002', 'VND003'],
        'vendor_name': ['ABC Solar Traders', 'XYZ Energy Hub', 'Solar Solutions Pak'],
        'mobile': ['0300-1234567', '0321-9876543', '0333-5555555'],
        'whatsapp_number': ['+923001234567', '+923219876543', '+923335555555'],
        'email': ['abc@email.com', 'xyz@email.com', 'solar@email.com'],
        'address': ['Lahore', 'Karachi', 'Islamabad'],
        'vendor_type': ['Importer', 'Trader', 'Importer'],
        'products': ['Inverter,Solar Panel', 'Battery', 'Solar Panel,Battery']
    }
    
    df = pd.DataFrame(template_data)
    
    output_path = Path(__file__).parent / "vendor_template.xlsx"
    df.to_excel(output_path, index=False)
    
    print(f"\n✓ Template generated: {output_path}")
    print("\nFill in your vendor data and import using:")
    print(f"  python setup_utils.py --import-excel {output_path}")
    
    return True

# ============================================
# MAIN CLI
# ============================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Vendor Management Utilities')
    parser.add_argument('--import-excel', metavar='FILE', help='Import vendors from Excel')
    parser.add_argument('--import-csv', metavar='FILE', help='Import vendors from CSV')
    parser.add_argument('--list', action='store_true', help='List all vendors')
    parser.add_argument('--add', action='store_true', help='Add vendor interactively')
    parser.add_argument('--template', action='store_true', help='Generate Excel template')
    
    args = parser.parse_args()
    
    if args.import_excel:
        import_vendors_from_excel(args.import_excel)
    
    elif args.import_csv:
        import_vendors_from_csv(args.import_csv)
    
    elif args.list:
        list_vendors()
    
    elif args.add:
        add_vendor_interactive()
    
    elif args.template:
        generate_excel_template()
    
    else:
        parser.print_help()
        print("\nQuick start:")
        print("  1. Generate template: python setup_utils.py --template")
        print("  2. Fill in vendors in Excel")
        print("  3. Import: python setup_utils.py --import-excel vendor_template.xlsx")
        print("  4. List vendors: python setup_utils.py --list")

if __name__ == "__main__":
    main()
