#!/usr/bin/env python3
"""
INTEGRATION HELPER
Shows how to integrate Google Sheets updates into existing automation
"""

# ============================================
# EXAMPLE 1: Integrate into whatsapp_automation.py
# ============================================

"""
Add to your existing automation script:

from google_sheets_updates import append_price_update, append_batch_updates

# After collecting prices from WhatsApp
prices_data = [
    {
        'vendor_name': 'Tech Store',
        'product': 'GPU RTX 4090',
        'price': 450000,
        'category': 'Graphics Card',
        'status': 'Active'
    },
    # ... more prices
]

# Push to Google Sheets
successful, failed = append_batch_updates(prices_data)
print(f"Google Sheets: {successful} updated, {failed} failed")
"""

# ============================================
# EXAMPLE 2: Integrate into price_intelligence.py
# ============================================

"""
Add to price tracking:

from google_sheets_updates import append_price_change

# When price changes detected
if new_price != old_price:
    append_price_change(
        product=product_name,
        old_price=old_price,
        new_price=new_price,
        vendor=vendor_name,
        notes=f"Detected at {datetime.now()}"
    )
"""

# ============================================
# EXAMPLE 3: Add to run_all.py
# ============================================

"""
# In run_all.py, add Google Sheets verification

from google_sheets_updates import get_sheets_service
import sys

# Check Google Sheets connection before running
service = get_sheets_service()
if not service:
    print("WARNING: Google Sheets not connected")
    print("Run: python setup_google_sheets.py --verify")
    # Continue anyway, but log this
else:
    print("✓ Google Sheets connected and ready")
"""

# ============================================
# COMPLETE INTEGRATION EXAMPLE
# ============================================

def integrated_automation_example():
    """
    Complete example showing Google Sheets integration
    """
    from google_sheets_updates import (
        append_price_update,
        append_batch_updates,
        append_price_change,
        get_latest_updates,
        update_vendor_list
    )
    from datetime import datetime
    
    # 1. After scraping prices
    print("\n[1] Pushing scraped prices to Google Sheets...")
    prices = [
        {
            'vendor_name': 'ElectroMart',
            'product': 'i7 13700K',
            'price': 85000,
            'category': 'CPU',
            'status': 'Active'
        },
        {
            'vendor_name': 'TechHub',
            'product': 'RTX 4080',
            'price': 420000,
            'category': 'GPU',
            'status': 'Active'
        }
    ]
    
    successful, failed = append_batch_updates(prices)
    print(f"   → Pushed {successful} updates")
    
    # 2. Log price changes
    print("\n[2] Logging detected price changes...")
    append_price_change(
        product='i5 13600K',
        old_price=65000,
        new_price=62000,
        vendor='TechZone',
        notes='Price reduction'
    )
    print("   → Price change logged")
    
    # 3. Update vendor list
    print("\n[3] Updating vendor list...")
    vendors = [
        {
            'vendor_id': 'V001',
            'vendor_name': 'ElectroMart',
            'mobile': '+92-300-1234567',
            'whatsapp_number': '+92-300-1234567',
            'email': 'electromart@example.com',
            'status': 'Active'
        }
    ]
    update_vendor_list(vendors)
    print("   → Vendor list updated")
    
    # 4. Retrieve latest data
    print("\n[4] Retrieving latest updates from Google Sheets...")
    updates = get_latest_updates(sheet_name="Daily Report", max_rows=10)
    print(f"   → Retrieved {len(updates)} recent updates")
    for update in updates[:3]:
        print(f"      • {update.get('Vendor Name', 'N/A')}: Rs {update.get('Price (PKR)', 'N/A')}")


# ============================================
# TEST CONNECTION
# ============================================

if __name__ == "__main__":
    import sys
    
    print("\n" + "="*60)
    print("GOOGLE SHEETS INTEGRATION - EXAMPLES")
    print("="*60)
    
    # Check if we can import the module
    try:
        from google_sheets_updates import get_sheets_service
        
        service = get_sheets_service()
        if service:
            print("\n✅ Google Sheets module is ready!")
            print("\nRun this example to test:")
            print("  python integration_examples.py --test")
            
            if len(sys.argv) > 1 and sys.argv[1] == "--test":
                print("\nRunning integration test...\n")
                integrated_automation_example()
        else:
            print("\n⚠ Google Sheets not yet configured")
            print("\nSetup steps:")
            print("  1. python setup_google_sheets.py")
            print("  2. Follow the instructions")
            print("  3. python setup_google_sheets.py --verify")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure google_sheets_updates.py is in the project directory")
    
    print("\n" + "="*60)
