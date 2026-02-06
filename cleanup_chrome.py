#!/usr/bin/env python3
"""
Chrome Cleanup Utility
Completely cleans Chrome processes and profile state before automation runs
"""

import os
import sys
import time
import shutil
from pathlib import Path
from datetime import datetime

def cleanup_chrome():
    """Clean up Chrome processes and profile"""
    print("=" * 80)
    print("CHROME CLEANUP UTILITY")
    print("=" * 80)
    
    # Step 1: Kill all Chrome processes
    print("\n[1] Terminating Chrome processes...")
    for attempt in range(3):
        try:
            os.system("taskkill /F /IM chrome.exe 2>nul > nul")
            os.system("taskkill /F /IM chromedriver.exe 2>nul > nul")
            os.system("taskkill /F /IM chrome.exe 2>nul > nul")
        except:
            pass
        time.sleep(1)
    print("    ✓ Chrome processes terminated")
    
    # Step 2: Clean Chrome profile
    print("\n[2] Cleaning Chrome profile...")
    chrome_profile = Path(__file__).parent / "chrome_profile"
    
    if chrome_profile.exists():
        try:
            # Remove lock files
            lock_patterns = [
                "Singleton", "SingletonLock", "SingletonSocket",
                ".lock", ".tmp", "DevToolsActivePort", "First Run"
            ]
            
            removed_count = 0
            for pattern in lock_patterns:
                for item in chrome_profile.rglob(f"*{pattern}*"):
                    try:
                        if item.is_file():
                            item.unlink(missing_ok=True)
                            removed_count += 1
                        elif item.is_dir():
                            shutil.rmtree(item, ignore_errors=True)
                            removed_count += 1
                    except:
                        pass
            
            # Remove Cache directory (can be very large and cause issues)
            cache_dir = chrome_profile / "Default" / "Cache"
            if cache_dir.exists():
                try:
                    shutil.rmtree(cache_dir, ignore_errors=True)
                    removed_count += 1
                    print(f"    ✓ Removed Cache directory ({cache_dir})")
                except:
                    pass
            
            # Remove Session Storage (preserves login state issues)
            session_dir = chrome_profile / "Default" / "Local Storage"
            if session_dir.exists():
                try:
                    shutil.rmtree(session_dir, ignore_errors=True)
                    removed_count += 1
                    print(f"    ✓ Removed Session Storage")
                except:
                    pass
            
            print(f"    ✓ Removed {removed_count} lock files and directories")
        except Exception as e:
            print(f"    ⚠ Error cleaning profile: {e}")
    else:
        print("    ℹ Chrome profile doesn't exist (fresh state)")
    
    # Step 3: Clean temp directories
    print("\n[3] Cleaning temporary Chrome directories...")
    temp_dir = Path(__file__).parent.parent / "Local Temp"
    chrome_temp_count = 0
    
    try:
        if temp_dir.exists():
            for item in temp_dir.glob("*chrome*"):
                try:
                    if item.is_dir():
                        shutil.rmtree(item, ignore_errors=True)
                        chrome_temp_count += 1
                except:
                    pass
    except:
        pass
    
    if chrome_temp_count > 0:
        print(f"    ✓ Removed {chrome_temp_count} temporary Chrome directories")
    
    # Step 4: System cache clear
    print("\n[4] Clearing system-level Chrome locks...")
    try:
        os.system("ipconfig /flushdns")
        print("    ✓ Flushed DNS cache")
    except:
        pass
    
    # Step 5: Final verification
    print("\n[5] Verifying cleanup...")
    result = os.popen("tasklist | findstr /I chrome").read()
    
    if result.strip():
        print(f"    ⚠ WARNING: Chrome still running:")
        print(f"    {result}")
        return False
    else:
        print("    ✓ No Chrome processes running")
    
    print("\n" + "=" * 80)
    print("✓ CLEANUP COMPLETE")
    print("=" * 80)
    print(f"Cleaned at: {datetime.now().isoformat()}")
    print("\nYou can now run: python run_all.py")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    success = cleanup_chrome()
    sys.exit(0 if success else 1)
