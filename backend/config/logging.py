"""
Structured logging configuration
"""

import logging
import sys
from typing import Any, Dict
from .settings import settings


def setup_logging():
    """Configure structured logging for the application"""
    
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Silence noisy loggers
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)


def log_request(logger: logging.Logger, request_id: str, **kwargs: Any):
    """Log an API request with context"""
    logger.info(f"[{request_id}] Request: {kwargs}")


def log_response(logger: logging.Logger, request_id: str, **kwargs: Any):
    """Log an API response with context"""
    logger.info(f"[{request_id}] Response: {kwargs}")


def log_error(logger: logging.Logger, request_id: str, error: Exception, **kwargs: Any):
    """Log an error with context"""
    logger.error(f"[{request_id}] Error: {type(error).__name__}: {str(error)}", extra=kwargs)
