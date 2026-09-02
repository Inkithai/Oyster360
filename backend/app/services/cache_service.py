"""
Oyster360 Redis Cache Service
Production-ready caching layer
"""
import redis
import json
import os
from typing import Any, Optional
from datetime import timedelta

class CacheService:
    def __init__(self):
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/1")
        self.redis = redis.from_url(redis_url, decode_responses=True)
        self.default_ttl = 3600  # 1 hour

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception:
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        try:
            ttl = ttl or self.default_ttl
            self.redis.set(key, json.dumps(value), ex=ttl)
            return True
        except Exception:
            return False

    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            self.redis.delete(key)
            return True
        except Exception:
            return False

    def get_dashboard_cache_key(self, organization_id: int) -> str:
        return f"dashboard:{organization_id}"

    def get_batch_cache_key(self, batch_id: int) -> str:
        return f"batch:{batch_id}"

    def invalidate_dashboard(self, organization_id: int):
        """Invalidate dashboard cache"""
        key = self.get_dashboard_cache_key(organization_id)
        self.delete(key)

    def invalidate_batch(self, batch_id: int):
        """Invalidate batch cache"""
        key = self.get_batch_cache_key(batch_id)
        self.delete(key)

# Global cache instance
cache = CacheService()