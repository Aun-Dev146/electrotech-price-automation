#!/usr/bin/env python3
"""
ELECTRO TECH - DAILY AUTOMATION ORCHESTRATOR
Master script that runs the complete workflow
Production-grade with error handling, monitoring, and audit logging

This is what gets scheduled to run daily at 8:00 AM
Version: 2.0.0 PRODUCTION
"""

import sys
import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple

# Setup paths
BASE_DIR = Path(__file__).parent.absolute()
sys.path.insert(0, str(BASE_DIR))

# Import modules
try:
    from price_intelligence import AutomationEngine, Config as PIConfig, DatabaseManager
    from whatsapp_automation import MessageCollector, ReportSender, WAConfig
    from production_utils import (
        ExecutionContext, CircuitBreaker, AuditLogger, HealthCheck,
        retry_with_backoff, RetryConfig, DataValidator
    )
except ImportError as e:
    print(f"CRITICAL ERROR: Failed to import required modules: {e}")
    print("Ensure all required files are in the same directory:")
    print("  - price_intelligence.py")
    print("  - whatsapp_automation.py")
    print("  - production_utils.py")
    sys.exit(1)

# ============================================
# PRODUCTION ORCHESTRATOR WITH MONITORING
# ============================================

class ProductionOrchestrator:
    """
    Enterprise-grade orchestrator with:
    - Comprehensive error handling and recovery
    - Execution context tracking
    - Circuit breakers for cascading failures
    - Audit logging for compliance
    - Health monitoring
    - Automatic retries with exponential backoff
    """
    
    def __init__(self):
        self.start_time = datetime.now()
        self.execution_context = ExecutionContext()
        self.setup_logging()
        self.setup_audit_logging()
        self.setup_circuit_breakers()
        self.db = DatabaseManager(PIConfig.DB_PATH)
        self.logger = logging.getLogger("ProductionOrchestrator")
    
    def setup_logging(self):
        """Configure production-grade logging"""
        log_dir = PIConfig.LOG_DIR
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f"daily_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # File handler (detailed)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        
        # Console handler (concise)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        
        # Root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        root_logger.handlers.clear()
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        
        self.logger = logging.getLogger("ProductionOrchestrator")
        self.logger.info("=" * 100)
        self.logger.info("ELECTRO TECH - DAILY PRICE INTELLIGENCE AUTOMATION")
        self.logger.info(f"Execution started at {self.start_time.isoformat()}")
        self.logger.info("=" * 100)
    
    def setup_audit_logging(self):
        """Setup audit trail for compliance"""
        audit_dir = PIConfig.LOG_DIR / "audit"
        audit_dir.mkdir(parents=True, exist_ok=True)
        audit_file = audit_dir / f"audit_{datetime.now().strftime('%Y%m')}.jsonl"
        
        self.audit_logger = AuditLogger(audit_file)
        self.audit_logger.log_access(
            user="SYSTEM",
            action="EXECUTION_START",
            resource="DailyOrchestrator",
            status="INITIATED",
            details=f"Execution ID: {self.execution_context.execution_id}"
        )
    
    def setup_circuit_breakers(self):
        """Setup circuit breakers for critical operations"""
        self.whatsapp_breaker = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=300,  # 5 minutes
            expected_exception=Exception
        )
        
        self.database_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60,  # 1 minute
            expected_exception=Exception
        )
    
    def get_vendor_numbers(self) -> list:
        """Get active vendor WhatsApp numbers with validation"""
        self.logger.info("Loading active vendors from database...")
        
        try:
            cursor = self.db.conn.execute("""
                SELECT vendor_id, vendor_name, whatsapp_number
                FROM vendors 
                WHERE status = 'active' AND whatsapp_number IS NOT NULL
                ORDER BY vendor_id
            """)
            
            vendors = cursor.fetchall()
            self.logger.info(f"[OK] Loaded {len(vendors)} active vendors")
            
            # Validate and normalize phone numbers
            valid_vendors = []
            for vendor_id, vendor_name, whatsapp_number in vendors:
                if DataValidator.validate_phone_number(whatsapp_number):
                    normalized = DataValidator.normalize_phone_number(whatsapp_number)
                    valid_vendors.append((vendor_id, vendor_name, normalized))
                    self.logger.debug(f"  - {vendor_name} ({vendor_id}): {normalized}")
                else:
                    self.logger.warning(f"  - SKIPPED: Invalid phone for {vendor_name}: {whatsapp_number}")
                    self.execution_context.add_warning(f"Invalid phone number for vendor {vendor_id}")
            
            if not valid_vendors:
                raise ValueError("No valid active vendors found in database")
            
            return valid_vendors
        
        except Exception as e:
            self.logger.error(f"Failed to load vendors: {e}", exc_info=True)
            self.execution_context.add_error(f"Vendor loading failed: {str(e)}")
            raise
    
    @retry_with_backoff(RetryConfig(max_attempts=3, initial_delay=5))
    def step1_collect_messages(self, vendors: list) -> Tuple[bool, int]:
        """
        Step 1: Collect vendor messages from WhatsApp with retry logic
        Returns: (success, message_count)
        """
        self.logger.info("\n" + "=" * 100)
        self.logger.info("STEP 1: COLLECTING VENDOR MESSAGES FROM WHATSAPP")
        self.logger.info("=" * 100)
        
        try:
            vendor_numbers = [v[2] for v in vendors]  # Normalized phone numbers
            vendor_names = {v[2]: v[1] for v in vendors}  # Map for logging
            
            self.logger.info(f"Monitoring {len(vendor_numbers)} specific vendors ONLY:")
            for i, (vendor_id, vendor_name, phone) in enumerate(vendors, 1):
                self.logger.info(f"  {i}. {vendor_name} ({phone})")
            
            collector = MessageCollector(vendor_numbers)
            message_count = collector.collect_daily_messages()
            collector.close()
            
            self.logger.info(f"[OK] Message collection successful: {message_count} messages collected")
            self.execution_context.add_metric("messages_collected", message_count)
            self.audit_logger.log_access(
                user="SYSTEM", action="MESSAGE_COLLECTION", resource="WhatsApp",
                status="SUCCESS", details=f"Collected {message_count} messages"
            )
            
            return True, message_count
        
        except Exception as e:
            self.logger.error(f"[FAILED] Message collection failed: {e}", exc_info=True)
            self.execution_context.add_error(f"Message collection failed: {str(e)}")
            self.audit_logger.log_access(
                user="SYSTEM", action="MESSAGE_COLLECTION", resource="WhatsApp",
                status="FAILED", details=str(e)
            )
            raise
    
    @retry_with_backoff(RetryConfig(max_attempts=2, initial_delay=3))
    def step2_process_data(self) -> Tuple[bool, int]:
        """
        Step 2: Extract prices and populate database
        Returns: (success, price_count)
        """
        self.logger.info("\n" + "=" * 100)
        self.logger.info("STEP 2: PROCESSING PRICE DATA EXTRACTION")
        self.logger.info("=" * 100)
        
        try:
            engine = AutomationEngine()
            price_count = engine.process_whatsapp_messages()
            
            self.logger.info(f"[OK] Price processing successful: {price_count} prices extracted")
            self.execution_context.add_metric("prices_extracted", price_count)
            self.audit_logger.log_access(
                user="SYSTEM", action="PRICE_EXTRACTION", resource="Database",
                status="SUCCESS", details=f"Extracted {price_count} prices"
            )
            
            return True, price_count
        
        except Exception as e:
            self.logger.error(f"[FAILED] Price processing failed: {e}", exc_info=True)
            self.execution_context.add_error(f"Price processing failed: {str(e)}")
            self.audit_logger.log_access(
                user="SYSTEM", action="PRICE_EXTRACTION", resource="Database",
                status="FAILED", details=str(e)
            )
            raise
    
    @retry_with_backoff(RetryConfig(max_attempts=2, initial_delay=3))
    def step3_generate_reports(self) -> Tuple[bool, Optional[Path], Optional[Path]]:
        """
        Step 3: Generate daily reports
        Returns: (success, summary_path, detailed_path)
        """
        self.logger.info("\n" + "=" * 100)
        self.logger.info("STEP 3: GENERATING DAILY REPORTS")
        self.logger.info("=" * 100)
        
        try:
            engine = AutomationEngine()
            summary_path, detailed_path = engine.generate_daily_report()
            
            if not summary_path or not detailed_path:
                raise ValueError("Report generation returned None paths")
            
            # Verify files exist
            if not summary_path.exists():
                raise FileNotFoundError(f"Summary report not created: {summary_path}")
            if not detailed_path.exists():
                raise FileNotFoundError(f"Detailed report not created: {detailed_path}")
            
            summary_size = summary_path.stat().st_size
            detailed_size = detailed_path.stat().st_size
            
            self.logger.info(f"[OK] Reports generated successfully:")
            self.logger.info(f"  - Summary: {summary_path} ({summary_size} bytes)")
            self.logger.info(f"  - Detailed: {detailed_path} ({detailed_size} bytes)")
            
            self.execution_context.add_metric("summary_report_size", summary_size)
            self.execution_context.add_metric("detailed_report_size", detailed_size)
            
            self.audit_logger.log_access(
                user="SYSTEM", action="REPORT_GENERATION", resource="FileSystem",
                status="SUCCESS", details=f"2 reports generated"
            )
            
            return True, summary_path, detailed_path
        
        except Exception as e:
            self.logger.error(f"[FAILED] Report generation failed: {e}", exc_info=True)
            self.execution_context.add_error(f"Report generation failed: {str(e)}")
            self.audit_logger.log_access(
                user="SYSTEM", action="REPORT_GENERATION", resource="FileSystem",
                status="FAILED", details=str(e)
            )
            return False, None, None
    
    @retry_with_backoff(RetryConfig(max_attempts=3, initial_delay=5))
    def step4_send_to_ceo(self, summary_path: Path, detailed_path: Path) -> bool:
        """
        Step 4: Send report to CEO via WhatsApp
        Returns: success status
        """
        self.logger.info("\n" + "=" * 100)
        self.logger.info("STEP 4: SENDING DAILY REPORT TO CEO")
        self.logger.info("=" * 100)
        
        try:
            if not summary_path.exists():
                raise FileNotFoundError(f"Summary file not found: {summary_path}")
            
            if not detailed_path.exists():
                raise FileNotFoundError(f"Detailed file not found: {detailed_path}")
            
            # Read summary
            with open(summary_path, 'r', encoding='utf-8') as f:
                summary_text = f.read()
            
            if not summary_text.strip():
                raise ValueError("Summary report is empty")
            
            # Send via WhatsApp
            self.logger.info(f"Attempting to send to CEO: {WAConfig.CEO_NAME}")
            sender = ReportSender(WAConfig.CEO_NAME)
            success = sender.send_daily_report(summary_text, detailed_path)
            sender.close()
            
            if success:
                self.logger.info("[OK] Report sent to CEO successfully")
                self.audit_logger.log_access(
                    user="SYSTEM", action="REPORT_SEND", resource="WhatsApp",
                    status="SUCCESS", details=f"Sent to {WAConfig.CEO_NAME}"
                )
                return True
            else:
                raise RuntimeError("Report send operation returned False")
        
        except Exception as e:
            self.logger.error(f"[FAILED] Report sending failed: {e}", exc_info=True)
            self.execution_context.add_error(f"Report sending failed: {str(e)}")
            self.audit_logger.log_access(
                user="SYSTEM", action="REPORT_SEND", resource="WhatsApp",
                status="FAILED", details=str(e)
            )
            raise
    
    def run(self) -> bool:
        """Execute complete daily workflow with production error handling"""
        workflow_success = True
        
        try:
            # Load vendors first (critical step)
            vendors = self.get_vendor_numbers()
            self.execution_context.add_metric("vendor_count", len(vendors))
            
            # Step 1: Collect messages (non-critical failure - continue if WhatsApp has issues)
            try:
                collect_success, message_count = self.step1_collect_messages(vendors)
            except Exception as e:
                self.logger.warning(f"Message collection had errors, but continuing with analysis...")
                collect_success = False
                message_count = 0
            
            # Step 2: Process data (critical)
            try:
                process_success, price_count = self.step2_process_data()
                if not process_success:
                    workflow_success = False
            except Exception as e:
                self.logger.error(f"Data processing critical failure, cannot continue...")
                workflow_success = False
                raise
            
            # Step 3: Generate reports (critical)
            try:
                report_success, summary_path, detailed_path = self.step3_generate_reports()
                if not report_success:
                    workflow_success = False
            except Exception as e:
                self.logger.error(f"Report generation critical failure, cannot continue...")
                workflow_success = False
                raise
            
            # Step 4: Send to CEO (important but non-critical)
            try:
                if summary_path and detailed_path:
                    send_success = self.step4_send_to_ceo(summary_path, detailed_path)
                    if not send_success:
                        self.logger.warning("Report not sent to CEO, but reports were generated")
                else:
                    self.logger.error("Cannot send reports - paths missing")
            except Exception as e:
                self.logger.warning(f"Failed to send report to CEO: {e}")
                # Don't fail workflow - report is still available
        
        except Exception as e:
            self.logger.error(f"CRITICAL ERROR in workflow: {e}", exc_info=True)
            self.execution_context.add_error(f"Workflow critical error: {str(e)}")
            workflow_success = False
        
        finally:
            # Cleanup
            try:
                if hasattr(self, 'db'):
                    self.db.close()
            except:
                pass
            
            # Generate final report
            self._generate_final_report(workflow_success)
        
        return workflow_success
    
    def _generate_final_report(self, success: bool):
        """Generate final execution report"""
        self.execution_context.mark_complete("SUCCESS" if success else "FAILURE")
        
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        summary = self.execution_context.get_summary()
        
        self.logger.info("\n" + "=" * 100)
        self.logger.info("EXECUTION SUMMARY")
        self.logger.info("=" * 100)
        self.logger.info(f"Execution ID: {self.execution_context.execution_id}")
        self.logger.info(f"Status: {summary['status']}")
        self.logger.info(f"Duration: {duration:.2f} seconds")
        self.logger.info(f"Errors: {summary['error_count']}")
        self.logger.info(f"Warnings: {summary['warning_count']}")
        self.logger.info(f"Metrics: {json.dumps(summary['metrics'], indent=2)}")
        
        if self.execution_context.errors:
            self.logger.error("ERRORS:")
            for error in self.execution_context.errors:
                self.logger.error(f"  - {error['error']}")
        
        self.logger.info("=" * 100)
        
        # Log to audit
        self.audit_logger.log_access(
            user="SYSTEM",
            action="EXECUTION_COMPLETE",
            resource="DailyOrchestrator",
            status=summary['status'],
            details=f"Duration: {duration:.2f}s, Errors: {summary['error_count']}, Warnings: {summary['warning_count']}"
        )

# ============================================
# ENTRY POINT
# ============================================


def main():
    """
    Main entry point - suitable for scheduled execution
    Exit codes:
      0 = Success
      1 = Partial failure (reports generated but not sent)
      2 = Critical failure (cannot generate reports)
    """
    try:
        orchestrator = ProductionOrchestrator()
        success = orchestrator.run()
        
        # Determine exit code based on success
        if success:
            exit_code = 0
        else:
            # Check if we at least generated reports
            output_dir = PIConfig.OUTPUT_DIR
            if list(output_dir.glob("daily_summary_*.txt")):
                exit_code = 1  # Partial success
            else:
                exit_code = 2  # Critical failure
        
        sys.exit(exit_code)
    
    except KeyboardInterrupt:
        print("\n[INTERRUPTED] Execution interrupted by user")
        sys.exit(3)
    
    except Exception as e:
        print(f"[FATAL] Unhandled exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(2)

if __name__ == "__main__":
    main()
