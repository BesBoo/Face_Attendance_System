# utils/logger.py

import logging
import os
from datetime import datetime

# Create logs directory if not exists
os.makedirs("logs", exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"logs/attendance_{datetime.now().strftime('%Y%m%d')}.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# Create loggers
app_logger = logging.getLogger("app")
system_logger = logging.getLogger("system")
user_logger = logging.getLogger("user")

def log_system_event(event_type, message):
    """Log system events"""
    try:
        system_logger.info(f"[{event_type}] {message}")
    except Exception as e:
        print(f"Logging error: {e}")

def log_user_action(action, details):
    """Log user actions"""
    try:
        user_logger.info(f"[{action}] {details}")
    except Exception as e:
        print(f"Logging error: {e}")

def log_error(error_type, message, exception=None):
    """Log errors"""
    try:
        error_msg = f"[{error_type}] {message}"
        if exception:
            error_msg += f" - Exception: {str(exception)}"
        app_logger.error(error_msg)
    except Exception as e:
        print(f"Logging error: {e}")

# Export functions
__all__ = ['app_logger', 'log_system_event', 'log_user_action', 'log_error']