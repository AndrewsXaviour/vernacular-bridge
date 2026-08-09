# Vernacular Bridge — Operations Center Upgrade Plan

**Document:** `docs/operations-center-upgrade.md`
**Status:** Planning
**Date:** 2026-06-19

---

## 1. Current State Analysis

### 1.1 What the Dashboard Currently Displays

| Section | Data Source | Type | Refresh |
|---------|------------|------|---------|
| **Module Overview Cards** | Hardcoded in JS | Static | Manual edit only |
| **Kanban Board** | `issues[]` array in JS | Static | Manual edit only |
| **Burn-down Chart** | Computed from `issues[]` | Static | On page load |
| **Execution Timeline** | Hardcoded HTML | Static | Never |
| **RCA Tracker** | `rcaEntries[]` array in JS | Static | Manual edit only |
| **Progress Bar** | Computed from `issues[]` | Static | On page load |

**Total sections:** 6
**Dynamic data:** 0 (everything is hardcoded in the HTML/JS)
**API connections:** 0

---

### 1.2 What the Backend Already Provides (But Dashboard Ignores)

The backend exposes rich operational data that the dashboard **does not consume**:

#### `/health` Endpoint (api/health.py)

```json
{
  "status": "ok",
  "uptime_seconds": 3842.5,
  "cache_size": 47,
  "active_ips": 3,
  "circuit_breaker": {
    "state": "closed",
    "failure_count": 0,
    "last_failure_time": 0.0,
    "threshold": 3,
    "cooldown": 60
  }
}
```

**Fields available but NOT displayed:**

| Field | What It Tells You | Dashboard Gap |
|-------|-------------------|---------------|
| `uptime_seconds` | How long the server has been running | No uptime display |
| `cache_size` | Number of cached LLM responses | No cache metrics |
| `active_ips` | Unique IPs making requests right now | No concurrent user count |
| `circuit_breaker.state` | `closed` / `open` / `half_open` | No system health indicator |
| `circuit_breaker.failure_count` | Consecutive LLM failures | No error rate display |
| `circuit_breaker.last_failure_time` | When the last failure occurred | No incident timeline |

#### Audit Middleware (core/audit.py)

Logs every request as structured JSON with:

```json
{
  "timestamp": "2026-06-19T14:32:01.234Z",
  "request_id": "req_8f3a2b1c",
  "method": "POST",
  "endpoint": "/learn",
  "client_ip": "192.168.1.xxx",
  "status_code": 200,
  "latency_ms": 2341.5,
  "query_hash": "a1b2c3d4e5f6g7h8",
  "model_used": "gemini-2.5-flash"
}
```

**Fields available but NOT displayed:**

| Field | What It Tells You | Dashboard Gap |
|-------|-------------------|---------------|
| `latency_ms` | Per-request response time | No latency chart |
| `status_code` | HTTP status per request | No error rate chart |
| `endpoint` | Which API route was hit | No endpoint usage breakdown |
| `model_used` | Which Gemini model served the request | No model usage tracking |
| `client_ip` (masked) | Unique user count | No user activity feed |
| `timestamp` | Request timing | No time-series data |
| `query_hash` | Request deduplication | No query frequency analysis |

#### Rate Limiter (core/rate_limiter.py)

- Tracks per-IP sliding window timestamps
- Exposes `get_active_ip_count()` — **available but not displayed**

#### Circuit Breaker (core/llm_client.py)

- 3-state machine: CLOSED → OPEN → HALF_OPEN → CLOSED
- Tracks: `failure_count`, `last_failure_time`, `half_open_probes`
- **State exposed via /health but not visualized**

#### LearnCache (core/cache.py)

- `cachetools.TTLCache` with LRU eviction
- Exposes `size()` — **available but not displayed**
- Tracks hits/misses internally — **not exposed via API**

---

### 1.3 What's Completely Missing

| Category | Missing Data | Why It Matters |
|----------|-------------|----------------|
| **Real-time Health** | Live /health polling | Dashboard shows nothing about actual system state |
| **Request Metrics** | Request count, error rate, latency percentiles | Cannot detect degradation |
| **LLM Performance** | Model used per request, success/failure rate, avg latency | Cannot track Gemini API costs or reliability |
| **Security Events** | Auth failures (401/403), injection pattern detections | Cannot detect attack attempts |
| **Cache Performance** | Hit rate, miss rate, eviction count | Cannot optimize caching |
| **Rate Limiting** | Blocked requests, per-IP breakdown | Cannot detect abuse |
| **Environment Config** | Current env vars (masked) | Cannot verify deployment config |
| **Log Viewer** | Recent audit log entries | Cannot debug production issues |
| **API Documentation** | Endpoint list, request/response schemas | Cannot onboard new developers |
| **Test Coverage** | Coverage %, test results over time | Cannot track quality trends |
| **Deployment Status** | Git version, deploy time, environment | Cannot correlate issues with deploys |
| **System Resources** | Memory, CPU, open file descriptors | Cannot detect resource exhaustion |

