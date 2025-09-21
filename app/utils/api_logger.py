"""
Centralized API logging utilities for request/response tracking and error handling.
"""

import time
import json
import traceback
from typing import Any, Dict, Optional
from functools import wraps
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from config.logging_config import logger


class APILogger:
    """Centralized API logging utility"""
    
    @staticmethod
    def log_request(request: Request, user_id: Optional[int] = None):
        """Log incoming API request"""
        logger.info(
            f"📥 REQUEST | {request.method} {request.url.path} | "
            f"User: {user_id or 'Anonymous'} | "
            f"IP: {request.client.host if request.client else 'Unknown'}"
        )
    
    @staticmethod
    def log_success(endpoint: str, user_id: Optional[int] = None, data: Any = None, duration: float = 0):
        """Log successful API response"""
        data_info = ""
        if data:
            if isinstance(data, dict):
                data_info = f" | Data: {len(data)} fields"
            elif isinstance(data, list):
                data_info = f" | Data: {len(data)} items"
            else:
                data_info = f" | Data: {type(data).__name__}"
        
        logger.info(
            f"✅ SUCCESS | {endpoint} | "
            f"User: {user_id or 'Anonymous'} | "
            f"Duration: {duration:.3f}s{data_info}"
        )
    
    @staticmethod
    def log_error(endpoint: str, error: Exception, user_id: Optional[int] = None, duration: float = 0):
        """Log API error"""
        error_type = type(error).__name__
        error_msg = str(error)
        
        logger.error(
            f"❌ ERROR | {endpoint} | "
            f"User: {user_id or 'Anonymous'} | "
            f"Error: {error_type} - {error_msg} | "
            f"Duration: {duration:.3f}s"
        )
        
        # Log full traceback for debugging
        logger.debug(f"Full traceback for {endpoint}: {traceback.format_exc()}")
    
    @staticmethod
    def log_auth_attempt(email: str, success: bool, ip: str = "Unknown"):
        """Log authentication attempts"""
        status = "✅ SUCCESS" if success else "❌ FAILED"
        logger.info(f"🔐 AUTH {status} | Email: {email} | IP: {ip}")
    
    @staticmethod
    def log_database_operation(operation: str, table: str, success: bool, user_id: Optional[int] = None):
        """Log database operations"""
        status = "✅" if success else "❌"
        logger.info(
            f"🗄️ DB {status} | {operation.upper()} on {table} | "
            f"User: {user_id or 'System'}"
        )


def log_endpoint(endpoint_name: str = None):
    """Decorator to add logging to API endpoints"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            endpoint = endpoint_name or func.__name__
            user_id = None
            
            # Try to extract user_id from kwargs
            if 'current_user' in kwargs:
                user_id = getattr(kwargs['current_user'], 'id', None)
            
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                APILogger.log_success(endpoint, user_id, result, duration)
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                APILogger.log_error(endpoint, e, user_id, duration)
                raise
        
        return wrapper
    return decorator


def log_user_action(action: str, user_id: int, details: str = ""):
    """Log user actions"""
    logger.info(f"👤 USER ACTION | {action} | User: {user_id} | {details}")

def log_security_event(event: str, user_id: Optional[int] = None, ip: str = "Unknown"):
    """Log security-related events"""
    logger.warning(f"🔒 SECURITY | {event} | User: {user_id or 'Anonymous'} | IP: {ip}")

def log_system_event(event: str, details: str = ""):
    """Log system events"""
    logger.info(f"⚙️ SYSTEM | {event} | {details}")