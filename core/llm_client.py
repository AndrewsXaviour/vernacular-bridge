"""LLM client module — Gemini API calls with circuit breaker and retry.

Provides an asynchronous Gemini API call wrapper with a 3-state circuit
breaker (CLOSED → OPEN → HALF_OPEN → CLOSED), retry logic, and
timeout-wrapped async execution.

Functions:
    async_call_gemini: Async Gemini API call using client.aio.
    async_generate_from_llm: Circuit breaker with retry, primary→secondary→fallback.
    safe_call: Timeout wrapper with exception handling and logging.
    get_circuit_breaker_state: Return the current CB state for /health.
"""

import time
import json
import asyncio
import logging
from enum import Enum
from typing import Optional

from google import genai
from google.genai import types

from core.config import settings

logger = logging.getLogger(__name__)

# SDK Client — initialized once at module load
_client: Optional[genai.Client] = None


def _get_client() -> genai.Client:
    """Return the lazily-initialized Gemini client singleton.

    Returns:
        The genai.Client instance.
    """
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.google_api_key)
    return _client


# ---------------------------------------------------------------------------
# 3-State Circuit Breaker
# ---------------------------------------------------------------------------

class CBState(str, Enum):
    """Circuit breaker states."""
    CLOSED = "closed"        # Normal operation — requests pass through
    OPEN = "open"            # Tripped — requests blocked, using secondary
    HALF_OPEN = "half_open"  # Probing — testing if primary has recovered


class CircuitBreaker:
    """3-state circuit breaker with auto-recovery.

    State transitions:
        CLOSED  → OPEN      : after `threshold` consecutive failures
        OPEN    → HALF_OPEN : after `cooldown` seconds
        HALF_OPEN → CLOSED  : on successful probe
        HALF_OPEN → OPEN    : on failed probe

    Attributes:
        state: Current CB state.
        failure_count: Consecutive failure counter (reset on success).
        last_failure_time: Timestamp of the most recent failure.
        half_open_probes: Number of probe attempts in HALF_OPEN state.
    """

    def __init__(
        self,
        threshold: int = 3,
        cooldown: int = 60,
        half_open_max: int = 1,
    ) -> None:
        """Initialize the circuit breaker.

        Args:
            threshold: Consecutive failures before tripping to OPEN.
            cooldown: Seconds to wait in OPEN before transitioning to HALF_OPEN.
            half_open_max: Max probe attempts in HALF_OPEN before reopening.
        """
        self.threshold = threshold
        self.cooldown = cooldown
        self.half_open_max = half_open_max
        self.state: CBState = CBState.CLOSED
        self.failure_count: int = 0
        self.last_failure_time: float = 0.0
        self.half_open_probes: int = 0

    def record_success(self) -> None:
        """Record a successful call — resets the circuit breaker."""
        self.failure_count = 0
        if self.state == CBState.HALF_OPEN:
            logger.info("CIRCUIT_BREAKER | transition=HALF_OPEN→CLOSED | reason=probe_success")
            self.state = CBState.CLOSED
            self.half_open_probes = 0

    def record_failure(self, is_quota: bool = False) -> None:
        """Record a failed call — may trip the circuit breaker.

        Args:
            is_quota: If True, the failure is a quota error (trips immediately).
        """
        self.failure_count += 1
        self.last_failure_time = time.time()

        if is_quota:
            # Quota errors trip immediately
            logger.warning(
                "CIRCUIT_BREAKER | state=%s | failure=%d | "
                "transition→OPEN | reason=quota_error",
                self.state.value, self.failure_count,
            )
            self.state = CBState.OPEN
            self.half_open_probes = 0
            return

        if self.state == CBState.HALF_OPEN:
            # Probe failed — reopen
            logger.warning(
                "CIRCUIT_BREAKER | transition=HALF_OPEN→OPEN | "
                "reason=probe_failed | probes=%d",
                self.half_open_probes,
            )
            self.state = CBState.OPEN
            self.half_open_probes = 0
            return

        if self.failure_count >= self.threshold:
            logger.warning(
                "CIRCUIT_BREAKER | transition=CLOSED→OPEN | "
                "failure=%d threshold=%d",
                self.failure_count, self.threshold,
            )
            self.state = CBState.OPEN
            self.half_open_probes = 0

    def should_allow_primary(self) -> bool:
        """Check whether the primary model should be attempted.

        Returns:
            True if requests should go to the primary model.
        """
        if self.state == CBState.CLOSED:
            return True

        if self.state == CBState.OPEN:
            # Check if cooldown has elapsed
            elapsed = time.time() - self.last_failure_time
            if elapsed >= self.cooldown:
                logger.info(
                    "CIRCUIT_BREAKER | transition=OPEN→HALF_OPEN | "
                    "cooldown_elapsed=%.1fs",
                    elapsed,
                )
                self.state = CBState.HALF_OPEN
                self.half_open_probes = 0
                return True  # Allow one probe
            return False

        # HALF_OPEN — allow probe if under limit
        if self.half_open_probes < self.half_open_max:
            self.half_open_probes += 1
            return True

        return False

    def to_dict(self) -> dict:
        """Serialize state for /health endpoint.

        Returns:
            Dict with state, failure_count, and last_failure_time.
        """
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "last_failure_time": self.last_failure_time,
            "threshold": self.threshold,
            "cooldown": self.cooldown,
        }


# Module-level circuit breaker instance
_circuit_breaker = CircuitBreaker(
    threshold=settings.cb_threshold,
    cooldown=settings.cb_cooldown,
    half_open_max=settings.cb_half_open_max,
)


