"""Health route — GET /health.

Thin controller for system health monitoring.

Routes:
    health_check: GET /health — returns status, cache size, IP count,
                   circuit breaker state, and data health.
"""

import time
from fastapi import APIRouter
from services.learn_service import get_learn_cache_size
from services.retrieval_service import get_data_health
from core.rate_limiter import get_active_ip_count
from core.llm_client import get_circuit_breaker_state
from core.config import settings

router = APIRouter()


@router.get("/health")
async def health_check():
    """Return system health status.

    Returns:
        Dict with status, timestamp, version, cache_size, active_ips,
        circuit_breaker state, and data health.
    """
    return {
        "status": "ok",
        "timestamp": time.time(),
        "version": "1.0.0",
        "cache_size": get_learn_cache_size(),
        "active_ips": get_active_ip_count(),
        "circuit_breaker": get_circuit_breaker_state(),
        "data": get_data_health(),
        "config": {
            "primary_model": settings.primary_model,
            "secondary_model": settings.secondary_model,
            "rate_limit_rpm": settings.rate_limit_rpm,
            "cache_ttl": settings.cache_ttl,
            "cache_max_size": settings.cache_max_size,
            "cb_threshold": settings.cb_threshold,
        },
    }
