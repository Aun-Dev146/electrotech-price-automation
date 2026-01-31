#!/usr/bin/env python3
"""
PRODUCTION READINESS VERIFICATION SCRIPT
Verifies all components are production-ready before CEO deployment
"""

import sys
from pathlib import Path
import sqlite3
from datetime import datetime

def check_file_exists(filepath, description):
    """Check if required file exists"""
    if Path(filepath).exists():
        print(f"✓ {description}")
        return True
    else:
        print(f"✗ {description} - FILE NOT FOUND: {filepath}")
        return False

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 9:
        print(f"✓ Python version OK: {version.major}.{version.minor}")
        return True
    else:
        print(f"✗ Python version too old: {version.major}.{version.minor} (need 3.9+)")
        return False

def check_packages():
    """Check if required packages are installed"""
    packages = [
        'selenium', 'webdriver_manager', 'pytesseract', 'PIL',
        'pdfplumber', 'openpyxl', 'pandas'
    ]
    
    all_ok = True
    for package in packages:
        try:
            __import__(package)
            print(f"✓ Package installed: {package}")
        except ImportError:
            print(f"✗ Package missing: {package}")
            all_ok = False
    
    return all_ok

def check_database():
    """Check if database is initialized"""
    db_path = Path("data/electro_tech.db")
    if not db_path.exists():
        print(f"✗ Database not initialized: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check tables
        tables = ['vendors', 'products', 'daily_prices']
        for table in tables:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            if cursor.fetchone():
                print(f"✓ Database table exists: {table}")
            else:
                print(f"✗ Database table missing: {table}")
                return False
        
        # Check for active vendors
        cursor.execute("SELECT COUNT(*) FROM vendors WHERE status='active'")
        vendor_count = cursor.fetchone()[0]
        if vendor_count > 0:
            print(f"✓ Active vendors in database: {vendor_count}")
        else:
            print(f"✗ No active vendors in database (add with: python setup_utils.py --add-vendor)")
            return False
        
        conn.close()
        return True
    
    except Exception as e:
        print(f"✗ Database check failed: {e}")
        return False

def check_configuration():
    """Check if configuration file exists and is valid"""
    config_path = Path("config.ini")
    if not config_path.exists():
        print(f"✗ Configuration file not found: {config_path}")
        return False
    
    try:
        # Read and parse config
        import configparser
        config = configparser.ConfigParser()
        config.read(config_path)
        
        # Check required sections
        required_sections = ['whatsapp', 'ceo_notification', 'vendors']
        for section in required_sections:
            if config.has_section(section):
                print(f"✓ Configuration section exists: [{section}]")
            else:
                print(f"✗ Configuration section missing: [{section}]")
                return False
        
        return True
    
    except Exception as e:
        print(f"✗ Configuration check failed: {e}")
        return False

def check_directories():
    """Check if all required directories exist"""
    directories = [
        'data/whatsapp_messages/text',
        'data/whatsapp_messages/images',
        'data/whatsapp_messages/pdfs',
        'output',
        'logs',
        'backups'
    ]
    
    all_ok = True
    for directory in directories:
        path = Path(directory)
        if path.exists():
            print(f"✓ Directory exists: {directory}")
        else:
            path.mkdir(parents=True, exist_ok=True)
            print(f"✓ Directory created: {directory}")
    
    return all_ok

def check_whatsapp_session():
    """Check if WhatsApp session is saved"""
    profile_path = Path("chrome_profile/Default")
    if profile_path.exists():
        print(f"✓ WhatsApp session found (ready for use)")
        return True
    else:
        print(f"⚠ WhatsApp session not found (run: python whatsapp_automation.py --setup)")
        return False

def main():
    """Run all checks"""
    print("\n" + "="*80)
    print("ELECTRO TECH - PRODUCTION READINESS VERIFICATION")
    print("="*80 + "\n")
    
    results = {
        "Python Version": check_python_version(),
        "Required Packages": check_packages(),
        "Configuration File": check_configuration(),
        "Directories": check_directories(),
        "Database": check_database(),
        "WhatsApp Session": check_whatsapp_session(),
        "System Files": (
            check_file_exists("run_all.py", "Main orchestrator") and
            check_file_exists("price_intelligence.py", "Price engine") and
            check_file_exists("whatsapp_automation.py", "WhatsApp automation") and
            check_file_exists("production_utils.py", "Production utilities")
        )
    }
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    for check_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {check_name}")
    
    # Overall status
    all_ok = all(results.values())
    
    print("\n" + "="*80)
    if all_ok:
        print("✓ SYSTEM IS PRODUCTION-READY FOR CEO DEPLOYMENT")
        print("="*80)
        print("\nNext steps:")
        print("1. Run test: python run_all.py")
        print("2. Verify reports in output/ folder")
        print("3. Check CEO received WhatsApp message")
        print("4. Deploy to scheduler (Task Scheduler or Cron)")
        return 0
    else:
        print("✗ SYSTEM NOT READY - ISSUES FOUND")
        print("="*80)
        print("\nFix issues above, then run this script again")
        return 1

if __name__ == "__main__":
    sys.exit(main())
