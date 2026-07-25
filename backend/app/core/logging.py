"""
Oyster360 Structured Logging
Production-ready logging configuration
"""
import logging
import json
from datetime import datetime
from typing import Any, Dict
import sys

class StructuredLogger:
    def __init__(self, name: str = "oyster360"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Console handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(handler)
    
    def _log(self, level: str, message: str, extra: Dict[str, Any] = None):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "message": message,
            "service": "oyster360",
            **(extra or {})
        }
        self.logger.info(json.dumps(log_data))
    
    def info(self, message: str, **kwargs):
        self._log("INFO", message, kwargs)
    
    def error(self, message: str, **kwargs):
        self._log("ERROR", message, kwargs)
    
    def warning(self, message: str, **kwargs):
        self._log("WARNING", message, kwargs)
    
    def audit(self, action: str, user_id: int, resource: str, **kwargs):
        """Audit logging for security events"""
        self._log("AUDIT", f"User {user_id} performed {action} on {resource}", {
            "action": action,
            "user_id": user_id,
            "resource": resource,
            **kwargs
        })

# Global logger instance
logger = StructuredLogger()