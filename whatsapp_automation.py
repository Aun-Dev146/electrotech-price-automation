#!/usr/bin/env python3
"""
WHATSAPP WEB AUTOMATION - PRODUCTION
Handles message collection and report sending

Uses Selenium for stable, ban-safe automation
"""

import time
import os
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Tuple

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.keys import Keys
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
except ImportError:
    print("ERROR: Selenium not installed!")
    print("Run: pip install selenium webdriver-manager")
    exit(1)

logger = logging.getLogger("WhatsAppAuto")

# ============================================
# CONFIGURATION
# ============================================

class WAConfig:
    """WhatsApp automation configuration"""
    
    # Paths
    BASE_DIR = Path(__file__).parent.absolute()
    CHROME_PROFILE = BASE_DIR / "chrome_profile"
    OUTPUT_DIR = BASE_DIR / "data" / "whatsapp_messages"
    
    # WhatsApp Web
    WA_WEB_URL = "https://web.whatsapp.com"
    
    # Timing (in seconds) - Production safe values
    HUMAN_DELAY_MIN = 2
    HUMAN_DELAY_MAX = 5
    PAGE_LOAD_TIMEOUT = 60
    ELEMENT_TIMEOUT = 30
    
    # CEO contact
    CEO_NAME = "CEO Electro Tech"  # WhatsApp contact name
    CEO_PHONE = "+92 300 1234567"  # Fallback

# ============================================
# WHATSAPP WEB DRIVER
# ============================================

