#!/usr/bin/env python3
"""
QUICK REFERENCE - GOOGLE SHEETS INTEGRATION
Copy & paste commands from here
"""

SETUP_COMMANDS = """
═════════════════════════════════════════════════════════════
INSTALLATION
═════════════════════════════════════════════════════════════

Install Google libraries:
  pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client

═════════════════════════════════════════════════════════════
FIRST TIME SETUP
═════════════════════════════════════════════════════════════

Setup headers (creates columns):
  python google_sheets_live_report.py --sheet-id 1PcC2KdA3VHf9EnyA4XzU_zWS7hLVpxDjkqwcCJGgFBs --setup

Setup everything (headers + data + summary):
  python google_sheets_live_report.py --sheet-id 1PcC2KdA3VHf9EnyA4XzU_zWS7hLVpxDjkqwcCJGgFBs --all

═════════════════════════════════════════════════════════════
DAILY COMMANDS
═════════════════════════════════════════════════════════════

Push price data to Google Sheet:
  python google_sheets_live_report.py --sheet-id 1PcC2KdA3VHf9EnyA4XzU_zWS7hLVpxDjkqwcCJGgFBs --push

Update summary statistics:
  python google_sheets_live_report.py --sheet-id 1PcC2KdA3VHf9EnyA4XzU_zWS7hLVpxDjkqwcCJGgFBs --summary

Do both (push + summary):
  python google_sheets_live_report.py --sheet-id 1PcC2KdA3VHf9EnyA4XzU_zWS7hLVpxDjkqwcCJGgFBs --all

═════════════════════════════════════════════════════════════
HELP
═════════════════════════════════════════════════════════════

Show setup instructions:
  python GOOGLE_SHEETS_SETUP_GUIDE.py

═════════════════════════════════════════════════════════════
GOOGLE SHEET
═════════════════════════════════════════════════════════════

Your Google Sheet:
  https://docs.google.com/spreadsheets/d/1PcC2KdA3VHf9EnyA4XzU_zWS7hLVpxDjkqwcCJGgFBs/

Sheet ID (use in commands):
  1PcC2KdA3VHf9EnyA4XzU_zWS7hLVpxDjkqwcCJGgFBs

═════════════════════════════════════════════════════════════
TASK SCHEDULER (Windows) - Run daily at 8:30 AM
═════════════════════════════════════════════════════════════

Program:
  C:\\Python\\python.exe

Arguments:
  C:\\Users\\pc\\Desktop\\Electro_tech_Whatsapp_Automation\\google_sheets_live_report.py --sheet-id 1PcC2KdA3VHf9EnyA4XzU_zWS7hLVpxDjkqwcCJGgFBs --all

Trigger:
  Daily at 08:30 AM

═════════════════════════════════════════════════════════════
CRON (Linux/Mac) - Run daily at 8:30 AM
═════════════════════════════════════════════════════════════

30 8 * * * cd /path/to/project && python google_sheets_live_report.py --sheet-id 1PcC2KdA3VHf9EnyA4XzU_zWS7hLVpxDjkqwcCJGgFBs --all

═════════════════════════════════════════════════════════════
CREDENTIALS SETUP
═════════════════════════════════════════════════════════════

1. Go to https://console.cloud.google.com/
2. Create project
3. Enable Google Sheets API
4. Enable Google Drive API
5. Create Service Account (Editor)
6. Create & download JSON key
7. Save as google_credentials.json in project folder
8. Copy service account email
9. Go to Google Sheet
10. Click Share
11. Paste email
12. Give Editor permission
13. Done!

═════════════════════════════════════════════════════════════
FILE LOCATIONS
═════════════════════════════════════════════════════════════

Main script:
  google_sheets_live_report.py

Credentials (you create this):
  google_credentials.json

Setup guide:
  GOOGLE_SHEETS_SETUP_GUIDE.py

Reference docs:
  GOOGLE_SHEETS_CONNECTION.md
  GOOGLE_SHEETS_INTEGRATION.md
  FINAL_SETUP_SUMMARY.md

═════════════════════════════════════════════════════════════
"""

if __name__ == "__main__":
    print(SETUP_COMMANDS)
