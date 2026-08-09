"""Core module — cross-cutting infrastructure (config, LLM, cache, rate limiter, safety, auth, audit).

This package contains shared services used across the application:
- config: Environment-driven Settings class
- llm_client: Gemini API calls with circuit breaker
- cache: TTL-based in-memory cache
- rate_limiter: Per-IP sliding window rate limiter
- safety_guard: Fact-Lock, Keyword-Lock, and Length Control
- auth: API key authentication for protected endpoints
- sanitizer: Prompt injection detection and user input wrapping
- audit: Structured JSON audit logging middleware
"""