class WhatsAppDriver:
    """Selenium driver for WhatsApp Web"""
    
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.driver = None
        self._setup_driver()
    
    def _setup_driver(self):
        """Initialize Chrome with WhatsApp-safe options"""
        options = Options()
        
        # Use persistent profile to keep logged in
        options.add_argument(f"--user-data-dir={WAConfig.CHROME_PROFILE}")
        options.add_argument("--profile-directory=Default")
        
        # Stealth settings
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Performance
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        
        if self.headless:
            options.add_argument("--headless")
        
        # Start driver
        self.driver = webdriver.Chrome(options=options)
        self.driver.maximize_window()
        
        logger.info("Chrome driver initialized")
    
    def _human_delay(self, min_sec=None, max_sec=None):
        """Random delay to mimic human behavior"""
        import random
        min_sec = min_sec or WAConfig.HUMAN_DELAY_MIN
        max_sec = max_sec or WAConfig.HUMAN_DELAY_MAX
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)
    
    def open_whatsapp(self):
        """Open WhatsApp Web and wait for load"""
        logger.info("Opening WhatsApp Web...")
        self.driver.get(WAConfig.WA_WEB_URL)
        
        # Wait for either QR code or chat to load
        try:
            # Check if already logged in
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-testid='chat-list']"))
            )
            logger.info("WhatsApp Web loaded successfully (logged in)")
            return True
        
        except TimeoutException:
            # Need to scan QR code
            try:
                qr_code = self.driver.find_element(By.CSS_SELECTOR, "canvas")
                logger.warning("QR CODE DETECTED - Please scan with your phone!")
                print("\n" + "="*60)
                print("QR CODE DETECTED")
                print("Please scan the QR code with your WhatsApp mobile app")
                print("Waiting for 2 minutes...")
                print("="*60 + "\n")
                
                # Wait for login (2 minutes)
                WebDriverWait(self.driver, 120).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-testid='chat-list']"))
                )
                logger.info("Successfully logged in!")
                return True
            
            except TimeoutException:
                logger.error("Login timeout - QR code not scanned")
                return False
    
    def find_chat(self, contact_name: str) -> bool:
        """Find and open a specific chat"""
        try:
            # Click search box
            search_box = WebDriverWait(self.driver, WAConfig.ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[contenteditable='true'][data-tab='3']"))
            )
            search_box.click()
            self._human_delay(1, 2)
            
            # Type contact name
            search_box.send_keys(contact_name)
            self._human_delay(2, 3)
            
            # Click first result
            first_result = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-testid='cell-frame-container']"))
            )
            first_result.click()
            self._human_delay(1, 2)
            
            logger.info(f"Opened chat with: {contact_name}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to find chat {contact_name}: {e}")
            return False
    
    def get_unread_messages(self, vendor_numbers: List[str]) -> List[Tuple[str, str]]:
        """
        Get unread messages ONLY from specific vendor numbers/groups
        IMPORTANT: Only processes chats that match vendor_numbers list
        
        Args:
            vendor_numbers: List of EXACT vendor phone numbers/group names to monitor
                           Example: ['+923001234567', '+923219876543', 'Vendor Group Name']
        
        Returns: [(vendor_number, message_text), ...]
        """
        messages = []
        
        logger.info(f"Looking for messages from {len(vendor_numbers)} specific vendors only")
        logger.info(f"Whitelist: {vendor_numbers}")
        
        try:
            # For each vendor, specifically search for and open their chat
            for vendor_identifier in vendor_numbers:
                try:
                    logger.info(f"Searching for vendor: {vendor_identifier}")
                    
                    # Search for this specific vendor
                    if not self.find_chat(vendor_identifier):
                        logger.warning(f"Could not find chat for: {vendor_identifier}")
                        continue
                    
                    self._human_delay(2, 3)
                    
                    # Check if this chat has unread messages
                    try:
                        unread_badge = self.driver.find_elements(
                            By.CSS_SELECTOR, 
                            "span[data-testid='icon-unread-count']"
                        )
                        
                        if not unread_badge:
                            logger.info(f"No unread messages from: {vendor_identifier}")
                            continue
                    
                    except:
                        logger.info(f"Could not check unread status for: {vendor_identifier}")
                        continue
                    
                    # Extract messages from THIS vendor only
                    try:
                        # Get all message elements in the current chat
                        message_elements = self.driver.find_elements(
                            By.CSS_SELECTOR, 
                            "div.message-in span.selectable-text"
                        )
                        
                        if not message_elements:
                            logger.info(f"No messages found in chat: {vendor_identifier}")
                            continue
                        
                        # Extract last 10 messages from this vendor
                        vendor_messages = []
                        for msg_elem in message_elements[-10:]:
                            text = msg_elem.text.strip()
                            if text:  # Only add non-empty messages
                                vendor_messages.append(text)
                        
                        if vendor_messages:
                            logger.info(f"Found {len(vendor_messages)} messages from {vendor_identifier}")
                            for text in vendor_messages:
                                messages.append((vendor_identifier, text))
                    
                    except Exception as e:
                        logger.error(f"Error extracting messages from {vendor_identifier}: {e}")
                        continue
                
                except Exception as e:
                    logger.error(f"Error processing vendor {vendor_identifier}: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error in get_unread_messages: {e}")
        
        logger.info(f"Total messages collected from {len(set(v for v, _ in messages))} vendors: {len(messages)} messages")
        return messages
    
    def send_message(self, contact_name: str, message: str, attachment_path: Path = None) -> bool:
        """Send message to contact, optionally with attachment"""
        try:
            # Find and open chat
            if not self.find_chat(contact_name):
                return False
            
            # Send attachment if provided
            if attachment_path and attachment_path.exists():
                try:
                    # Click attachment button
                    attach_btn = self.driver.find_element(By.CSS_SELECTOR, "div[title='Attach']")
                    attach_btn.click()
                    self._human_delay(1, 2)
                    
                    # Click document option
                    doc_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='file']")
                    doc_input.send_keys(str(attachment_path.absolute()))
                    self._human_delay(3, 5)
                    
                    # Click send
                    send_btn = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "span[data-testid='send']"))
                    )
                    send_btn.click()
                    self._human_delay(2, 3)
                    
                    logger.info(f"Sent attachment: {attachment_path.name}")
                
                except Exception as e:
                    logger.error(f"Failed to send attachment: {e}")
            
            # Send text message
            if message:
                # Find message input
                msg_box = WebDriverWait(self.driver, WAConfig.ELEMENT_TIMEOUT).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[contenteditable='true'][data-tab='10']"))
                )
                msg_box.click()
                self._human_delay(1, 1.5)
                
                # Type message
                msg_box.send_keys(message)
                self._human_delay(1, 2)
                
                # Send
                msg_box.send_keys(Keys.ENTER)
                self._human_delay(2, 3)
                
                logger.info(f"Sent message to: {contact_name}")
            
            return True
        
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False
    
    def close(self):
        """Close browser"""
        if self.driver:
            self.driver.quit()
            logger.info("Browser closed")

# ============================================
# MESSAGE COLLECTOR
# ============================================

