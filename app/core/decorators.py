"""
Decorator pattern implementation for cross-cutting concerns.

This module provides decorators for caching, logging, performance monitoring,
and other cross-cutting concerns that can be applied to service methods.
"""

import time
import logging
from typing import Any, Callable, Dict, Optional, TypeVar, Union
from functools import wraps

from app.core.base import CacheInterface, Result

logger = logging.getLogger(__name__)

# Type variable for function return types
F = TypeVar('F', bound=Callable[..., Any])


def cache_result(
    cache_service: CacheInterface,
    key_prefix: str,
    expire_seconds: int = 3600,
    key_generator: Optional[Callable] = None
):
    """
    Decorator to cache function results.
    
    Args:
        cache_service: Cache service instance
        key_prefix: Prefix for cache keys
        expire_seconds: Cache expiration time in seconds
        key_generator: Custom function to generate cache keys
        
    Returns:
        Decorated function with caching
    """
    def decorator(func: F) -> F:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            if key_generator:
                cache_key = key_generator(*args, **kwargs)
            else:
                cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache first
            try:
                cached_result = await cache_service.get(cache_key)
                if cached_result is not None:
                    logger.debug(f"Cache hit for key: {cache_key}")
                    return cached_result
            except Exception as e:
                logger.warning(f"Cache get failed for key {cache_key}: {str(e)}")
            
            # Execute function and cache result
            try:
                result = await func(*args, **kwargs)
                
                # Cache the result
                try:
                    await cache_service.set(cache_key, result, expire=expire_seconds)
                    logger.debug(f"Cached result for key: {cache_key}")
                except Exception as e:
                    logger.warning(f"Cache set failed for key {cache_key}: {str(e)}")
                
                return result
                
            except Exception as e:
                logger.error(f"Function execution failed: {str(e)}")
                raise
        
        return wrapper
    return decorator


def log_execution(
    log_args: bool = True,
    log_result: bool = False,
    log_execution_time: bool = True,
    log_level: str = "info"
):
    """
    Decorator to log function execution details.
    
    Args:
        log_args: Whether to log function arguments
        log_result: Whether to log function result
        log_execution_time: Whether to log execution time
        log_level: Logging level for execution logs
        
    Returns:
        Decorated function with logging
    """
    def decorator(func: F) -> F:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            func_name = func.__name__
            
            # Log function call
            if log_args:
                log_data = {
                    "function": func_name,
                    "args": str(args),
                    "kwargs": str(kwargs),
                    "timestamp": datetime.utcnow().isoformat()
                }
                getattr(logger, log_level)(f"Function call: {json.dumps(log_data, default=str)}")
            
            try:
                # Execute function
                result = await func(*args, **kwargs)
                
                # Log execution time
                if log_execution_time:
                    execution_time = time.time() - start_time
                    logger.info(f"Function {func_name} executed in {execution_time:.4f} seconds")
                
                # Log result if requested
                if log_result:
                    logger.debug(f"Function {func_name} result: {str(result)[:200]}...")
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(
                    f"Function {func_name} failed after {execution_time:.4f} seconds: {str(e)}"
                )
                raise
        
        return wrapper
    return decorator


