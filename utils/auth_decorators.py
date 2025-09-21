"""
Authorization decorators and utilities for role-based access control.
"""

from functools import wraps
from typing import Callable, List, Optional
from fastapi import HTTPException, status, Depends
from app.core.security import get_current_user
from app.models.user import User
from utils.api_logger import APILogger
import logging

logger = logging.getLogger(__name__)

def require_roles(required_roles: List[str], allow_self: bool = False):
    """
    Decorator to require specific roles for endpoint access.
    
    Args:
        required_roles: List of required roles ('admin', 'chef', 'decision_maker', 'family_member')
        allow_self: Allow access if user is accessing their own resources
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current user from kwargs (injected by FastAPI dependency)
            current_user = None
            for key, value in kwargs.items():
                if isinstance(value, User):
                    current_user = value
                    break
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # Check if user has required roles
            user_roles = _get_user_roles(current_user)
            has_required_role = any(role in user_roles for role in required_roles)
            
            if not has_required_role:
                # Log unauthorized access attempt
                APILogger.log_security_event(
                    "unauthorized_access_attempt",
                    f"User {current_user.id} attempted to access {func.__name__} without required roles",
                    {
                        "user_id": current_user.id,
                        "required_roles": required_roles,
                        "user_roles": user_roles,
                        "endpoint": func.__name__
                    }
                )
                
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Required roles: {', '.join(required_roles)}"
                )
            
            # Log successful authorization
            logger.debug(f"✅ Role authorization passed for user {current_user.id} | Roles: {user_roles}")
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator

def require_admin(func: Callable) -> Callable:
    """Decorator to require admin role"""
    return require_roles(['admin'])(func)

def require_chef(func: Callable) -> Callable:
    """Decorator to require chef role"""
    return require_roles(['chef', 'admin'])(func)

def require_family_decision_maker(func: Callable) -> Callable:
    """Decorator to require family decision maker role"""
    return require_roles(['decision_maker', 'admin'])(func)

def require_family_member(func: Callable) -> Callable:
    """Decorator to require family membership"""
    return require_roles(['family_member', 'decision_maker', 'chef', 'admin'])(func)

def require_self_or_admin(resource_user_id_param: str = "user_id"):
    """
    Decorator to allow access only to own resources or admin users.
    
    Args:
        resource_user_id_param: Parameter name that contains the resource owner's user ID
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = None
            resource_user_id = None
            
            # Get current user and resource user ID from kwargs
            for key, value in kwargs.items():
                if isinstance(value, User):
                    current_user = value
                elif key == resource_user_id_param:
                    resource_user_id = value
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # Check if user is admin or accessing own resource
            user_roles = _get_user_roles(current_user)
            is_admin = 'admin' in user_roles
            is_self = current_user.id == resource_user_id
            
            if not (is_admin or is_self):
                APILogger.log_security_event(
                    "unauthorized_resource_access",
                    f"User {current_user.id} attempted to access resource belonging to user {resource_user_id}",
                    {
                        "current_user_id": current_user.id,
                        "resource_user_id": resource_user_id,
                        "endpoint": func.__name__
                    }
                )
                
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: can only access own resources"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator

def require_family_access(allow_individual: bool = True):
    """
    Decorator to require family access or individual access based on resource ownership.
    
    Args:
        allow_individual: Whether to allow individual users to access their own resources
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = None
            
            # Get current user from kwargs
            for key, value in kwargs.items():
                if isinstance(value, User):
                    current_user = value
                    break
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            user_roles = _get_user_roles(current_user)
            
            # Admin always has access
            if 'admin' in user_roles:
                return await func(*args, **kwargs)
            
            # Check family access
            if current_user.is_family_account:
                return await func(*args, **kwargs)
            
            # Check individual access if allowed
            if allow_individual and not current_user.is_family_account:
                return await func(*args, **kwargs)
            
            # Access denied
            APILogger.log_security_event(
                "family_access_denied",
                f"User {current_user.id} denied family resource access",
                {
                    "user_id": current_user.id,
                    "is_family_account": current_user.is_family_account,
                    "endpoint": func.__name__
                }
            )
            
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Family account required for this resource"
            )
        
        return wrapper
    return decorator

def log_access_attempt(action: str):
    """Decorator to log access attempts for security auditing"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = None
            
            # Get current user from kwargs
            for key, value in kwargs.items():
                if isinstance(value, User):
                    current_user = value
                    break
            
            user_id = current_user.id if current_user else "anonymous"
            
            # Log access attempt
            APILogger.log_user_action(
                user_id,
                action,
                f"Accessed {func.__name__}",
                {"endpoint": func.__name__, "function": func.__qualname__}
            )
            
            logger.info(f"🔍 Access logged: User {user_id} | Action: {action} | Endpoint: {func.__name__}")
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator

def rate_limit_user(max_requests: int = 100, window_minutes: int = 60):
    """
    Decorator for user-based rate limiting.
    
    Args:
        max_requests: Maximum requests allowed per window
        window_minutes: Time window in minutes
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = None
            
            # Get current user from kwargs
            for key, value in kwargs.items():
                if isinstance(value, User):
                    current_user = value
                    break
            
            if current_user:
                # TODO: Implement rate limiting logic with Redis or in-memory cache
                # For now, just log the attempt
                logger.debug(f"🚦 Rate limit check for user {current_user.id} | Endpoint: {func.__name__}")
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator

def _get_user_roles(user: User) -> List[str]:
    """Get list of roles for a user"""
    roles = []
    
    # Check admin role (if exists in user model)
    if hasattr(user, 'is_admin') and user.is_admin:
        roles.append('admin')
    
    # Check chef role
    if hasattr(user, 'is_chef') and user.is_chef:
        roles.append('chef')
    
    # Check family decision maker
    if (hasattr(user, 'is_family_account') and user.is_family_account and
        hasattr(user, 'is_decision_maker') and user.is_decision_maker):
        roles.append('decision_maker')
    
    # Check family member
    if hasattr(user, 'is_family_account') and user.is_family_account:
        roles.append('family_member')
    
    # Default user role
    if not roles:
        roles.append('user')
    
    return roles

# Dependency functions for FastAPI
def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """FastAPI dependency to get admin user"""
    if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

def get_chef_user(current_user: User = Depends(get_current_user)) -> User:
    """FastAPI dependency to get chef user"""
    user_roles = _get_user_roles(current_user)
    if not any(role in ['chef', 'admin'] for role in user_roles):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chef or admin access required"
        )
    return current_user

def get_family_decision_maker(current_user: User = Depends(get_current_user)) -> User:
    """FastAPI dependency to get family decision maker"""
    user_roles = _get_user_roles(current_user)
    if not any(role in ['decision_maker', 'admin'] for role in user_roles):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Family decision maker or admin access required"
        )
    return current_user

def get_family_member(current_user: User = Depends(get_current_user)) -> User:
    """FastAPI dependency to get family member"""
    user_roles = _get_user_roles(current_user)
    if not any(role in ['family_member', 'decision_maker', 'chef', 'admin'] for role in user_roles):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Family membership required"
        )
    return current_user
