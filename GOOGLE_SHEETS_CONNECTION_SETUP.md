## Google Sheets Connection - Quick Start Guide

### 💰 Completely FREE Setup!

✅ **No costs whatsoever**
- Uses Google Cloud FREE tier
- 300+ API requests per minute included free
- Unlimited Google Sheets storage free
- No credit card charges

### Spreadsheet Configured
**URL:** https://docs.google.com/spreadsheets/d/1PcC2KdA3VHf9EnyA4XzU_zWS7hLVpxDjkqwcCJGgFBs/edit?usp=sharing&pli=1&authuser=0

**ID:** `1PcC2KdA3VHf9EnyA4XzU_zWS7hLVpxDjkqwcCJGgFBs`

---

## Setup Steps

### 1. Create Google Cloud Project
```
1. Go to https://console.cloud.google.com/
2. Click 'Select a Project' → 'NEW PROJECT'
3. Name: "Electro Tech Automation"
4. Click 'CREATE'
```

### 2. Enable APIs
```
1. Go to 'APIs & Services' → 'Library'
2. Search and enable:
   - Google Sheets API
   - Google Drive API
```

### 3. Create Service Account
```
1. Go to 'APIs & Services' → 'Credentials'
2. Click 'CREATE CREDENTIALS' → 'Service Account'
3. Service account name: "electro-tech-automation"
4. Click 'CREATE AND CONTINUE'
5. Grant 'Editor' role
6. Click 'CONTINUE' → 'DONE'
```

### 4. Create and Download API Key
```
1. In Credentials, click the service account
2. Go to 'Keys' tab
3. Click 'ADD KEY' → 'Create new key'
4. Select 'JSON' format
5. Click 'CREATE'
6. Save as 'google_credentials.json' in project root
```

### 5. Share Spreadsheet
```
1. Open the Google Sheet
2. Click 'Share' button
3. Copy service account email from JSON credentials file
4. Paste email in Share dialog
5. Give 'Editor' access
6. Click 'Share'
```

### 6. Verify Setup
```bash
python setup_google_sheets.py --verify
```

---

## Usage in Code

### Append Single Price Update
```python
from google_sheets_updates import append_price_update

append_price_update(
    vendor_name="Vendor Name",
    product="Product Model",
    price=5000,
    category="Electronics",
    status="Active"
)
```

### Append Multiple Updates
```python
from google_sheets_updates import append_batch_updates

updates = [
    {
        'vendor_name': 'Vendor 1',
        'product': 'Product A',
        'price': 5000,
        'category': 'Electronics',
        'status': 'Active'
    },
    {
        'vendor_name': 'Vendor 2',
        'product': 'Product B',
        'price': 8000,
        'category': 'Components',
        'status': 'Active'
    }
]

successful, failed = append_batch_updates(updates)
print(f"Successful: {successful}, Failed: {failed}")
```

### Log Price Changes
```python
from google_sheets_updates import append_price_change

append_price_change(
    product="GPU RTX 3080",
    old_price=150000,
    new_price=145000,
    vendor="TechStore",
    notes="Price drop detected"
)
```

### Get Latest Updates
```python
from google_sheets_updates import get_latest_updates

# Get latest 50 updates from Daily Report
updates = get_latest_updates(sheet_name="Daily Report", max_rows=50)
for update in updates:
    print(f"{update['Date']} - {update['Vendor Name']}: Rs {update['Price (PKR)']}")
```

---

## Sheet Structure

### Daily Report
| Column | Description |
|--------|-------------|
| Date | YYYY-MM-DD format |
| Time | HH:MM:SS format |
| Vendor Name | Vendor name |
| Product | Product model |
| Price (PKR) | Price in Pakistani Rupees |
| Category | Product category |
| Status | Active/Inactive/Error |
| Last Updated | ISO timestamp |

### Vendor List
| Column | Description |
|--------|-------------|
| Vendor ID | Unique ID |
| Vendor Name | Full vendor name |
| Mobile | Contact number |
| WhatsApp | WhatsApp number |
| Email | Email address |
| Status | Active/Inactive |
| Last Contact | Last contact date |

### Price Updates
| Column | Description |
|--------|-------------|
| Timestamp | When price changed |
| Product | Product name |
| Old Price | Previous price |
| New Price | New price |
| Change % | Percentage change |
| Vendor | Vendor name |
| Notes | Additional notes |

---

## Integration with Automation

The automation will now automatically:
1. ✅ Append price updates to **Daily Report** sheet
2. ✅ Log price changes to **Price Updates** sheet
3. ✅ Update vendor list to **Vendor List** sheet
4. ✅ Timestamp all entries
5. ✅ Provide real-time CEO visibility

---

## Troubleshooting

### Error: "Credentials file not found"
```
→ Complete Step 4: Download and save google_credentials.json
```

### Error: "Permission denied"
```
→ Complete Step 5: Share spreadsheet with service account email
```

### Error: "Spreadsheet not found"
```
→ Verify spreadsheet ID in config.ini
→ Verify service account has Editor access
```

### Error: "Google libraries not installed"
```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

---

## Configuration File

Edit `config.ini` to customize:
```ini
[google_sheets]
spreadsheet_id = 1PcC2KdA3VHf9EnyA4XzU_zWS7hLVpxDjkqwcCJGgFBs
credentials_file = ./google_credentials.json
daily_report_sheet = Daily Report
vendor_list_sheet = Vendor List
price_updates_sheet = Price Updates
auto_append = yes
timestamp_enabled = yes
```

---

## Support
For issues or questions, refer to Google Sheets API documentation:
https://developers.google.com/sheets/api