def retry_on_failure(
    max_attempts: int = 3,
    delay_seconds: float = 1.0,
    backoff_multiplier: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorator to retry function execution on failure.
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay_seconds: Initial delay between retries
        backoff_multiplier: Multiplier for exponential backoff
        exceptions: Tuple of exceptions to retry on
        
    Returns:
        Decorated function with retry logic
    """
    def decorator(func: F) -> F:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay_seconds
            
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                    
                except exceptions as e:
                    last_exception = e
                    
                    if attempt < max_attempts - 1:
                        logger.warning(
                            f"Attempt {attempt + 1} failed for {func.__name__}: {str(e)}. "
                            f"Retrying in {current_delay} seconds..."
                        )
                        
                        # Wait before retry
                        import asyncio
                        await asyncio.sleep(current_delay)
                        
                        # Exponential backoff
                        current_delay *= backoff_multiplier
                    else:
                        logger.error(
                            f"All {max_attempts} attempts failed for {func.__name__}. "
                            f"Last error: {str(e)}"
                        )
            
            # Re-raise the last exception if all attempts failed
            raise last_exception
        
        return wrapper
    return decorator


def validate_input(validator_func: Callable):
    """
    Decorator to validate function input parameters.
    
    Args:
        validator_func: Function to validate input parameters
        
    Returns:
        Decorated function with input validation
    """
    def decorator(func: F) -> F:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Validate input
            validation_result = validator_func(*args, **kwargs)
            
            if not validation_result:
                raise ValueError("Input validation failed")
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def performance_monitor(threshold_seconds: float = 1.0):
    """
    Decorator to monitor function performance.
    
    Args:
        threshold_seconds: Threshold in seconds to log slow executions
        
    Returns:
        Decorated function with performance monitoring
    """
    def decorator(func: F) -> F:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                return result
                
            finally:
                execution_time = time.time() - start_time
                
                if execution_time > threshold_seconds:
                    logger.warning(
                        f"Slow execution detected: {func.__name__} took {execution_time:.4f} seconds "
                        f"(threshold: {threshold_seconds}s)"
                    )
                else:
                    logger.debug(
                        f"Function {func.__name__} executed in {execution_time:.4f} seconds"
                    )
        
        return wrapper
    return decorator


def circuit_breaker(
    failure_threshold: int = 5,
    recovery_timeout: int = 60,
    expected_exception: type = Exception
):
    """
    Decorator to implement circuit breaker pattern.
    
    Args:
        failure_threshold: Number of failures before opening circuit
        recovery_timeout: Time in seconds to wait before attempting recovery
        expected_exception: Exception type to count as failures
        
    Returns:
        Decorated function with circuit breaker
    """
    def decorator(func: F) -> F:
        # Circuit breaker state
        failure_count = 0
        last_failure_time = None
        circuit_open = False
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            nonlocal failure_count, last_failure_time, circuit_open
            
            # Check if circuit is open
            if circuit_open:
                if (datetime.utcnow() - last_failure_time).total_seconds() < recovery_timeout:
                    logger.warning(f"Circuit breaker open for {func.__name__}")
                    raise Exception("Circuit breaker is open")
                else:
                    # Attempt recovery
                    circuit_open = False
                    failure_count = 0
                    logger.info(f"Circuit breaker attempting recovery for {func.__name__}")
            
            try:
                result = await func(*args, **kwargs)
                
                # Reset failure count on success
                failure_count = 0
                return result
                
            except expected_exception as e:
                failure_count += 1
                last_failure_time = datetime.utcnow()
                
                # Open circuit if threshold reached
                if failure_count >= failure_threshold:
                    circuit_open = True
                    logger.error(
                        f"Circuit breaker opened for {func.__name__} after {failure_count} failures"
                    )
                
                raise e
        
        return wrapper
    return decorator


def rate_limit(max_calls: int, time_window: int):
    """
    Decorator to implement rate limiting.
    
    Args:
        max_calls: Maximum number of calls allowed
        time_window: Time window in seconds
        
    Returns:
        Decorated function with rate limiting
    """
    def decorator(func: F) -> F:
        # Rate limiting state
        call_times = []
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            nonlocal call_times
            
            current_time = time.time()
            
            # Remove old call times outside the window
            call_times = [t for t in call_times if current_time - t < time_window]
            
            # Check if rate limit exceeded
            if len(call_times) >= max_calls:
                logger.warning(f"Rate limit exceeded for {func.__name__}")
                raise Exception("Rate limit exceeded")
            
            # Record this call
            call_times.append(current_time)
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def transaction_rollback(db_session):
    """
    Decorator to handle database transaction rollback on errors.
    
    Args:
        db_session: Database session to rollback on error
        
    Returns:
        Decorated function with transaction rollback
    """
    def decorator(func: F) -> F:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                db_session.commit()
                return result
                
            except Exception as e:
                db_session.rollback()
                logger.error(f"Transaction rolled back for {func.__name__}: {str(e)}")
                raise
        
        return wrapper
    return decorator


def async_timeout(timeout_seconds: float):
    """
    Decorator to add timeout to async functions.
    
    Args:
        timeout_seconds: Timeout in seconds
        
    Returns:
        Decorated function with timeout
    """
    def decorator(func: F) -> F:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            import asyncio
            
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout_seconds)
            except asyncio.TimeoutError:
                logger.error(f"Function {func.__name__} timed out after {timeout_seconds} seconds")
                raise TimeoutError(f"Function {func.__name__} timed out")
        
        return wrapper
    return decorator


# Utility decorator that combines multiple common decorators
def service_method(
    cache_service: Optional[CacheInterface] = None,
    cache_key_prefix: str = "",
    cache_expire: int = 3600,
    log_execution: bool = True,
    log_args: bool = False,
    log_result: bool = False,
    retry_attempts: int = 0,
    performance_threshold: float = 1.0
):
    """
    Utility decorator that combines common service method decorators.
    
    Args:
        cache_service: Optional cache service for result caching
        cache_key_prefix: Prefix for cache keys
        cache_expire: Cache expiration time in seconds
        log_execution: Whether to log execution details
        log_args: Whether to log function arguments
        log_result: Whether to log function results
        retry_attempts: Number of retry attempts on failure
        performance_threshold: Performance monitoring threshold
        
    Returns:
        Decorated function with multiple cross-cutting concerns
    """
    def decorator(func: F) -> F:
        # Apply logging decorator
        if log_execution:
            func = log_execution(log_args=log_args, log_result=log_result)(func)
        
        # Apply performance monitoring
        func = performance_monitor(performance_threshold)(func)
        
        # Apply retry decorator if requested
        if retry_attempts > 0:
            func = retry_on_failure(max_attempts=retry_attempts)(func)
        
        # Apply caching decorator if cache service provided
        if cache_service:
            func = cache_result(
                cache_service=cache_service,
                key_prefix=cache_key_prefix,
                expire_seconds=cache_expire
            )(func)
        
        return func
    
    return decorator
