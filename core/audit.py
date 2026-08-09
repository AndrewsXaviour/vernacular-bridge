"""Structured JSON audit logging for all API requests.

Provides a FastAPI middleware that logs every request/response pair as
a single JSON line, including request_id, endpoint, method, query hash,
masked IP, status code, and latency.

Privacy:
    - Raw user text is NEVER logged (only a SHA-256 hash).
    - IP addresses are masked (last octet zeroed for IPv4).

Functions:
    AuditMiddleware: ASGI middleware that logs structured request data.
"""

import hashlib
import json
import logging
import time
import uuid
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("audit")


def _hash_text(text: str) -> str:
    """Return a SHA-256 hex digest for the given text.

    Used to create a repeatable, non-reversible fingerprint of user
    input for log correlation without exposing the raw text.

    Args:
        text: The string to hash.

    Returns:
        First 16 characters of the SHA-256 hex digest.
    """
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _mask_ip(ip: str) -> str:
    """Mask the last octet of an IPv4 address for privacy.

    Examples:
        "192.168.1.42" → "192.168.1.0"
        "10.0.0.1"     → "10.0.0.0"
        "unknown"      → "unknown"

    Args:
        ip: The raw IP address string.

    Returns:
        The masked IP address.
    """
    parts = ip.split(".")
    if len(parts) == 4:
        parts[-1] = "0"
        return ".".join(parts)
    return ip


class AuditMiddleware(BaseHTTPMiddleware):
    """ASGI middleware that logs structured audit data for every request.

    Each log line is a JSON object with:
        - request_id: Short UUID for correlation.
        - method: HTTP method.
        - endpoint: Request path.
        - client_ip: Masked IP address.
        - status_code: Response status code.
        - latency_ms: Request duration in milliseconds.
        - query_hash: SHA-256 hash of the request body (if present).
        - model_used: LLM model if identifiable from path.

    Privacy: Raw request body text is never logged.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process a single request through the audit logger.

        Args:
            request: The incoming FastAPI request.
            call_next: The next middleware or route handler.

        Returns:
            The response from the downstream handler.
        """
        req_id = str(uuid.uuid4())[:8]
        start = time.time()

        # Extract client IP
        client_ip = "unknown"
        if request.client:
            client_ip = request.client.host

        # Hash the request body (if present) — never log raw text
        query_hash = ""
        try:
            body = await request.body()
            if body:
                query_hash = _hash_text(body.decode("utf-8", errors="replace"))
        except Exception:
            pass

        # Attach request_id to request state for downstream use
        request.state.request_id = req_id

        # Process request
        response = await call_next(request)

        # Calculate latency
        latency_ms = round((time.time() - start) * 1000, 1)

        # Detect model from path (for LLM endpoints)
        model_used = ""
        if "/learn" in request.url.path or "/generate" in request.url.path:
            model_used = "learn"
        elif "/coach" in request.url.path:
            model_used = "coach"
        elif "/navigator" in request.url.path:
            model_used = "navigator"
        elif "/full-flow" in request.url.path:
            model_used = "full_flow"

        # Structured log entry
        log_entry = {
            "request_id": req_id,
            "method": request.method,
            "endpoint": request.url.path,
            "client_ip": _mask_ip(client_ip),
            "status_code": response.status_code,
            "latency_ms": latency_ms,
            "query_hash": query_hash,
            "model_used": model_used,
        }

        # Log level based on status code
        if response.status_code >= 500:
            logger.error(json.dumps(log_entry))
        elif response.status_code >= 400:
            logger.warning(json.dumps(log_entry))
        else:
            logger.info(json.dumps(log_entry))

        return response
