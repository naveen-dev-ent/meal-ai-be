import json
import logging
from typing import Optional, Any, Dict
import asyncio

logger = logging.getLogger(__name__)

# In-memory cache for development
memory_cache = {}


async def init_cache():
    """Initialize cache"""
    logger.info("✅ Using in-memory cache for development")


async def close_cache():
    """Close cache connections"""
    logger.info("✅ Cache closed")


class CacheManager:
    """Cache manager for the application"""
    
    def __init__(self):
        self.memory_cache = memory_cache
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            return self.memory_cache.get(key)
        except Exception as e:
            logger.error(f"❌ Cache get failed for key {key}: {e}")
            return None
    
    async def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        """Set value in cache with expiration"""
        try:
            self.memory_cache[key] = value
            # Simple in-memory expiration
            asyncio.create_task(self._expire_key(key, expire))
            return True
        except Exception as e:
            logger.error(f"❌ Cache set failed for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            self.memory_cache.pop(key, None)
            return True
        except Exception as e:
            logger.error(f"❌ Cache delete failed for key {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            return key in self.memory_cache
        except Exception as e:
            logger.error(f"❌ Cache exists check failed for key {key}: {e}")
            return False
    
    async def _expire_key(self, key: str, seconds: int):
        """Expire key after specified seconds (in-memory fallback)"""
        await asyncio.sleep(seconds)
        self.memory_cache.pop(key, None)


# Global cache manager instance
cache_manager = CacheManager()


# Cache decorator for functions
def cache_result(expire: int = 3600, key_prefix: str = ""):
    """Decorator to cache function results"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached_result = await cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache_manager.set(cache_key, result, expire)
            return result
        
        return wrapper
    return decorator


# Specific cache functions for common use cases
async def cache_user_session(user_id: int, session_data: Dict[str, Any]) -> bool:
    """Cache user session data"""
    key = f"session:user:{user_id}"
    return await cache_manager.set(key, session_data, expire=1800)  # 30 minutes


async def get_user_session(user_id: int) -> Optional[Dict[str, Any]]:
    """Get cached user session data"""
    key = f"session:user:{user_id}"
    return await cache_manager.get(key)


async def cache_meal_generation(diet: str, region: str, meal_data: Dict[str, Any]) -> bool:
    """Cache meal generation results for diet/region combinations"""
    key = f"meal:generation:{diet}:{region}"
    return await cache_manager.set(key, meal_data, expire=7200)  # 2 hours


async def get_cached_meal(diet: str, region: str) -> Optional[Dict[str, Any]]:
    """Get cached meal generation for diet/region"""
    key = f"meal:generation:{diet}:{region}"
    return await cache_manager.get(key)


async def cache_stock_prices(postal_code: str, prices: Dict[str, float]) -> bool:
    """Cache stock prices for postal code"""
    key = f"prices:stock:{postal_code}"
    return await cache_manager.set(key, prices, expire=86400)  # 24 hours


async def get_cached_prices(postal_code: str) -> Optional[Dict[str, float]]:
    """Get cached stock prices for postal code"""
    key = f"prices:stock:{postal_code}"
    return await cache_manager.get(key)


# Health check
def check_cache_health() -> bool:
    """Check if cache is accessible"""
    try:
        # In-memory cache is always available
        return True
    except Exception as e:
        logger.error(f"❌ Cache health check failed: {e}")
        return False