class MessageCollector:
    """
    Collect vendor messages and save to files
    
    SECURITY: Only collects from SPECIFIC vendor chats/groups specified in whitelist
    Does NOT scrape all WhatsApp data
    """
    
    def __init__(self, vendor_numbers: List[str]):
        """
        Initialize with specific vendor identifiers
        
        Args:
            vendor_numbers: List of EXACT vendor phone numbers or group names to monitor
                           Example: ['+923001234567', '+923219876543', 'Solar Vendors Group']
        """
        if not vendor_numbers:
            raise ValueError("ERROR: No vendor numbers provided! Must specify which chats to monitor.")
        
        self.vendor_numbers = vendor_numbers
        self.wa = WhatsAppDriver(headless=False)  # Visible for first setup
        
        logger.info("="*80)
        logger.info("MESSAGE COLLECTOR INITIALIZED")
        logger.info(f"Monitoring {len(vendor_numbers)} specific vendors ONLY:")
        for i, vendor in enumerate(vendor_numbers, 1):
            logger.info(f"  {i}. {vendor}")
        logger.info("="*80)
        
        # Ensure output directories exist
        WAConfig.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        (WAConfig.OUTPUT_DIR / "text").mkdir(exist_ok=True)
        (WAConfig.OUTPUT_DIR / "images").mkdir(exist_ok=True)
        (WAConfig.OUTPUT_DIR / "pdfs").mkdir(exist_ok=True)
    
    def collect_daily_messages(self) -> int:
        """
        Collect unread messages ONLY from specified vendor chats
        
        IMPORTANT: This will ONLY process chats/groups explicitly listed.
        All other chats are completely ignored.
        
        Returns: Number of messages collected
        """
        logger.info("="*80)
        logger.info("STARTING MESSAGE COLLECTION FROM SPECIFIC VENDORS")
        logger.info(f"Will only monitor: {self.vendor_numbers}")
        logger.info("="*80)
        
        # Open WhatsApp
        if not self.wa.open_whatsapp():
            logger.error("Failed to open WhatsApp")
            return 0
        
        # Get unread messages ONLY from vendor_numbers
        messages = self.wa.get_unread_messages(self.vendor_numbers)
        
        # Save messages to files
        count = 0
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        
        for vendor, text in messages:
            # Clean vendor name for filename
            vendor_clean = "".join(c for c in vendor if c.isalnum() or c in " -").strip()
            vendor_clean = vendor_clean.replace(" ", "_")
            
            # Save text
            filename = f"{timestamp}_{vendor_clean}.txt"
            filepath = WAConfig.OUTPUT_DIR / "text" / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"Vendor: {vendor}\n")
                f.write(f"Time: {datetime.now().isoformat()}\n")
                f.write(f"{'='*60}\n\n")
                f.write(text)
            
            count += 1
            logger.info(f"Saved message from {vendor}")
        
        logger.info(f"Collected {count} messages")
        return count
    
    def close(self):
        """Close WhatsApp session"""
        self.wa.close()

# ============================================
# REPORT SENDER
# ============================================

class ReportSender:
    """Send daily report to CEO"""
    
    def __init__(self, ceo_contact: str):
        self.ceo_contact = ceo_contact
        self.wa = WhatsAppDriver(headless=False)
    
    def send_daily_report(self, summary_text: str, pdf_path: Path = None) -> bool:
        """Send report to CEO"""
        logger.info("Sending daily report to CEO...")
        
        # Open WhatsApp
        if not self.wa.open_whatsapp():
            logger.error("Failed to open WhatsApp")
            return False
        
        # Send message with attachment
        success = self.wa.send_message(
            contact_name=self.ceo_contact,
            message=summary_text,
            attachment_path=pdf_path
        )
        
        if success:
            logger.info("Daily report sent successfully!")
        else:
            logger.error("Failed to send daily report")
        
        return success
    
    def close(self):
        """Close WhatsApp session"""
        self.wa.close()

# ============================================
# CLI INTERFACE
# ============================================

def main():
    """Command-line interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description='WhatsApp Automation for Electro Tech')
    parser.add_argument('--setup', action='store_true', help='First-time setup (scan QR)')
    parser.add_argument('--collect', action='store_true', help='Collect vendor messages')
    parser.add_argument('--send', metavar='MESSAGE', help='Send test message')
    parser.add_argument('--dry-run', action='store_true', help='Test without sending')
    
    args = parser.parse_args()
    
    if args.setup:
        print("=== WHATSAPP WEB SETUP ===")
        print("This will open WhatsApp Web for first-time login")
        print("Please scan the QR code with your phone when prompted")
        print()
        input("Press Enter to continue...")
        
        wa = WhatsAppDriver(headless=False)
        wa.open_whatsapp()
        
        print("\n✓ Setup complete!")
        print("WhatsApp Web session saved. You won't need to scan QR again.")
        print("Browser will stay open for 30 seconds so you can verify...")
        time.sleep(30)
        
        wa.close()
    
    elif args.collect:
        print("=== COLLECTING VENDOR MESSAGES ===")
        
        # Load vendor numbers (in production, load from database)
        vendor_numbers = ["+923001234567", "+923219876543"]
        
        collector = MessageCollector(vendor_numbers)
        count = collector.collect_daily_messages()
        
        print(f"\n✓ Collected {count} messages")
        print(f"Messages saved to: {WAConfig.OUTPUT_DIR / 'text'}")
        
        collector.close()
    
    elif args.send:
        print("=== SENDING TEST MESSAGE ===")
        
        sender = ReportSender(WAConfig.CEO_NAME)
        success = sender.send_daily_report(args.send)
        
        if success:
            print("\n✓ Message sent successfully")
        else:
            print("\n✗ Failed to send message")
        
        sender.close()
    
    elif args.dry_run:
        print("=== DRY RUN (NO MESSAGES SENT) ===")
        print("Opening WhatsApp Web to verify connection...")
        
        wa = WhatsAppDriver(headless=False)
        if wa.open_whatsapp():
            print("\n✓ WhatsApp Web connection successful!")
            print("You can see your chats. No messages will be sent.")
            print("Browser will stay open for inspection...")
            input("Press Enter to close...")
        else:
            print("\n✗ Failed to connect to WhatsApp Web")
        
        wa.close()
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
