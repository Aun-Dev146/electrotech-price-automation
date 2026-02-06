#!/usr/bin/env python3
"""
GOOGLE SHEETS CONNECTION SETUP GUIDE
Step-by-step instructions to connect to the provided Google Sheet
"""

def show_setup_instructions():
    """Display complete setup instructions"""
    instructions = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║         GOOGLE SHEETS LIVE REPORT SETUP - STEP BY STEP                      ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

YOUR GOOGLE SHEET:
─────────────────────────────────────────────────────────────────────────────
https://docs.google.com/spreadsheets/d/1PcC2KdA3VHf9EnyA4XzU_zWS7hLVpxDjkqwcCJGgFBs/edit?gid=0#gid=0

Sheet ID: 1PcC2KdA3VHf9EnyA4XzU_zWS7hLVpxDjkqwcCJGgFBs

═══════════════════════════════════════════════════════════════════════════════

STEP 1: SETUP GOOGLE CLOUD PROJECT
─────────────────────────────────────────────────────────────────────────────

1. Go to: https://console.cloud.google.com/

2. Create a new project:
   • Click "Select a Project" at top
   • Click "NEW PROJECT"
   • Name: "Electro Tech Price Report"
   • Click Create

3. Wait for project to be created, then select it

4. Enable APIs:
   • Click "Enable APIs and Services"
   • Search for "Google Sheets API"
   • Click on it, then "ENABLE"
   
   • Go back, search for "Google Drive API"
   • Click on it, then "ENABLE"

═══════════════════════════════════════════════════════════════════════════════

STEP 2: CREATE SERVICE ACCOUNT
─────────────────────────────────────────────────────────────────────────────

1. In Google Cloud Console:
   • Go to "Credentials" (left sidebar)
   • Click "Create Credentials"
   • Select "Service Account"

2. Fill in:
   • Service account name: "electro-tech-report"
   • Service account ID: (auto-filled)
   • Description: "For accessing Google Sheets and uploading price data"
   • Click "Create and Continue"

3. Grant permissions:
   • Select role: "Editor"
   • Click "Continue"
   • Click "Done"

═══════════════════════════════════════════════════════════════════════════════

STEP 3: CREATE AND DOWNLOAD JSON KEY
─────────────────────────────────────────────────────────────────────────────

1. Go to the service account you just created:
   • In Credentials page, find "Service Accounts"
   • Click on "electro-tech-report"

2. Go to "Keys" tab:
   • Click "Add Key"
   • Select "Create new key"
   • Choose "JSON"
   • Click "Create"

3. A JSON file will download automatically (google_credentials.json)

4. Move the file:
   • Save to your project folder: 
     C:\\Users\\pc\\Desktop\\Electro_tech_Whatsapp_Automation\\google_credentials.json

═══════════════════════════════════════════════════════════════════════════════

STEP 4: SHARE GOOGLE SHEET WITH SERVICE ACCOUNT
─────────────────────────────────────────────────────────────────────────────

1. Open the JSON file you downloaded:
   • Find the "client_email" field
   • Copy the email address
   • Example: electro-tech-report@your-project.iam.gserviceaccount.com

2. Go to your Google Sheet:
   https://docs.google.com/spreadsheets/d/1PcC2KdA3VHf9EnyA4XzU_zWS7hLVpxDjkqwcCJGgFBs/

3. Click "Share" (top right)

4. Paste the service account email:
   • Paste the email from step 1
   • Select "Editor" permission
   • Uncheck "Notify people"
   • Click Share

═══════════════════════════════════════════════════════════════════════════════

STEP 5: INSTALL REQUIRED PACKAGES
─────────────────────────────────────────────────────────────────────────────

Run this command:

pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client

═══════════════════════════════════════════════════════════════════════════════

STEP 6: TEST THE CONNECTION
─────────────────────────────────────────────────────────────────────────────

Run this command to setup headers in your Google Sheet:

