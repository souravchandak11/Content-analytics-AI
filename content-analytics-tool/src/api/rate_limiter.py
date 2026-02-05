"""Rate Limiter using Redis for Content Analytics Tool."""

import os
import time
import functools
from typing import Optional, Callable, Any
import redis
from dotenv import load_dotenv

load_dotenv()


class RateLimiter:
    """Redis-backed rate limiter using token bucket algorithm."""
    
    def __init__(
        self,
        redis_url: Optional[str] = None,
        max_requests: int = 100,
        window_seconds: int = 60
    ):
        """Initialize the rate limiter.
        
        Args:
            redis_url: Redis connection URL. If not provided, reads from environment.
            max_requests: Maximum number of requests allowed in the window
            window_seconds: Time window in seconds
        """
        self.redis_url = redis_url or os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        
        try:
            self.redis_client = redis.from_url(self.redis_url)
            self.redis_client.ping()
            self._is_connected = True
        except (redis.ConnectionError, redis.RedisError):
            self._is_connected = False
            self.redis_client = None
    
    def _get_key(self, identifier: str) -> str:
        """Generate Redis key for rate limiting.
        
        Args:
            identifier: Unique identifier (e.g., API name, user ID)
            
        Returns:
            Redis key string
        """
        return f"rate_limit:{identifier}"
    
    def is_allowed(self, identifier: str) -> bool:
        """Check if a request is allowed under rate limits.
        
        Args:
            identifier: Unique identifier for the rate limit bucket
            
        Returns:
            True if request is allowed, False if rate limited
        """
        if not self._is_connected:
            return True  # Allow if Redis is not available
        
        key = self._get_key(identifier)
        current_time = int(time.time())
        window_start = current_time - self.window_seconds
        
        pipe = self.redis_client.pipeline()
        
        # Remove old entries outside the window
        pipe.zremrangebyscore(key, 0, window_start)
        
        # Count requests in current window
        pipe.zcard(key)
        
        # Add current request
        pipe.zadd(key, {str(current_time): current_time})
        
        # Set expiry on the key
        pipe.expire(key, self.window_seconds)
        
        results = pipe.execute()
        request_count = results[1]
        
        return request_count < self.max_requests
    
    def get_remaining(self, identifier: str) -> int:
        """Get remaining requests in the current window.
        
        Args:
            identifier: Unique identifier for the rate limit bucket
            
        Returns:
            Number of remaining requests allowed
        """
        if not self._is_connected:
            return self.max_requests
        
        key = self._get_key(identifier)
        current_time = int(time.time())
        window_start = current_time - self.window_seconds
        
        # Clean up old entries
        self.redis_client.zremrangebyscore(key, 0, window_start)
        
        # Get current count
        current_count = self.redis_client.zcard(key)
        
        return max(0, self.max_requests - current_count)
    
    def wait_if_needed(self, identifier: str) -> float:
        """Wait if rate limited and return wait time.
        
        Args:
            identifier: Unique identifier for the rate limit bucket
            
        Returns:
            Time waited in seconds (0 if no wait needed)
        """
        if not self._is_connected:
            return 0.0
        
        if self.is_allowed(identifier):
            return 0.0
        
        # Calculate wait time based on oldest entry
        key = self._get_key(identifier)
        oldest = self.redis_client.zrange(key, 0, 0, withscores=True)
        
        if oldest:
            oldest_time = oldest[0][1]
            wait_time = self.window_seconds - (time.time() - oldest_time)
            if wait_time > 0:
                time.sleep(wait_time)
                return wait_time
        
        return 0.0


def rate_limited(
    identifier: str,
    max_requests: int = 100,
    window_seconds: int = 60
) -> Callable:
    """Decorator for rate limiting function calls.
    
    Args:
        identifier: Unique identifier for the rate limit bucket
        max_requests: Maximum number of requests in the window
        window_seconds: Time window in seconds
        
    Returns:
        Decorated function
    """
    limiter = RateLimiter(max_requests=max_requests, window_seconds=window_seconds)
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            limiter.wait_if_needed(identifier)
            return func(*args, **kwargs)
        return wrapper
    return decorator
