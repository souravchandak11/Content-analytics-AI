"""
Content Analytics Platform - Rate Limiter
==========================================
Redis-based rate limiting with sliding window.
"""

import os
import time
from functools import wraps
from typing import Callable, Optional

import redis
from dotenv import load_dotenv
from loguru import logger

load_dotenv()


class RateLimiter:
    """
    Redis-based rate limiter using sliding window algorithm.
    """
    
    def __init__(self, redis_url: str = None):
        """
        Initialize rate limiter.
        
        Args:
            redis_url: Redis connection URL
        """
        url = redis_url or os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        
        try:
            self.redis = redis.from_url(url, decode_responses=True)
            self.redis.ping()
            self._available = True
        except redis.RedisError as e:
            logger.warning(f"Redis not available, using in-memory fallback: {e}")
            self._available = False
            self._memory_store = {}
    
    def is_allowed(
        self, 
        key: str, 
        max_requests: int, 
        window_seconds: int
    ) -> bool:
        """
        Check if request is allowed under rate limit.
        
        Args:
            key: Rate limit key (e.g., 'youtube_api')
            max_requests: Maximum requests in window
            window_seconds: Time window in seconds
            
        Returns:
            True if request is allowed
        """
        if self._available:
            return self._redis_check(key, max_requests, window_seconds)
        return self._memory_check(key, max_requests, window_seconds)
    
    def _redis_check(
        self, 
        key: str, 
        max_requests: int, 
        window_seconds: int
    ) -> bool:
        """Redis-based rate check."""
        now = time.time()
        window_start = now - window_seconds
        rate_key = f"rate_limit:{key}"
        
        pipe = self.redis.pipeline()
        
        # Remove old entries
        pipe.zremrangebyscore(rate_key, 0, window_start)
        # Count current entries
        pipe.zcard(rate_key)
        
        results = pipe.execute()
        current_count = results[1]
        
        if current_count < max_requests:
            # Add this request
            self.redis.zadd(rate_key, {str(now): now})
            self.redis.expire(rate_key, window_seconds)
            return True
        
        return False
    
    def _memory_check(
        self, 
        key: str, 
        max_requests: int, 
        window_seconds: int
    ) -> bool:
        """In-memory fallback rate check."""
        now = time.time()
        window_start = now - window_seconds
        
        if key not in self._memory_store:
            self._memory_store[key] = []
        
        # Clean old entries
        self._memory_store[key] = [
            t for t in self._memory_store[key] if t > window_start
        ]
        
        if len(self._memory_store[key]) < max_requests:
            self._memory_store[key].append(now)
            return True
        
        return False
    
    def wait_if_needed(
        self, 
        key: str, 
        max_requests: int, 
        window_seconds: int,
        timeout: int = 60
    ) -> bool:
        """
        Wait until request is allowed.
        
        Args:
            key: Rate limit key
            max_requests: Maximum requests
            window_seconds: Time window
            timeout: Maximum wait time
            
        Returns:
            True if eventually allowed, False if timeout
        """
        start = time.time()
        
        while not self.is_allowed(key, max_requests, window_seconds):
            if time.time() - start > timeout:
                return False
            time.sleep(1)
        
        return True
    
    def get_remaining(self, key: str, max_requests: int, window_seconds: int) -> int:
        """Get remaining requests in window."""
        rate_key = f"rate_limit:{key}"
        now = time.time()
        window_start = now - window_seconds
        
        if self._available:
            self.redis.zremrangebyscore(rate_key, 0, window_start)
            current = self.redis.zcard(rate_key)
        else:
            if key in self._memory_store:
                self._memory_store[key] = [
                    t for t in self._memory_store[key] if t > window_start
                ]
                current = len(self._memory_store[key])
            else:
                current = 0
        
        return max(0, max_requests - current)


def rate_limited(
    key: str = None,
    max_requests: int = 100, 
    window_seconds: int = 60
) -> Callable:
    """
    Decorator for rate limiting functions.
    
    Args:
        key: Rate limit key (defaults to function name)
        max_requests: Maximum requests in window
        window_seconds: Time window
    """
    def decorator(func: Callable) -> Callable:
        limiter = RateLimiter()
        rate_key = key or func.__name__
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            if limiter.wait_if_needed(rate_key, max_requests, window_seconds):
                return func(*args, **kwargs)
            raise Exception(f"Rate limit exceeded for {rate_key}")
        
        return wrapper
    return decorator


# Global limiter instance
_limiter: Optional[RateLimiter] = None


def get_rate_limiter() -> RateLimiter:
    """Get global rate limiter instance."""
    global _limiter
    if _limiter is None:
        _limiter = RateLimiter()
    return _limiter