---

## 2. Upgrade Plan

### Priority 1: Connect to Live Backend Data (High Impact, Medium Effort)

**Goal:** Replace all hardcoded data with live API calls to `/health` and add real-time system status.

| Task | Description | Data Source | Effort |
|------|-------------|-------------|--------|
| **P1.1** | Add live `/health` polling section | `GET /health` every 5s | 2h |
| **P1.2** | Display circuit breaker state with visual indicator | `circuit_breaker.state` | 1h |
| **P1.3** | Show cache size and active IP count | `cache_size`, `active_ips` | 1h |
| **P1.4** | Display uptime counter | `uptime_seconds` | 30m |
| **P1.5** | Add system status header (green/yellow/red) | Derived from `circuit_breaker.state` + `status` | 1h |

**New Section: "System Health" (replaces static Module Overview)**

```
┌─────────────────────────────────────────────────────────┐
│  🟢 System Healthy          Uptime: 1h 4m  │  Cache: 47  │
│  Circuit Breaker: CLOSED    Active IPs: 3  │  Latency: -- │
└─────────────────────────────────────────────────────────┘
```

---

### Priority 2: Live Request Metrics (High Impact, High Effort)

**Goal:** Add a new `/metrics` backend endpoint that aggregates audit log data, then display charts.

| Task | Description | Data Source | Effort |
|------|-------------|-------------|--------|
| **P2.1** | Create `GET /metrics` endpoint | Aggregate from in-memory counters | 3h |
| **P2.2** | Track request count per endpoint | Counter dict in audit middleware | 1h |
| **P2.3** | Track latency histogram (p50, p95, p99) | Rolling window in audit middleware | 2h |
| **P2.4** | Track error rate (4xx, 5xx) per endpoint | Status code counters | 1h |
| **P2.5** | Add latency chart to dashboard | Frontend Chart.js or CSS bars | 2h |
| **P2.6** | Add endpoint usage breakdown chart | Frontend visualization | 2h |
| **P2.7** | Add error rate trend chart | Frontend visualization | 2h |

**New Backend: `core/metrics.py`**

```python
# In-memory metrics collector (no external dependencies)
class MetricsCollector:
    request_count: dict[str, int]           # endpoint → count
    error_count: dict[str, dict[int, int]]  # endpoint → {status_code: count}
    latency_ms: dict[str, list[float]]      # endpoint → [latencies]
    model_usage: dict[str, int]             # model_name → count
    injection_attempts: int                 # total detected
    auth_failures: int                      # total 401/403
```

**New Endpoint: `GET /metrics`**

```json
{
  "requests": {
    "total": 1247,
    "by_endpoint": {
      "/learn": {"count": 423, "avg_latency_ms": 2100, "p95_ms": 4500},
      "/coach": {"count": 189, "avg_latency_ms": 1800, "p95_ms": 3200},
      "/navigator/explain": {"count": 312, "avg_latency_ms": 1500, "p95_ms": 2800},
      "/full-flow": {"count": 323, "avg_latency_ms": 5200, "p95_ms": 9000}
    }
  },
  "errors": {
    "total": 23,
    "rate_pct": 1.84,
    "by_status": {"400": 12, "401": 5, "422": 4, "500": 2}
  },
  "models": {
    "gemini-2.5-flash": {"count": 890, "success_pct": 97.2},
    "gemini-2.5-pro": {"count": 357, "success_pct": 99.1}
  },
  "security": {
    "injection_attempts": 7,
    "auth_failures": 12,
    "rate_limit_blocks": 3
  }
}
```

---

### Priority 3: Security Dashboard (Medium Impact, Medium Effort)

**Goal:** Display security-relevant events from the audit middleware and sanitizer.

| Task | Description | Data Source | Effort |
|------|-------------|-------------|--------|
| **P3.1** | Track injection pattern detections | `core/sanitizer.py` logger | 1h |
| **P3.2** | Track auth failures (401/403) | `core/auth.py` response codes | 1h |
| **P3.3** | Track rate limit blocks | `core/rate_limiter.py` blocks | 1h |
| **P3.4** | Add security events section to dashboard | New section in HTML | 2h |
| **P3.5** | Show recent injection attempts (masked) | Metrics collector | 1h |

**New Section: "Security Events"**

