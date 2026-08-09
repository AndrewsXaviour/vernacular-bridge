"""In-memory TTL cache for LLM response caching.

Uses ``cachetools.TTLCache`` for proper LRU eviction combined with
time-to-live expiry.  Falls back to a manual dict-based cache if
``cachetools`` is not installed.

Classes:
    LearnCache: TTL cache with get/put/size operations.
"""

import time
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Try cachetools first, fall back to manual implementation
try:
    from cachetools import TTLCache

    _HAS_CACHETOOLS = True
except ImportError:
    _HAS_CACHETOOLS = False


class LearnCache:
    """Time-to-live cache for learn endpoint responses.

    Uses ``cachetools.TTLCache`` when available for proper LRU eviction
    with automatic time-based expiry.  Falls back to a manual dict-based
    cache otherwise.

    Attributes:
        max_size: Maximum number of cached entries.
        ttl: Time-to-live in seconds for each entry.

    Methods:
        get: Retrieve a cached value by key (returns None if missing/expired).
        put: Store a value with the current timestamp + TTL.
        size: Number of non-expired entries.
    """

    def __init__(self, max_size: int = 100, ttl: int = 600) -> None:
        """Initialize the cache.

        Args:
            max_size: Maximum entries before LRU eviction.
            ttl: Time-to-live in seconds.
        """
        self.max_size = max_size
        self.ttl = ttl

        if _HAS_CACHETOOLS:
            self._ttl_cache: Optional[TTLCache] = TTLCache(maxsize=max_size, ttl=ttl)
            self._store: Optional[Dict[str, Dict[str, Any]]] = None
        else:
            self._ttl_cache = None
            self._store = {}

    def get(self, key: str) -> Optional[dict]:
        """Retrieve a cached value, returning None if missing or expired.

        Args:
            key: The cache key.

        Returns:
            The cached data dict, or None.
        """
        if self._ttl_cache is not None:
            entry = self._ttl_cache.get(key)
            if entry is not None:
                logger.info("CACHE_HIT | key=%s", key)
                return entry
            return None

        # Fallback: manual dict
        entry = self._store.get(key)
        if entry is None:
            return None
        if time.time() >= entry["expiry"]:
            logger.info("CACHE_EXPIRED | key=%s", key)
            self._store.pop(key, None)
            return None
        logger.info("CACHE_HIT | key=%s", key)
        return entry["data"]

    def put(self, key: str, data: dict) -> None:
        """Store a value in the cache with TTL-based expiry.

        If the cache is full, the LRU entry is evicted automatically
        (cachetools) or the oldest entry is removed (fallback).

        Args:
            key: The cache key.
            data: The data to cache.
        """
        if self._ttl_cache is not None:
            self._ttl_cache[key] = data
            return

        # Fallback: manual dict
        if len(self._store) >= self.max_size:
            try:
                first_key = next(iter(self._store))
                self._store.pop(first_key)
            except StopIteration:
                pass
        self._store[key] = {
            "data": data,
            "expiry": time.time() + self.ttl,
        }

    def size(self) -> int:
        """Return the current number of entries in the cache.

        Returns:
            Count of cached entries (including possibly-expired ones).
        """
        if self._ttl_cache is not None:
            return len(self._ttl_cache)
        return len(self._store)
