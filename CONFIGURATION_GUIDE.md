# ⚙️ CONFIGURATION GUIDE - NO HARDCODING POLICY

**IMPORTANT:** The system uses **NO HARDCODED VALUES**. All configuration is loaded from `config.ini`.

---

## 🚫 What's NOT Hardcoded

The following values **MUST** be configured in `config.ini`, NOT in code:

- ❌ CEO contact name
- ❌ CEO phone number
- ❌ Vendor phone numbers
- ❌ Vendor names
- ❌ Chrome profile path
- ❌ Delay timings
- ❌ Timeout values
- ❌ Report time
- ❌ Any real phone numbers
- ❌ Any real contact information

---

## ✅ Configuration Sources

### 1. **Database (Recommended)**
Vendors are loaded from the **database**:
```sql
SELECT phone_number, name FROM vendors WHERE status='active'
```

**File:** `run_all.py` (ProductionOrchestrator class)

### 2. **config.ini (Static Configuration)**

#### [ceo_notification] Section
```ini
[ceo_notification]
# CEO WhatsApp contact name (exact match in phone)
ceo_contact_name = Your Real CEO Name

# Fallback: CEO phone number (if contact not found)
ceo_phone_number = +92-XXXXXXXXX

# Daily report time (24-hour format)
report_time = 08:30

# Send report as: whatsapp/email/both
send_via = whatsapp

# Attach PDF: yes/no
attach_pdf = yes
```

#### [whatsapp] Section
```ini
[whatsapp]
persistent_session = yes
chrome_profile_path = ./chrome_profile
qr_timeout = 120
page_load_timeout = 60
message_timeout = 30
human_delay_min = 2
human_delay_max = 5
```

### 3. **Database Setup**
Add vendors to database:
```sql
INSERT INTO vendors (phone_number, name, contact_type, status, created_at)
VALUES ('+92-300-XXXXXXX', 'Vendor Name', 'contact', 'active', datetime('now'));
```

---

## 🔧 How to Configure

### Step 1: Update config.ini
Edit `config.ini` and replace placeholder values:

```ini
[ceo_notification]
ceo_contact_name = CEO Your Company Name
ceo_phone_number = +92-XXXXXXXXX
report_time = 09:00
```

### Step 2: Add Vendors to Database
Run the setup script:
```bash
python setup_utils.py --add-vendor
```

Or use Python directly:
```python
from setup_utils import VendorManager
manager = VendorManager()
manager.add_vendor(
    phone_number="+92-300-XXXXXXX",
    name="Your Vendor Name",
    contact_type="contact"
)
```

### Step 3: Verify Configuration
Run the verification script:
```bash
python verify_production_ready.py
```

Should show:
```
✓ CEO contact configured: Yes
✓ Vendors configured: X active vendors
✓ Configuration valid: Yes
```

---

## 🔄 Code Changes Made

### whatsapp_automation.py
**Before (Hardcoded):**
```python
CEO_NAME = "CEO Electro Tech"  # ❌ Hardcoded
CEO_PHONE = "+92 300 1234567"  # ❌ Hardcoded
HUMAN_DELAY_MIN = 2            # ❌ Hardcoded
```

**After (Configured):**
```python
# Load from config.ini
_config = configparser.ConfigParser()
_config.read('config.ini')

CEO_NAME = _config.get('ceo_notification', 'ceo_contact_name', fallback='CEO')
CEO_PHONE = _config.get('ceo_notification', 'ceo_phone_number', fallback='')
HUMAN_DELAY_MIN = float(_config.get('whatsapp', 'human_delay_min', fallback='2'))
```

---

## 📋 Configuration Checklist

Before deploying, ensure:

- [ ] config.ini exists in project root
- [ ] [ceo_notification] section has real values
- [ ] CEO contact name matches phone's contact name exactly
- [ ] Database has at least 1 active vendor
- [ ] All vendors have real phone numbers
- [ ] verify_production_ready.py shows all ✓

---

## 🚨 Important Notes

1. **Phone Numbers:** Use international format: `+92-300-XXXXXXX`
2. **Contact Name:** Must match EXACTLY as saved in phone
3. **Never commit sensitive data:** Git ignores config.ini (use .gitignore)
4. **Fallback values:** Config file has sensible defaults if value missing
5. **Database priority:** Database vendors override any hardcoded lists

---

## 🔒 Security Best Practices

✅ **Store sensitive data in:**
- config.ini (local, not in git)
- Environment variables
- Secrets management system

❌ **NEVER store in:**
- Source code (.py files)
- Version control (git)
- Log files
- Documentation

---

## 📞 Getting Real Data

### CEO Contact
1. Open WhatsApp on phone
2. Find your CEO contact
3. Copy EXACT name
4. Paste in config.ini as `ceo_contact_name`

### Vendor Information
1. Get vendor contact details
2. Add to database via:
   - `setup_utils.py --add-vendor`
   - Manual database insert
   - API endpoint
3. Verify status = 'active'
4. Run `verify_production_ready.py`

---

## ✅ Verification

Run after configuration:
```bash
python verify_production_ready.py
```

Check output for:
```
✓ Python version: 3.12
✓ All 8 packages installed
✓ Configuration valid
✓ CEO contact configured
✓ Vendors configured: X active vendors
✓ WhatsApp session ready
✓ System ready for production
```

---

## 🆘 Troubleshooting

### "CEO contact not found"
- **Cause:** Contact name doesn't match phone exactly
- **Fix:** Update `ceo_contact_name` in config.ini to match phone

### "Vendor not found"
- **Cause:** Vendor not in database with status='active'
- **Fix:** Add vendor to database and set status='active'

### "Configuration file not found"
- **Cause:** config.ini missing
- **Fix:** Create config.ini from template or run `setup_utils.py`

### "Invalid configuration"
- **Cause:** Missing required fields
- **Fix:** Run `python verify_production_ready.py` for details

---

**System Status:** ✅ No hardcoding - All configuration from config.ini and database

*Last Updated: 2026-02-01*
