#!/usr/bin/env python3
"""
PRODUCTION UTILITIES - ERROR HANDLING, VALIDATION, MONITORING
Enterprise-grade utilities for production deployment
"""

import time
import logging
import functools
import hashlib
import json
from datetime import datetime, timedelta
from typing import Optional, Callable, Any
from pathlib import Path
import re

logger = logging.getLogger("ProductionUtils")

# ============================================
# RETRY LOGIC WITH EXPONENTIAL BACKOFF
# ============================================

class RetryConfig:
    """Configuration for retry behavior"""
    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_multiplier: float = 2.0,
        jitter: bool = True
    ):
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.backoff_multiplier = backoff_multiplier
        self.jitter = jitter

def retry_with_backoff(config: RetryConfig = None):
    """
    Decorator for automatic retry with exponential backoff
    
    Usage:
        @retry_with_backoff(RetryConfig(max_attempts=3))
        def risky_function():
            # Something that might fail
            pass
    """
    if config is None:
        config = RetryConfig()
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            delay = config.initial_delay
            
            for attempt in range(1, config.max_attempts + 1):
                try:
                    logger.debug(f"Attempt {attempt}/{config.max_attempts} for {func.__name__}")
                    return func(*args, **kwargs)
                
                except Exception as e:
                    last_exception = e
                    
                    if attempt < config.max_attempts:
                        # Calculate delay with jitter
                        jitter_factor = 1.0
                        if config.jitter:
                            import random
                            jitter_factor = random.uniform(0.8, 1.2)
                        
                        actual_delay = min(delay * jitter_factor, config.max_delay)
                        
                        logger.warning(
                            f"{func.__name__} failed (attempt {attempt}/{config.max_attempts}): {str(e)}. "
                            f"Retrying in {actual_delay:.1f}s..."
                        )
                        
                        time.sleep(actual_delay)
                        delay *= config.backoff_multiplier
                    else:
                        logger.error(
                            f"{func.__name__} failed after {config.max_attempts} attempts: {str(e)}"
                        )
            
            raise last_exception
        
        return wrapper
    return decorator

# ============================================
# CIRCUIT BREAKER PATTERN
# ============================================

class CircuitBreakerState:
    """Circuit breaker states"""
    CLOSED = "CLOSED"      # Normal operation
    OPEN = "OPEN"          # Failing, reject requests
    HALF_OPEN = "HALF_OPEN"  # Testing if service recovered