```
┌─────────────────────────────────────────────────────────┐
│  🔒 Security Events (Last 24h)                          │
│  Injection Attempts: 7   Auth Failures: 12   Rate Limits: 3 │
│  ┌──────────────────────────────────────────────┐      │
│  │ 14:32 ⚠️  Injection detected (pattern: ignore) │      │
│  │ 14:28 🔴  Auth failure (invalid key)           │      │
│  │ 14:15 🟡  Rate limit exceeded (IP: 192.168.x)  │      │
│  └──────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────┘
```

---

### Priority 4: Live Request Feed (Medium Impact, Low Effort)

**Goal:** Show the last N requests in real-time, like a live tail.

| Task | Description | Data Source | Effort |
|------|-------------|-------------|--------|
| **P4.1** | Store last 50 audit entries in memory | Audit middleware | 1h |
| **P4.2** | Expose via `GET /logs?limit=50` | New endpoint | 1h |
| **P4.3** | Add live request feed to dashboard | Frontend SSE or polling | 2h |

**New Section: "Live Request Feed"**

```
┌─────────────────────────────────────────────────────────┐
│  📡 Live Requests                              [Filter▼] │
│  14:32:01  POST /learn          200  2.3s  flash        │
│  14:31:58  POST /coach          200  1.8s  flash        │
│  14:31:55  GET  /health         200  0.01s --           │
│  14:31:50  POST /navigator      401  0.00s --           │
│  14:31:45  POST /learn          200  4.1s  pro          │
└─────────────────────────────────────────────────────────┘
```

---

### Priority 5: Environment & Config Viewer (Low Impact, Low Effort)

**Goal:** Show current deployment configuration (masked for security).

| Task | Description | Data Source | Effort |
|------|-------------|-------------|--------|
| **P5.1** | Create `GET /config` endpoint | `core/config.py` (masked values) | 1h |
| **P5.2** | Add config viewer section | Frontend display | 1h |

**New Endpoint: `GET /config`**

```json
{
  "google_api_key": "AIza***...***",
  "primary_model": "gemini-2.5-flash",
  "secondary_model": "gemini-2.5-pro",
  "allowed_origins": ["http://localhost:3000"],
  "cors_origins_count": 1,
  "cache_ttl_seconds": 600,
  "cache_max_size": 100,
  "rate_limit_per_minute": 30,
  "cb_threshold": 3,
  "cb_cooldown_seconds": 60,
  "api_keys_count": 1
}
```

---

### Priority 6: Test Coverage Tracker (Low Impact, Medium Effort)

**Goal:** Show test results and coverage trends.

| Task | Description | Data Source | Effort |
|------|-------------|-------------|--------|
| **P6.1** | Run `pytest --tb=short` on deploy/nightly | CI script | 2h |
| **P6.2** | Store results in JSON file | `tests/results.json` | 1h |
| **P6.3** | Display test results in dashboard | Frontend section | 2h |

---

## 3. Implementation Roadmap

### Phase A: Quick Wins (1-2 days)

| # | Task | Impact | Effort |
|---|------|--------|--------|
| P1.1 | Live /health polling | 🔴 High | 2h |
| P1.2 | Circuit breaker visual | 🔴 High | 1h |
| P1.3 | Cache + active IPs | 🟡 Medium | 1h |
| P1.4 | Uptime counter | 🟡 Medium | 30m |
| P1.5 | System status header | 🔴 High | 1h |
| P3.1-3.3 | Security event tracking | 🟡 Medium | 3h |
| P5.1-5.2 | Config viewer | 🟢 Low | 2h |

**Total: ~11 hours**

### Phase B: Metrics Foundation (2-3 days)

| # | Task | Impact | Effort |
|---|------|--------|--------|
| P2.1 | Create /metrics endpoint | 🔴 High | 3h |
| P2.2-2.4 | Request/error/latency counters | 🔴 High | 4h |
| P2.5-2.7 | Metrics charts in dashboard | 🔴 High | 6h |
| P3.4-3.5 | Security events section | 🟡 Medium | 3h |

**Total: ~16 hours**

### Phase C: Live Feed & Polish (1-2 days)

| # | Task | Impact | Effort |
|---|------|--------|--------|
| P4.1-4.3 | Live request feed | 🟡 Medium | 4h |
| P6.1-6.3 | Test coverage tracker | 🟢 Low | 5h |

**Total: ~9 hours**

---

## 4. New Sections Added to Dashboard

### 4.1 System Health Bar (replaces static module cards)

Real-time system status with:
- 🟢/🟡/🔴 health indicator
- Uptime counter
- Cache size
- Active IP count
- Circuit breaker state
- Current model in use

### 4.2 Request Metrics Dashboard (new section)

Charts showing:
- Request volume over time (last 1h / 24h / 7d)
- Latency percentiles (p50, p95, p99) per endpoint
- Error rate trend
- Endpoint usage breakdown (pie chart)
- Model usage distribution (pie chart)