python google_sheets_live_report.py \\
  --sheet-id 1PcC2KdA3VHf9EnyA4XzU_zWS7hLVpxDjkqwcCJGgFBs \\
  --setup

Expected output:
  ✓ Headers setup complete for sheet: Daily Report

═══════════════════════════════════════════════════════════════════════════════

STEP 7: PUSH YOUR PRICE DATA
─────────────────────────────────────────────────────────────────────────────

Once connection is working, push all your data:

python google_sheets_live_report.py \\
  --sheet-id 1PcC2KdA3VHf9EnyA4XzU_zWS7hLVpxDjkqwcCJGgFBs \\
  --all

This will:
  ✓ Setup professional headers
  ✓ Push all price data from your database
  ✓ Create a summary sheet
  ✓ Format everything nicely

═══════════════════════════════════════════════════════════════════════════════

WHAT YOUR GOOGLE SHEET WILL SHOW
─────────────────────────────────────────────────────────────────────────────

Tab 1: "Daily Report" (Main Data)
  ├─ Date
  ├─ Time  
  ├─ Vendor Name
  ├─ Product Category (Inverter, Solar Panel, Battery)
  ├─ Product Model
  ├─ Product Company
  ├─ Price (PKR)
  ├─ Unit
  ├─ Source
  └─ Status

Tab 2: "Summary" (Statistics)
  ├─ Date
  ├─ Total Active Vendors
  ├─ Records Collected Today
  ├─ Product Categories
  ├─ Average Price
  └─ Report Generated Time

═══════════════════════════════════════════════════════════════════════════════

AUTOMATIC DAILY UPDATES
─────────────────────────────────────────────────────────────────────────────

Add to your Windows Task Scheduler:

Python script: google_sheets_live_report.py
Command: 
  python C:\\Users\\pc\\Desktop\\Electro_tech_Whatsapp_Automation\\google_sheets_live_report.py \\
    --sheet-id 1PcC2KdA3VHf9EnyA4XzU_zWS7hLVpxDjkqwcCJGgFBs \\
    --all

Schedule: After WhatsApp data collection (after 8:00 AM daily)

Result: Google Sheet automatically updates with latest prices!

═══════════════════════════════════════════════════════════════════════════════

COMMANDS REFERENCE
─────────────────────────────────────────────────────────────────────────────

Setup headers only:
  python google_sheets_live_report.py --sheet-id <ID> --setup

Push data only:
  python google_sheets_live_report.py --sheet-id <ID> --push

Push summary only:
  python google_sheets_live_report.py --sheet-id <ID> --summary

Setup + Push everything:
  python google_sheets_live_report.py --sheet-id <ID> --all

═══════════════════════════════════════════════════════════════════════════════

TROUBLESHOOTING
─────────────────────────────────────────────────────────────────────────────

Problem: "Credentials file not found"
Solution: Make sure google_credentials.json is in the project folder

Problem: "Permission denied"
Solution: Make sure you shared the Google Sheet with the service account email

Problem: "API not enabled"
Solution: Go to Google Cloud console and enable Sheets API + Drive API

Problem: "Connection timeout"
Solution: Check internet connection and Google Cloud project status

═══════════════════════════════════════════════════════════════════════════════

SHARE WITH CEO
─────────────────────────────────────────────────────────────────────────────

Once everything is set up, share this link with CEO:

https://docs.google.com/spreadsheets/d/1PcC2KdA3VHf9EnyA4XzU_zWS7hLVpxDjkqwcCJGgFBs/

The CEO can:
  ✓ View live price data
  ✓ Filter by vendor, product, date
  ✓ Download as Excel
  ✓ See daily summary statistics
  ✓ Access from any device, anytime

No manual updates needed - it updates automatically!

═══════════════════════════════════════════════════════════════════════════════

Ready? Let's go! 🚀

Generated: February 2, 2026
Status: Complete & Ready to Deploy

"""
    print(instructions)

if __name__ == "__main__":
    show_setup_instructions()
