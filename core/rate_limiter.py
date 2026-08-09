"""Per-IP sliding-window rate limiter.

Provides a lightweight, non-blocking rate limiter that tracks request
timestamps per IP address. Old timestamps are pruned on each check.

Classes:
    RateLimiter: Tracks timestamps for a single client IP.

Functions:
    check_rate_limit: Returns True if the IP is allowed to make another request.
"""

import time
from typing import Dict

from core.config import settings


class RateLimiter:
    """Sliding-window rate limiter for a single client IP.

    Attributes:
        rpm: Maximum requests allowed per 60-second window.
        requests: List of Unix timestamps for recent requests.

    Methods:
        is_allowed: Check if a new request is permitted.
    """

    def __init__(self, rpm: int = 20) -> None:
        """Initialize the rate limiter.

        Args:
            rpm: Maximum requests per minute.
        """
        self.rpm = rpm
        self.requests: list[float] = []

    def is_allowed(self) -> bool:
        """Check whether a new request is within the rate limit.

        Returns:
            True if the request is allowed, False if the limit is exceeded.
        """
        now = time.time()
        # Prune timestamps older than 60 seconds
        self.requests = [t for t in self.requests if now - t < 60]
        if len(self.requests) >= self.rpm:
            return False
        self.requests.append(now)
        return True


# Global per-IP limiter state
_IP_LIMITS: Dict[str, RateLimiter] = {}


def check_rate_limit(ip: str, rpm: int = 0) -> bool:
    """Check whether the given IP address is within the rate limit.

    Creates a new RateLimiter for unseen IPs. Default limit comes from
    settings.rate_limit_rpm (env: RATE_LIMIT_RPM, default 20).

    Args:
        ip: The client IP address.
        rpm: Maximum requests per minute (0 = use settings default).

    Returns:
        True if the request is allowed.
    """
    effective_rpm = rpm if rpm > 0 else settings.rate_limit_rpm
    if ip not in _IP_LIMITS:
        _IP_LIMITS[ip] = RateLimiter(rpm=rpm)
    return _IP_LIMITS[ip].is_allowed()


def get_active_ip_count() -> int:
    """Return the number of distinct IPs that have made requests.

    Returns:
        Count of unique IP addresses tracked.
    """
    return len(_IP_LIMITS)