class CircuitBreaker:
    """
    Circuit breaker for preventing cascading failures
    
    Usage:
        breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=60)
        
        @breaker.call
        def risky_api_call():
            # Code that might fail
            pass
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitBreakerState.CLOSED
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        
        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitBreakerState.HALF_OPEN
                logger.info(f"Circuit breaker entering HALF_OPEN state (testing recovery)")
            else:
                raise Exception(
                    f"Circuit breaker is OPEN. Service unavailable. "
                    f"Retry in {self._time_until_retry()}s"
                )
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        
        except self.expected_exception as e:
            self._on_failure()
            
            if self.state == CircuitBreakerState.OPEN:
                logger.error(f"Circuit breaker OPEN: {str(e)}")
                raise Exception(f"Service circuit breaker is open: {str(e)}")
            
            raise
    
    def _on_success(self):
        """Handle successful call"""
        self.failure_count = 0
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.state = CircuitBreakerState.CLOSED
            logger.info("Circuit breaker recovered, returning to CLOSED state")
    
    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN
            logger.error(
                f"Circuit breaker OPEN after {self.failure_count} failures. "
                f"Will retry in {self.recovery_timeout}s"
            )
    
    def _should_attempt_reset(self) -> bool:
        """Check if recovery timeout has passed"""
        if self.last_failure_time is None:
            return False
        
        elapsed = (datetime.now() - self.last_failure_time).total_seconds()
        return elapsed >= self.recovery_timeout
    
    def _time_until_retry(self) -> int:
        """Calculate seconds until retry is allowed"""
        if self.last_failure_time is None:
            return self.recovery_timeout
        
        elapsed = (datetime.now() - self.last_failure_time).total_seconds()
        remaining = max(0, int(self.recovery_timeout - elapsed))
        return remaining

# ============================================
# DATA VALIDATION
# ============================================

class DataValidator:
    """Validate and sanitize data before storage"""
    
    # Regex patterns
    PHONE_PATTERN = r"^\+?92[-\s]?3\d{2}[-\s]?\d{7}$"  # Pakistani format
    PRICE_PATTERN = r"(?:Rs\.?|PKR|रु\.?)\s*([0-9,]+(?:\.[0-9]{2})?)"
    EMAIL_PATTERN = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    
    @staticmethod
    def validate_phone_number(phone: str) -> bool:
        """Validate Pakistani phone number format"""
        if not phone:
            return False
        
        # Clean number
        cleaned = re.sub(r"[^\d+]", "", phone)
        
        # Check length and pattern
        return bool(re.match(DataValidator.PHONE_PATTERN, cleaned))
    
    @staticmethod
    def normalize_phone_number(phone: str) -> str:
        """Normalize phone number to standard format"""
        if not phone:
            return None
        
        # Remove all non-digits except +
        cleaned = re.sub(r"[^\d+]", "", phone)
        
        # Ensure starts with +92
        if not cleaned.startswith("+"):
            if cleaned.startswith("0"):
                cleaned = "+92" + cleaned[1:]
            elif cleaned.startswith("92"):
                cleaned = "+" + cleaned
            else:
                cleaned = "+92" + cleaned
        
        return cleaned
    
    @staticmethod
    def validate_price(price: float, min_price: float = 100, max_price: float = 999999999) -> bool:
        """Validate price is within acceptable range"""
        try:
            price_float = float(price)
            return min_price <= price_float <= max_price
        except (TypeError, ValueError):
            return False
    
    @staticmethod
    def extract_price_from_text(text: str) -> Optional[float]:
        """Extract price from text using regex"""
        if not text:
            return None
        
        match = re.search(DataValidator.PRICE_PATTERN, text)
        if match:
            price_str = match.group(1).replace(",", "")
            try:
                return float(price_str)
            except ValueError:
                return None
        
        return None
    
    @staticmethod
    def validate_vendor_data(vendor_dict: dict) -> tuple[bool, list]:
        """
        Validate vendor dictionary
        Returns: (is_valid, list_of_errors)
        """
        errors = []
        
        # Validate vendor_id
        if not vendor_dict.get("vendor_id"):
            errors.append("vendor_id is required")
        
        # Validate vendor_name
        if not vendor_dict.get("vendor_name"):
            errors.append("vendor_name is required")
        
        # Validate WhatsApp number
        if vendor_dict.get("whatsapp_number"):
            if not DataValidator.validate_phone_number(vendor_dict["whatsapp_number"]):
                errors.append(f"Invalid WhatsApp number format: {vendor_dict['whatsapp_number']}")
        
        # Validate email (if provided)
        if vendor_dict.get("email"):
            if not re.match(DataValidator.EMAIL_PATTERN, vendor_dict["email"]):
                errors.append(f"Invalid email format: {vendor_dict['email']}")
        
        # Validate status
        if vendor_dict.get("status") not in ["active", "inactive", "pending"]:
            errors.append(f"Invalid status: {vendor_dict.get('status')}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def sanitize_text(text: str, max_length: int = 1000) -> str:
        """Sanitize text for database storage"""
        if not text:
            return ""
        
        # Remove null bytes
        text = text.replace("\x00", "")
        
        # Limit length
        text = text[:max_length]
        
        # Strip whitespace
        text = text.strip()
        
        return text

# ============================================
# HEALTH MONITORING
# ============================================

class HealthCheck:
    """Monitor system health and generate alerts"""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path
        self.checks = {}
        self.last_check_time = None
    
    def register_check(self, name: str, check_func: Callable, critical: bool = False):
        """Register a health check function"""
        self.checks[name] = {
            "func": check_func,
            "critical": critical,
            "last_result": None,
            "last_run": None
        }
    
    def run_all_checks(self) -> dict:
        """Run all registered health checks"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "checks": {},
            "overall_status": "HEALTHY"
        }
        
        for check_name, check_data in self.checks.items():
            try:
                is_healthy = check_data["func"]()
                results["checks"][check_name] = {
                    "status": "PASS" if is_healthy else "FAIL",
                    "critical": check_data["critical"]
                }
                
                if not is_healthy and check_data["critical"]:
                    results["overall_status"] = "CRITICAL"
            
            except Exception as e:
                results["checks"][check_name] = {
                    "status": "ERROR",
                    "error": str(e),
                    "critical": check_data["critical"]
                }
                
                if check_data["critical"]:
                    results["overall_status"] = "CRITICAL"
        
        self.last_check_time = datetime.now()
        return results
    
    def is_healthy(self) -> bool:
        """Quick check if system is healthy"""
        results = self.run_all_checks()
        return results["overall_status"] != "CRITICAL"