def get_circuit_breaker_state() -> dict:
    """Return the current circuit breaker state for /health.

    Returns:
        Dict with CB state, failure count, and config.
    """
    return _circuit_breaker.to_dict()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SAFE_FALLBACK_JSON = {
    "status": "error",
    "message": "Unable to generate accurate content. Please try again.",
}


def _is_quota_error(e: Exception) -> bool:
    """Detect quota-related failures (429 / RESOURCE_EXHAUSTED).

    Args:
        e: The exception to inspect.

    Returns:
        True if the error indicates quota exhaustion.
    """
    err_str = str(e).upper()
    return "429" in err_str or "RESOURCE_EXHAUSTED" in err_str


# ---------------------------------------------------------------------------
# Async Gemini call
# ---------------------------------------------------------------------------

async def async_call_gemini(model_name: str, prompt: str) -> str:
    """Async Gemini API call using client.aio with structured JSON output.

    Args:
        model_name: The Gemini model identifier.
        prompt: The prompt to send to the model.

    Returns:
        The raw response text from the model.

    Raises:
        ValueError: If the model returns an empty response.
        Exception: If the API call fails.
    """
    client = _get_client()
    try:
        # Run the synchronous client in a thread pool to completely bypass 
        # aiohttp's Windows DNS resolution bug, since standard sockets work fine!
        response = await asyncio.to_thread(
            client.models.generate_content,
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )
    except Exception as e:
        logger.error(
            "ASYNC_GEMINI_EXCEPTION | model=%s | error=%s | msg=%s",
            model_name, type(e).__name__, str(e),
        )
        raise

    if not response.text or not response.text.strip():
        raise ValueError(f"Empty response from {model_name}")
    return response.text


# ---------------------------------------------------------------------------
# Circuit breaker with retry (async)
# ---------------------------------------------------------------------------

async def async_generate_from_llm(prompt: str) -> str:
    """Call Gemini asynchronously with circuit breaker, retry, and fallback.

    Execution order:
        1. Primary model (up to 3 retries) — gated by circuit breaker.
        2. Secondary model on CB OPEN or primary failure.
        3. Safe fallback JSON as last resort.

    The circuit breaker auto-recovers: OPEN → HALF_OPEN (after cooldown)
    → CLOSED (on successful probe).

    Args:
        prompt: The assembled prompt to send.

    Returns:
        The raw LLM response text or a safe fallback JSON string.
    """
    # 1. PRIMARY EXECUTION (gated by circuit breaker)
    if _circuit_breaker.should_allow_primary():
        for attempt in range(1, 4):
            start_time = time.time()
            try:
                text = await async_call_gemini(settings.primary_model, prompt)
                duration = time.time() - start_time
                _circuit_breaker.record_success()
                logger.info(
                    "LLM_PRIMARY_SUCCESS | model=%s | time=%.2fs | length=%d",
                    settings.primary_model, duration, len(text),
                )
                return text
            except Exception as e:
                duration = time.time() - start_time
                is_quota = _is_quota_error(e)
                _circuit_breaker.record_failure(is_quota=is_quota)
                logger.error(
                    "LLM_PRIMARY_ERROR | model=%s | attempt=%d | "
                    "quota=%s | time=%.2fs | msg=%s",
                    settings.primary_model, attempt, is_quota,
                    duration, str(e)[:200],
                )
                if attempt < 3:
                    await asyncio.sleep(1)
                else:
                    logger.warning(
                        "LLM_PRIMARY_EXHAUSTED | model=%s | "
                        "retries=3 | transitioning to secondary",
                        settings.primary_model,
                    )
    else:
        logger.info(
            "LLM_PRIMARY_SKIPPED | cb_state=%s",
            _circuit_breaker.state.value,
        )

    # 2. SECONDARY EXECUTION
    start_time = time.time()
    try:
        text = await async_call_gemini(settings.secondary_model, prompt)
        duration = time.time() - start_time
        logger.info(
            "LLM_SECONDARY_SUCCESS | model=%s | time=%.2fs",
            settings.secondary_model, duration,
        )
        return text
    except Exception as e:
        duration = time.time() - start_time
        error_type = "quota" if _is_quota_error(e) else "other"
        logger.error(
            "LLM_SECONDARY_ERROR | model=%s | type=%s | time=%.2fs | msg=%s",
            settings.secondary_model, error_type, duration, str(e)[:200],
        )

    # 3. FINAL SAFETY FALLBACK
    logger.warning("LLM_FINAL_FALLBACK | status=zero_failure_demo_mode")
    return json.dumps(SAFE_FALLBACK_JSON)


# ---------------------------------------------------------------------------
# Timeout wrapper
# ---------------------------------------------------------------------------

async def safe_call(coro, module_name: str, timeout: int = 15) -> Optional[dict]:
    """Wrap an async coroutine with timeout, exception handling, and logging.

    Args:
        coro: The coroutine to execute.
        module_name: Human-readable name for log messages.
        timeout: Maximum seconds to wait.

    Returns:
        The coroutine result, or None on timeout/error.
    """
    try:
        logger.info("MODULE_%s_START", module_name)
        result = await asyncio.wait_for(coro, timeout=timeout)
        logger.info("MODULE_%s_SUCCESS", module_name)
        return result
    except asyncio.TimeoutError:
        logger.warning("MODULE_%s_TIMEOUT", module_name)
        return None
    except Exception as e:
        try:
            logger.error("MODULE_%s_FAILED | error=%s", module_name, str(e))
        except Exception:
            pass
        return None
