# Vernacular Bridge — App Overview

**Repository:** [github.com/nadana1985/vernacular-bridge](https://github.com/nadana1985/vernacular-bridge)

---

## What Is This Project?

**Vernacular Bridge** is a bilingual academic bridging platform that transforms Tamil-medium understanding into confident academic English performance for first-generation college students in Indian government universities. It's not just translation — it's a cognitive bridge that combines concept explanation, exam preparation, and writing coaching into a unified AI-powered system.

---

## The Problem

45% of undergraduate students in Indian government universities are first-generation college students. They have strong foundational knowledge from Tamil-medium schools, but higher education operates entirely in English — textbooks, instruction, and examinations. The resulting language-knowledge gap leads to academic failure attributable to **language barriers, not intellectual incapacity**.

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Python 3.12+, FastAPI 0.115, Uvicorn |
| **LLM** | Google Gemini API (google-genai 0.3.0) — 2.5 Flash / 2.5 Pro |
| **Frontend** | Next.js 16, React 19, TypeScript 5, Tailwind CSS 4 |
| **Schema Validation** | Pydantic v2.9 (backend), Zod (frontend) |
| **State Management** | Zustand 5 (frontend), React Context for learning state |
| **API Client** | Fetch-based API layer with proxy rewrites |
| **Configuration** | pydantic-settings (`.env` loaded automatically) |
| **Caching** | cachetools TTLCache (in-memory) |
| **Architecture** | Layered: `api/` → `services/` → `core/` → `models/` |

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  CLIENT (Next.js 16)                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐ │
│  │   Pages   │ │Components│ │  Store   │ │ API Client │ │
│  │ (App Rtr) │ │ (Cards,  │ │(Zustand) │ │            │ │
│  │           │ │  Coach,  │ │          │ │            │ │
│  │           │ │  Nav)    │ │          │ │            │ │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └─────┬──────┘ │
│       └─────────────┴────────────┴─────────────┘        │
└────────────────────────┬────────────────────────────────┘
                         │ REST API (JSON)
┌────────────────────────▼────────────────────────────────┐
│              SERVER (FastAPI + Python)                    │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │               api/  (Thin Controllers)            │   │
│  │  ┌────────┐ ┌────────┐ ┌──────────┐ ┌────────┐  │   │
│  │  │ /learn │ │ /coach │ │/navigator│ │/full   │  │   │
│  │  │ /generate│ │        │ │          │ │-flow   │  │   │
│  │  └───┬────┘ └───┬────┘ └────┬─────┘ └───┬────┘  │   │
│  │      │          │           │            │        │   │
│  │  ┌───▼──────────▼───────────▼────────────▼────┐  │   │
│  │  │          services/ (Business Logic)         │  │   │
│  │  │  learn_service │ coach_service              │  │   │
│  │  │  navigator_service │ retrieval_service      │  │   │
│  │  └──────────────────┬─────────────────────────┘  │   │
│  └─────────────────────┼────────────────────────────┘   │
│                        │                                 │
│  ┌─────────────────────▼────────────────────────────┐   │
│  │               core/ (Infrastructure)              │   │
│  │  ┌──────────────┐  ┌──────────────┐              │   │
│  │  │  llm_client  │  │    config    │              │   │
│  │  │  (Gemini +   │  │ (pydantic-   │              │   │
│  │  │   CB + retry)│  │  settings)   │              │   │
│  │  └──────────────┘  └──────────────┘              │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────────────┐  │   │
│  │  │  auth    │ │  cache   │ │  rate_limiter    │  │   │
│  │  │(API Key) │ │(TTLCache)│ │(per-IP sliding)  │  │   │
│  │  └──────────┘ └──────────┘ └──────────────────┘  │   │
│  │  ┌──────────────┐ ┌────────────┐ ┌────────────┐  │   │
│  │  │ safety_guard │ │ sanitizer  │ │   audit     │  │   │
│  │  │(fact/keyword │ │(injection  │ │(structured  │  │   │
│  │  │    lock)     │ │ protection)│ │   JSON log) │  │   │
│  │  └──────────────┘ └────────────┘ └────────────┘  │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────┐  │
│  │ Models   │ │ Parsers  │ │  Utils   │ │   Data    │  │
│  │(Pydantic)│ │(JSON     │ │(Prompt   │ │(Entitle-  │  │
│  │          │ │ extract, │ │ Builder) │ │ments,     │  │
│  │          │ │ normalize│ │          │ │Processes) │  │
│  └──────────┘ └──────────┘ └──────────┘ └───────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
vernacular-bridge/
├── orchestrator.py              # Thin FastAPI entry point (<100 lines)
│
├── api/                         # Thin route controllers
│   ├── learn.py                 # POST /learn, POST /generate
│   ├── coach.py                 # POST /coach
│   ├── navigator.py             # POST /navigator/explain
│   ├── full_flow.py             # POST /full-flow
│   ├── retrieval.py             # GET /entitlements, GET /processes
│   └── health.py                # GET /health
│
├── core/                        # Infrastructure & cross-cutting concerns
│   ├── config.py                # pydantic-settings configuration singleton
│   ├── llm_client.py            # Gemini API client + 3-state circuit breaker
│   ├── auth.py                  # API key validation (X-API-Key header)
│   ├── cache.py                 # TTLCache for learn responses
│   ├── rate_limiter.py          # Per-IP sliding-window rate limiter
│   ├── safety_guard.py          # Fact-lock & keyword-lock hallucination prevention
│   ├── sanitizer.py             # Prompt injection protection (XML delimiters)
│   └── audit.py                 # Structured JSON audit logging middleware
│
├── services/                    # Business logic layer
│   ├── learn_service.py         # Learn endpoint orchestration
│   ├── coach_service.py         # Writing coach orchestration
│   ├── navigator_service.py     # Navigator explanation orchestration
│   └── retrieval_service.py     # Data loading & retrieval
│
├── parsers/                     # LLM output parsing
│   ├── json_extractor.py        # Extract JSON from LLM text responses
│   └── normalize.py             # Normalize LLM output to schema
│
├── models/                      # Pydantic request/response schemas
│   ├── request.py               # QueryRequest, FullFlowRequest, LanguageConfig
│   ├── contracts.py             # OutputSchema with @model_validator normalization
│   ├── coach.py                 # CoachRequest, CoachResponse
│   ├── navigator.py             # NavigatorExplainRequest, NavigatorExplainResponse
│   └── full_flow.py             # FullFlowResponse (unified wrapper)
│
├── validators/                  # Content validation
│   ├── validators.py            # Tamil ratio, semantic alignment, MCQ quality
│   └── coach_validator.py       # Coach output normalization & logic guards
│
├── utils/                       # Prompt construction & input processing
│   ├── prompt_builder.py        # LLM prompt assembly
│   ├── concept_resolver.py      # Tanglish/Tamil input normalization
│   └── preprocessing.py         # Input preprocessing utilities
│
├── verification/                # Adversarial testing & scoring
│   ├── adversarial_generator.py # Generate adversarial test cases
│   ├── run_verification.py      # Execute verification pipeline
│   ├── scenarios.yaml           # Test scenario definitions
│   ├── scoring.py               # Response quality scoring
│   └── verifier.py              # Verification logic
│
├── data/                        # Pre-loaded datasets
│   ├── entitlements.json        # 7 government schemes/scholarships
│   └── processes.json           # 3 university administrative processes
│
├── tests/                       # Test suite (124 tests, 15 categories)
│   ├── unit/
│   │   └── test_normalize.py    # MCQ/text normalization tests
│   ├── test_contracts.py        # OutputSchema validation tests
│   ├── test_coach.py            # Coach endpoint tests
│   ├── test_navigator_explain.py# Navigator tests (require live Gemini)
│   └── test_retrieval.py        # Data retrieval tests
│
├── docs/                        # Documentation & operations
│   ├── operations-center.html   # Interactive operations dashboard
│   ├── data/
│   │   ├── rca-entries.json     # Root cause analysis entries
│   │   ├── kanban-issues.json   # Kanban task tracker data
│   │   ├── tests-data.js        # 124 test definitions for dashboard
│   │   ├── rca-data.js          # RCA data (JS wrapper for file:// compat)
│   │   └── kanban-data.js       # Kanban data (JS wrapper for file:// compat)
│   ├── contracts.md             # Schema contract documentation
│   ├── deployment.md            # Deployment guide
│   └── engineering_audit.md     # Engineering audit report
│
├── vernacular-bridge-ui/        # Next.js frontend application
│   └── src/
│       ├── app/                 # Next.js App Router pages
│       │   ├── page.tsx         # Main learning dashboard
│       │   ├── dashboard/       # Analytics dashboard
│       │   └── command-center/  # Operations command center
│       ├── components/          # React components
│       │   ├── cards/           # Academic, Decoder, MCQ, Steps, Tamil cards
│       │   ├── coach/           # CoachTextArea, ImprovedAnswer, ScoreCard
│       │   ├── navigator/       # NavigatorList, NavigatorDetail
│       │   ├── learning/        # ConceptCard, MCQSection, StepsList
│       │   ├── command-center/  # CoachingPanel, LearningPanel, NavigatorPanel, TopQueryBar
│       │   ├── InteractiveText.tsx  # Hover-isolated interactive text
│       │   ├── input-panel.tsx  # Concept query input
│       │   └── navbar.tsx       # Navigation bar
│       ├── context/             # React context providers
│       │   └── LearningContext.tsx
│       ├── store/               # Zustand state management
│       │   └── commandCenterStore.ts
│       ├── lib/api/             # API client functions
│       │   ├── coach.ts
│       │   ├── fullFlow.ts
│       │   └── navigator.ts
│       └── utils/
│           └── learning-engine.ts # Interactive text tooltip engine
│
├── .env                         # Environment variables (not in git)
├── .env.example                 # Environment template
├── requirements.txt             # Python dependencies
├── requirements-dev.txt         # Development dependencies
├── Dockerfile                   # Container build
├── Procfile                     # Process manager config
└── VERNACULAR_BRIDGE_OVERVIEW.md# This file
```

---

## Core Features

### 1. 🧠 Bilingual Concept Explainer (`/learn`)
- Receives a concept query in Tamil, Tanglish, or English
- Generates **simple Tamil explanation** with culturally situated examples
- Generates **precise academic English** with clear step-by-step breakdown
- Produces exam-ready MCQs including:
  - Understanding checks
  - Misconception traps
  - Application-based questions

### 2. 📝 Academic Question Decoder (embedded in `/learn`)
- Identifies question type: define, explain, compare, analyze, diagram, short_note
- Provides **section-by-section answer templates**
- Maps question intent to expected academic structure

### 3. ✍️ Writing Coach (`/coach`)
- Evaluates student draft answers
- Provides **structured feedback** with scoring (0–10)
- Gives specific improvement suggestions with missing points
- Normalizes output for consistency (markdown stripping, length control)

### 4. 🧭 Navigator (`/navigator/explain`)
- Bilingual explanation of dataset items (entitlements & processes)
- **Fact-lock hallucination protection** — prevents LLM from inventing numbers/URLs
- **Keyword-lock** — ensures core semantic meaning is preserved across languages

### 5. 🔗 Unified Orchestration (`/full-flow`)
- Runs Learn, Coach, and Navigator **in parallel**
- Returns unified response with all three outputs
- Optimized for speed and comprehensive student support

### 6. 📊 Data Retrieval (`/entitlements`, `/processes`)
- Query pre-loaded government datasets
- 7 entitlement schemes + 3 university processes
- Keyword-based search and filtering

---

## Safety & Quality System

| Mechanism | Location | Purpose |
|-----------|----------|---------|
| **Fact-Lock** | `core/safety_guard.py` | Prevents hallucination — no new numbers/URLs in output |
| **Keyword-Lock** | `core/safety_guard.py` | Ensures core semantic meaning preserved across Tamil ↔ English |
| **Tamil Ratio Validation** | `validators/validators.py` | Enforces ≥60% Tamil Unicode in Tamil explanations |
| **MCQ Quality Guards** | `validators/validators.py` | Rejects trivial, duplicate, or Yes/No MCQs |
| **Generic Phrase Blocker** | `models/contracts.py` | Blocks low-quality LLM output ("identify the concept", etc.) |
| **MCQ Normalization** | `models/contracts.py` | Deduplicates options, aliases correct_answer keys, fixes option count |
| **Circuit Breaker** | `core/llm_client.py` | 3-state CB: CLOSED → OPEN → HALF_OPEN → auto-recovery |
| **Per-IP Rate Limiting** | `core/rate_limiter.py` | 20 requests/minute sliding window per client |
| **Prompt Injection Protection** | `core/sanitizer.py` | XML delimiter wrapping + pattern detection |
| **API Key Auth** | `core/auth.py` | Optional X-API-Key header validation |
| **Structured Output** | `models/contracts.py` | Strict Pydantic schema validation on all responses |
| **Audit Logging** | `core/audit.py` | Structured JSON logs with masked IPs, hashed payloads |

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/full-flow` | POST | Unified orchestration — runs Learn, Coach, and Navigator in parallel |
| `/learn` | POST | Bilingual concept explanation with MCQs |
| `/generate` | POST | Legacy alias for `/learn` |
| `/coach` | POST | Evaluate student answers with structured feedback |
| `/navigator/explain` | POST | Bilingual explanation of dataset items |
| `/entitlements` | GET | Query government entitlements/schemes |
| `/processes` | GET | Query government processes |
| `/health` | GET | Health check with cache, circuit breaker, and data status |

---

## Output Schema

The `OutputSchema` model uses a `@model_validator(mode='before')` that normalizes raw LLM dictionaries before Pydantic field validation. This handles type coercion, missing fields, quality guards, question-type mapping, and MCQ cleanup.

```json
{
  "tamil_simple": "...",
  "english_academic": "...",
  "steps": ["Step 1...", "Step 2...", "Step 3..."],
  "question_decoder": {
    "question_type": "explain",
    "expected_structure": "...",
    "answer_template": "..."
  },
  "mcqs": [
    {
      "question": "...",
      "options": ["A", "B", "C", "D"],
      "correct_answer": "..."
    }
  ]
}
```

**Key validation rules:**
- `tamil_simple`: 10–800 chars, must pass Tamil ratio check (≥60%)
- `english_academic`: 20–1200 chars, must align with MCQ keywords
- `steps`: 2–7 items, no generic phrases allowed
- `mcqs`: Up to 5 questions, each with exactly 4 unique options
- `correct_answer`: Must be one of the 4 options (auto-replaces last option if missing)

---

## Configuration

All configuration is centralized in `core/config.py` via pydantic-settings. Values are loaded from `.env` with sensible defaults:

| Setting | Env Var | Default | Description |
|---------|---------|---------|-------------|
| Google API Key | `GOOGLE_API_KEY` | `""` | Gemini API key |
| Primary Model | `PRIMARY_MODEL` | `gemini-2.5-flash` | Main LLM |
| Secondary Model | `SECONDARY_MODEL` | `gemini-2.5-pro` | Fallback LLM |
| Rate Limit | `RATE_LIMIT_RPM` | `20` | Max requests/min/IP |
| Cache TTL | `CACHE_TTL` | `600` | Cache entry lifetime (seconds) |
| Cache Size | `CACHE_MAX_SIZE` | `100` | Max cached entries |
| CB Threshold | `CB_THRESHOLD` | `3` | Failures before circuit trips |
| CB Cooldown | `CB_COOLDOWN` | `60` | Seconds before CB recovery attempt |
| API Keys | `API_KEYS` | `""` | Comma-separated auth keys (empty = open) |
| Allowed Origins | `ALLOWED_ORIGINS` | `localhost:3000,localhost:7860` | CORS origins |

---

## Frontend

The Next.js 16 frontend provides a rich interactive learning experience:

**Pages:**
- **Main Dashboard** (`/`) — Concept input, bilingual output, MCQs, coaching
- **Analytics Dashboard** (`/dashboard`) — Progress tracking, learning metrics
- **Command Center** (`/command-center`) — Operations monitoring

**Key Components:**
- **InteractiveText** — Hover-isolated tooltips on academic terms (React state-driven)
- **ConceptCard** — Bilingual concept explanation display
- **MCQSection** — Interactive multiple-choice questions
- **StepsList** — Step-by-step breakdown
- **CoachTextArea** — Student answer input with evaluation
- **ScoreCard** — Coach scoring display
- **NavigatorList/Detail** — Entitlement & process browsing

**State Management:** Zustand store for command center, React Context for learning flow.

---

## Test Suite

**124 tests** across **15 categories** with a **97% pass rate** (120 passed, 4 skipped — live Gemini integration tests):

| Category | Tests | Description |
|----------|-------|-------------|
| Coach Validator | 8 | Coach output normalization & logic guards |
| Contract Validation | 13 | OutputSchema field validation & quality guards |
| Navigator Integration | 7 | Navigator endpoint tests (require live API) |
| Data Retrieval | 7 | Entitlement & process data loading |
| Circuit Breaker | 10 | 3-state CB transitions & recovery |
| Learn Cache | 5 | TTL cache hit/miss/eviction |
| LLM Functions | 2 | LLM client helpers |
| Text Normalization | 5 | MCQ correct_answer edge cases |
| Steps Normalization | 6 | Steps list cleanup & dedup |
| Quality Guards | 13 | Generic phrase detection, empty content |
| Question Decoder | 15 | Question type mapping & template generation |
| MCQ Normalization | 12 | Option dedup, alias handling, count fix |
| Input Sanitization | 4 | XML delimiter wrapping |
| Injection Detection | 13 | Prompt injection pattern detection |
| Instruction Prefix | 3 | Safety instruction prefix generation |

Run tests: `python -m pytest tests/ -v --tb=short`

---

## Frontend-Backend Integration

The frontend proxies API requests to the backend via Next.js rewrites in `next.config.ts`:

```typescript
// vernacular-bridge-ui/next.config.ts
async rewrites() {
  return [
    { source: '/api/:path*', destination: 'http://localhost:8000/:path*' },
  ];
}
```

**Quick start:**
```bash
# Backend (port 8000)
pip install -r requirements.txt
python orchestrator.py

# Frontend (port 3000)
cd vernacular-bridge-ui
npm install
npm run dev
```

---

## Operations Center

The `docs/operations-center.html` dashboard provides a static operations overview:

- **Kanban Board** — Task tracker with status columns (36 issues)
- **Burn-Down Chart** — Phase progress visualization
- **Module Status** — 7 module cards with completion status
- **Timeline** — Development phase timeline
- **RCA Tracker** — 22 root cause analysis entries
- **Test Tracker** — 124 test results with category filters

Open directly: `file:///path/to/docs/operations-center.html`

---

## Deployment

- **Dockerfile** — Container build with Python 3.12, system deps, gunicorn
- **Procfile** — Process manager configuration
- **`/health` endpoint** — Production health monitoring with circuit breaker state, cache stats, and data health

---

## Why Not ChatGPT?

| Aspect | Generic LLMs | Vernacular Bridge |
|--------|-------------|-------------------|
| Output Structure | Free-form, inconsistent | Strict bilingual structured JSON |
| Language Control | Mixed tone, possible slang | Controlled textbook Tamil + academic English |
| Exam Focus | General answers | Question decoding + structured templates |
| Consistency | Varies widely | Quality checks + internal consistency |
| Hallucination | No protection | Fact-lock + keyword-lock enforcement |
| Safety | No injection protection | XML delimiters + pattern detection |

---

## Future Expansion

- Support for additional Indian languages (Hindi, Telugu, Kannada)
- Voice-first interface for low-literacy users
- Integration with university syllabus datasets
- Personalized learning paths based on student performance
- Real-time data integration for entitlements/processes

---

*Updated: June 19, 2026 — aligned with latest codebase (124 tests, layered architecture).*
