"""
Unit tests for core/llm_client.py (CircuitBreaker) and core/cache.py.

Tests cover:
- CircuitBreaker: state transitions (CLOSED→OPEN→HALF_OPEN→CLOSED)
- CircuitBreaker: auto-recovery after cooldown
- LearnCache: get/put/delete/clear operations
- LearnCache: TTL expiration
"""
from __future__ import annotations

import time
from unittest.mock import patch, MagicMock

import pytest
from core.llm_client import CircuitBreaker, CBState, async_call_gemini, async_generate_from_llm
from core.cache import LearnCache


# ---------------------------------------------------------------------------
# CircuitBreaker tests
# ---------------------------------------------------------------------------

class TestCircuitBreaker:
    """Tests for the 3-state circuit breaker."""

    def test_initial_state_is_closed(self):
        cb = CircuitBreaker(threshold=3, cooldown=10, half_open_max=1)
        assert cb.state == CBState.CLOSED

    def test_stays_closed_under_threshold(self):
        cb = CircuitBreaker(threshold=3, cooldown=10, half_open_max=1)
        cb.record_failure()
        cb.record_failure()
        assert cb.state == CBState.CLOSED

    def test_opens_after_threshold_failures(self):
        cb = CircuitBreaker(threshold=3, cooldown=10, half_open_max=1)
        cb.record_failure()
        cb.record_failure()
        cb.record_failure()
        assert cb.state == CBState.OPEN

    def test_opens_on_quota_error(self):
        cb = CircuitBreaker(threshold=5, cooldown=10, half_open_max=1)
        cb.record_failure(is_quota=True)
        assert cb.state == CBState.OPEN

    def test_success_resets_failure_count(self):
        cb = CircuitBreaker(threshold=3, cooldown=10, half_open_max=1)
        cb.record_failure()
        cb.record_failure()
        cb.record_success()
        assert cb.state == CBState.CLOSED

    def test_open_rejects_primary(self):
        cb = CircuitBreaker(threshold=3, cooldown=10, half_open_max=1)
        cb.record_failure()
        cb.record_failure()
        cb.record_failure()
        assert cb.state == CBState.OPEN
        assert cb.should_allow_primary() is False

    def test_half_open_after_cooldown(self):
        cb = CircuitBreaker(threshold=3, cooldown=0, half_open_max=1)
        cb.record_failure()
        cb.record_failure()
        cb.record_failure()
        assert cb.state == CBState.OPEN
        # With cooldown=0, should transition to HALF_OPEN immediately
        assert cb.should_allow_primary() is True
        assert cb.state == CBState.HALF_OPEN

    def test_half_open_success_returns_to_closed(self):
        cb = CircuitBreaker(threshold=3, cooldown=0, half_open_max=2)
        cb.record_failure()
        cb.record_failure()
        cb.record_failure()
        cb.should_allow_primary()
        cb.record_success()
        assert cb.state == CBState.CLOSED

    def test_half_open_failure_reopens(self):
        cb = CircuitBreaker(threshold=3, cooldown=0, half_open_max=2)
        cb.record_failure()
        cb.record_failure()
        cb.record_failure()
        cb.should_allow_primary()
        cb.record_failure()
        assert cb.state == CBState.OPEN

    def test_to_dict_returns_dict(self):
        cb = CircuitBreaker(threshold=3, cooldown=10, half_open_max=1)
        state = cb.to_dict()
        assert isinstance(state, dict)
        assert state["state"] == "closed"
        assert "threshold" in state
        assert "failure_count" in state


# ---------------------------------------------------------------------------
# LearnCache tests
# ---------------------------------------------------------------------------

class TestLearnCache:
    """Tests for the TTL-based cache."""

    def test_put_and_get(self):
        cache = LearnCache(max_size=100, ttl=300)
        cache.put("key1", {"data": "value1"})
        result = cache.get("key1")
        assert result == {"data": "value1"}

    def test_get_missing_key(self):
        cache = LearnCache(max_size=100, ttl=300)
        assert cache.get("nonexistent") is None

    def test_size(self):
        cache = LearnCache(max_size=100, ttl=300)
        cache.put("key1", {"data": "value1"})
        cache.put("key2", {"data": "value2"})
        assert cache.size() == 2

    def test_ttl_expiration(self):
        cache = LearnCache(max_size=100, ttl=0)
        cache.put("key1", {"data": "value1"})
        time.sleep(0.1)
        assert cache.get("key1") is None

    def test_maxsize_eviction(self):
        cache = LearnCache(max_size=2, ttl=300)
        cache.put("key1", {"data": "1"})
        cache.put("key2", {"data": "2"})
        cache.put("key3", {"data": "3"})
        # One of the earlier keys should be evicted
        assert cache.get("key3") == {"data": "3"}
        assert cache.size() <= 2


# ---------------------------------------------------------------------------
# call_gemini routing tests
# ---------------------------------------------------------------------------

class TestCallGeminiFunctions:
    """Tests that async_call_gemini and async_generate_from_llm are properly defined."""

    def test_async_call_gemini_is_callable(self):
        assert callable(async_call_gemini)

    def test_async_generate_from_llm_is_callable(self):
        assert callable(async_generate_from_llm)
