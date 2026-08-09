"""API key authentication for protected endpoints.

Provides a FastAPI dependency that validates incoming requests against
a comma-separated list of API keys configured via the ``API_KEYS``
environment variable.

Behavior:
    - If ``API_KEYS`` is empty, authentication is disabled (open access).
    - Valid keys are sent via the ``X-API-Key`` request header.
    - Missing key → 401 Unauthorized.
    - Invalid key → 403 Forbidden.

Functions:
    verify_api_key: FastAPI dependency that enforces API key validation.
"""

import logging
from typing import Optional

from fastapi import Header, HTTPException

from core.config import settings

logger = logging.getLogger(__name__)


def _get_valid_keys() -> set[str]:
    """Parse the API_KEYS env var into a set of valid keys.

    Returns:
        Set of non-empty key strings. Empty set means auth is disabled.
    """
    raw = settings.api_keys.strip()
    if not raw:
        return set()
    return {k.strip() for k in raw.split(",") if k.strip()}


# Cache at module load time — keys rarely change without restart.
_VALID_KEYS: set[str] = _get_valid_keys()


async def verify_api_key(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> Optional[str]:
    """FastAPI dependency: validate the X-API-Key header.

    If no API keys are configured (``API_KEYS`` env var is empty),
    this dependency is a no-op and all requests are allowed through.

    Args:
        x_api_key: The API key from the request header, or None.

    Returns:
        The validated API key string on success.

    Raises:
        HTTPException 401: If authentication is enabled but no key was sent.
        HTTPException 403: If the provided key is not in the valid set.
    """
    # Auth disabled — open access
    if not _VALID_KEYS:
        return None

    # No key provided
    if not x_api_key:
        logger.warning("AUTH_FAILED | reason=missing_key")
        raise HTTPException(
            status_code=401,
            detail="API key required. Send via X-API-Key header.",
        )

    # Invalid key
    if x_api_key not in _VALID_KEYS:
        logger.warning("AUTH_FAILED | reason=invalid_key")
        raise HTTPException(
            status_code=403,
            detail="Invalid API key.",
        )

    return x_api_key
