"""
Redis cache service module for managing caching operations.
"""

import pickle
from typing import Any, Optional
import redis.asyncio as redis
from fastapi import Request, Response
from functools import wraps

from src.conf.config import settings


class RedisCache:
    """
    Redis cache service for managing cached data.
    """

    def __init__(self):
        """Initialize Redis connection."""
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_DB,
            decode_responses=False,  # We need bytes for pickle
        )

    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key (str): Cache key.

        Returns:
            Any | None: Cached value if exists, None otherwise.
        """
        data = await self.redis_client.get(key)
        if data is not None:
            return pickle.loads(data)
        return None

    async def set(self, key: str, value: Any, expire: int = None) -> None:
        """
        Set value in cache.

        Args:
            key (str): Cache key.
            value (Any): Value to cache.
            expire (int, optional): Expiration time in seconds. Defaults to settings.REDIS_EXPIRE.
        """
        expire = expire or settings.REDIS_EXPIRE
        await self.redis_client.set(key, pickle.dumps(value), ex=expire)

    async def delete(self, key: str) -> None:
        """
        Delete value from cache.

        Args:
            key (str): Cache key to delete.
        """
        await self.redis_client.delete(key)

    async def clear_user_cache(self, user_id: int) -> None:
        """
        Clear all cache entries related to a specific user.

        Args:
            user_id (int): User ID whose cache should be cleared.
        """
        pattern = f"user:{user_id}:*"
        keys = await self.redis_client.keys(pattern)
        if keys:
            await self.redis_client.delete(*keys)


# Create a global Redis cache instance
redis_cache = RedisCache()


def cache_response(expire: int = None):
    """
    Decorator for caching API responses.

    Args:
        expire (int, optional): Cache expiration time in seconds.

    Returns:
        Callable: Decorator function.
    """

    def decorator(func):
        @wraps(func)  # Preserve the original function metadata
        async def wrapper(request: Request, *args, **kwargs):
            # Get current user if authenticated
            user = getattr(request.state, "user", None)
            user_id = getattr(user, "id", "anonymous")

            # Create cache key from path, query params, and user
            cache_key = f"user:{user_id}:path:{request.url.path}"
            if request.query_params:
                cache_key += f":query:{str(request.query_params)}"

            # Try to get cached response
            cached_data = await redis_cache.get(cache_key)
            if cached_data is not None:
                return cached_data

            # Get fresh response
            response = await func(request, *args, **kwargs)

            # Cache the response
            await redis_cache.set(cache_key, response, expire)
            return response

        return wrapper

    return decorator
