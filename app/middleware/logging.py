"""Request logging middleware"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.utils.api_logger import APILogger
import time

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all requests"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request
        APILogger.log_request(request)
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log response
        APILogger.log_response(request, response.status_code, process_time)
        
        return response