# ============================================
# AUDIT LOGGING
# ============================================

class AuditLogger:
    """Log all critical operations for compliance and debugging"""
    
    def __init__(self, log_file: Path):
        self.log_file = log_file
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def log_access(self, user: str, action: str, resource: str, status: str, details: str = ""):
        """Log data access for audit trail"""
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "user": user,
            "action": action,
            "resource": resource,
            "status": status,
            "details": details
        }
        
        self._write_log(audit_entry)
        logger.info(f"AUDIT: {user} - {action} - {resource} - {status}")
    
    def log_data_modification(self, user: str, operation: str, table: str, record_id: str, old_data: dict, new_data: dict):
        """Log data modifications for compliance"""
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "user": user,
            "operation": operation,
            "table": table,
            "record_id": record_id,
            "old_data": old_data,
            "new_data": new_data,
            "change_hash": self._compute_hash({**old_data, **new_data})
        }
        
        self._write_log(audit_entry)
        logger.info(f"AUDIT: {operation} in {table} by {user}")
    
    def _write_log(self, entry: dict):
        """Write audit entry to log file"""
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")
    
    @staticmethod
    def _compute_hash(data: dict) -> str:
        """Compute hash of data for integrity checking"""
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()[:16]

# ============================================
# EXECUTION CONTEXT
# ============================================

class ExecutionContext:
    """Track execution context for debugging and monitoring"""
    
    def __init__(self, execution_id: str = None):
        self.execution_id = execution_id or self._generate_id()
        self.start_time = datetime.now()
        self.end_time = None
        self.status = "RUNNING"
        self.errors = []
        self.warnings = []
        self.metrics = {}
    
    def mark_complete(self, status: str = "SUCCESS"):
        """Mark execution as complete"""
        self.end_time = datetime.now()
        self.status = status
    
    def add_error(self, error: str):
        """Add error to context"""
        self.errors.append({"timestamp": datetime.now().isoformat(), "error": error})
    
    def add_warning(self, warning: str):
        """Add warning to context"""
        self.warnings.append({"timestamp": datetime.now().isoformat(), "warning": warning})
    
    def add_metric(self, name: str, value: Any):
        """Add performance metric"""
        self.metrics[name] = {"value": value, "timestamp": datetime.now().isoformat()}
    
    def get_duration(self) -> float:
        """Get execution duration in seconds"""
        end = self.end_time or datetime.now()
        return (end - self.start_time).total_seconds()
    
    def get_summary(self) -> dict:
        """Get execution summary"""
        return {
            "execution_id": self.execution_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.get_duration(),
            "status": self.status,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "metrics": self.metrics
        }
    
    @staticmethod
    def _generate_id() -> str:
        """Generate unique execution ID"""
        from uuid import uuid4
        return str(uuid4())[:8]