### 4.3 Security Events (new section)

- Injection attempt counter + recent attempts
- Auth failure counter + recent failures
- Rate limit block counter

### 4.4 Live Request Feed (new section)

- Real-time scrolling list of recent requests
- Shows: timestamp, method, endpoint, status, latency, model
- Filterable by endpoint, status, time range
- Auto-scrolls with pause on hover

### 4.5 Configuration Viewer (new section)

- Current environment variables (API keys masked)
- Model configuration
- Rate limiting settings
- Circuit breaker settings
- Cache configuration

### 4.6 Test Results (new section)

- Last test run results
- Pass/fail counts
- Coverage percentage (when available)
- Test execution time

---

## 5. Backend Changes Required

### New Files

| File | Purpose |
|------|---------|
| `core/metrics.py` | In-memory metrics collector |
| `api/metrics.py` | `GET /metrics` endpoint |
| `api/logs.py` | `GET /logs` endpoint (live feed) |
| `api/config.py` | `GET /config` endpoint (masked config) |

### Modified Files

| File | Changes |
|------|---------|
| `core/audit.py` | Add metrics counter increments |
| `core/auth.py` | Add auth failure counter |
| `core/sanitizer.py` | Add injection attempt counter |
| `core/rate_limiter.py` | Add rate limit block counter |
| `orchestrator.py` | Register new routes |
| `docs/operations-center.html` | Major UI additions |

### No New Dependencies

All metrics are tracked in-memory using Python dicts and lists. No Redis, Prometheus, or external services required. This keeps the system simple and dependency-free.

---

## 6. Data Flow Diagram

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│   Request    │────▶│  Middleware   │────▶│  Audit Logger   │
│  (user)      │     │  (auth, etc) │     │  (structured)   │
└─────────────┘     └──────────────┘     └────────┬────────┘
                                                   │
                           ┌───────────────────────┼───────────────────────┐
                           │                       │                       │
                    ┌──────▼──────┐         ┌──────▼──────┐         ┌──────▼──────┐
                    │  Metrics    │         │  Audit Log  │         │  Circuit    │
                    │  Collector  │         │  (last 50)  │         │  Breaker    │
                    └──────┬──────┘         └──────┬──────┘         └──────┬──────┘
                           │                       │                       │
                    ┌──────▼───────────────────────▼───────────────────────▼──────┐
                    │                        /metrics + /health + /logs           │
                    └────────────────────────────────────┬────────────────────────┘
                                                         │
                    ┌────────────────────────────────────▼────────────────────────┐
                    │              Operations Center Dashboard                    │
                    │  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐   │
                    │  │Health│ │Metric│ │Secur │ │Live  │ │Conf  │ │Test  │   │
                    │  │  Bar │ │Chart │ │Events│ │Feed  │ │View  │ │Res   │   │
                    │  └──────┘ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘   │
                    │  ┌──────────────────────────────────────────────────────┐   │
                    │  │          Existing: Kanban + Burn-down + RCA          │   │
                    │  └──────────────────────────────────────────────────────┘   │
                    └─────────────────────────────────────────────────────────────┘
```

---

## 7. API Endpoints Summary

| Endpoint | Method | Purpose | Auth Required |
|----------|--------|---------|---------------|
| `/health` | GET | System health + circuit breaker + cache | No |
| `/metrics` | GET | Aggregated request metrics | Yes (API key) |
| `/logs` | GET | Last N audit log entries | Yes (API key) |
| `/config` | GET | Current config (masked) | Yes (API key) |

---

## 8. Success Metrics

After implementing this upgrade, the Operations Center should be able to:

| Metric | Before | After |
|--------|--------|-------|
| **Data freshness** | Static (manual edit) | Live (5s polling) |
| **System visibility** | 0% | 80%+ |
| **Time to detect issues** | Manual inspection | <30s (automated alerts) |
| **Debugging capability** | Read logs manually | Live feed + filtered view |
| **Security awareness** | None | Real-time injection/auth tracking |
| **Performance monitoring** | None | Latency percentiles + error rates |

---

## 9. Future Enhancements (Post-Upgrade)

| Enhancement | Description | Effort |
|-------------|-------------|--------|
| **Alerting** | Webhook/Slack alerts on circuit breaker OPEN | 4h |
| **Historical data** | Persist metrics to SQLite for trend analysis | 1d |
| **WebSocket live feed** | Replace polling with Server-Sent Events | 4h |
| **Cost tracking** | Estimate Gemini API costs per request | 2h |
| **User analytics** | Track concept popularity, language distribution | 1d |
| **A/B testing dashboard** | Compare model performance | 2d |
