"""Tests for the Redis-backed CacheService with a fake redis client."""
import json

from app.services.cache_service import CacheService


class FakeRedis:
    def __init__(self):
        self.store = {}
        self.last_ttl = None

    def get(self, key):
        return self.store.get(key)

    def setex(self, key, ttl, value):
        self.last_ttl = ttl
        self.store[key] = value

    def delete(self, key):
        self.store.pop(key, None)


class ExplodingRedis:
    def get(self, key):
        raise RuntimeError("connection lost")

    def setex(self, key, ttl, value):
        raise RuntimeError("connection lost")

    def delete(self, key):
        raise RuntimeError("connection lost")


def _svc():
    svc = CacheService()
    svc.redis = FakeRedis()
    return svc


def test_set_and_get_roundtrip():
    svc = _svc()
    assert svc.set("k", {"a": 1}) is True
    assert svc.get("k") == {"a": 1}
    assert svc.redis.last_ttl == svc.default_ttl


def test_set_respects_custom_ttl():
    svc = _svc()
    svc.set("k", 1, ttl=120)
    assert svc.redis.last_ttl == 120


def test_get_missing_returns_none():
    assert _svc().get("nope") is None


def test_delete_removes_key():
    svc = _svc()
    svc.set("k", 1)
    assert svc.delete("k") is True
    assert svc.get("k") is None


def test_cache_key_builders():
    svc = CacheService()
    assert svc.get_dashboard_cache_key(5) == "dashboard:5"
    assert svc.get_batch_cache_key(9) == "batch:9"


def test_invalidate_helpers():
    svc = _svc()
    svc.set(svc.get_dashboard_cache_key(1), "x")
    svc.set(svc.get_batch_cache_key(2), "y")
    svc.invalidate_dashboard(1)
    svc.invalidate_batch(2)
    assert svc.get(svc.get_dashboard_cache_key(1)) is None
    assert svc.get(svc.get_batch_cache_key(2)) is None


def test_operations_swallow_connection_errors():
    svc = CacheService()
    svc.redis = ExplodingRedis()
    assert svc.get("k") is None
    assert svc.set("k", 1) is False
    assert svc.delete("k") is False  # connection failure is surfaced as False
