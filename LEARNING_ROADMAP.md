# LEARNING_ROADMAP.md — Vernacular Bridge Learning Roadmap

**Purpose:** A structured learning path that maps **every technology used in this repo** into a progressive curriculum for a developer to learn the full stack by studying this project's codebase.

**Content Categories (9 Phases):**

---

## Phase 1: Python Foundation (Week 1–2)

### Python 3.12+ Core
- **Type Hints & Dataclasses**: Pydantic models use `str`, `int`, `float`, `list[str]`, `Optional[T]`, `Literal[...]` extensively.
  - Study: `models/request.py` — `QueryRequest`, `FullFlowRequest`, `LanguageConfig`
  - Study: `models/contracts.py` — `OutputSchema`, `MCQ`, `QuestionDecoder`
- **async/await & asyncio**: The entire backend is async-first. Understand `async def`, `await`, `asyncio.gather()`, `asyncio.create_task()`.
  - Study: `services/learn_service.py` — async LLM calls
  - Study: `services/` — all service functions are async
- **Context Managers & Generators**: Used in cache and rate limiter.
  - Study: `core/cache.py` — TTLCache with thread-safe locking
- **Decorators & Metaclasses**: Pydantic uses decorators for field validation.
  - Study: `models/contracts.py` — `@model_validator(mode='before')`, `@field_validator`
- **Error Handling**: Try/except patterns, custom exceptions, graceful degradation.
  - Study: `core/llm_client.py` — circuit breaker exception handling
  - Study: `services/learn_service.py` — fallback responses

**Mini-Project Ideas:**
1. Write a simple async function that fetches data from two APIs concurrently
2. Build a basic TTL cache with `cachetools`
3. Create a Pydantic model with custom validators

### Pydantic v2
- **Models**: `BaseModel` inheritance, field definitions with `Field(...)`.
  - Study: `models/request.py` — all request models
  - Study: `models/coach.py` — `CoachRequest`, `CoachResponse`
- **Validators**: `@field_validator`, `@model_validator(mode='before')`.
  - Study: `models/contracts.py` — the normalization pipeline in `OutputSchema`
- **Settings Management**: `pydantic-settings` for environment configuration.
  - Study: `core/config.py` — `Settings` class with `.env` loading
- **Type Coercion**: Automatic type conversion (string→list, dict→list).
  - Study: `models/contracts.py` — `normalize_raw_llm_output()`

**Code Example:**
```python
# From models/request.py
class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500, description="Concept query")
    language_config: LanguageConfig = Field(default_factory=LanguageConfig)
```

---

## Phase 2: Backend Architecture (Week 2–4)

### FastAPI
- **Routing**: `APIRouter`, `@router.post()`, `@router.get()`.
  - Study: `api/learn.py` — POST /learn, POST /generate routes
  - Study: `api/health.py` — GET /health route
  - Study: `api/coach.py` — POST /coach route
  - Study: `api/navigator.py` — POST /navigator/explain route
  - Study: `api/full_flow.py` — POST /full-flow route
  - Study: `api/retrieval.py` — GET /entitlements, GET /processes routes
- **Request/Response Models**: Pydantic models as route parameters.
  - Study: `api/learn.py` — `request: QueryRequest` parameter
- **Middleware**: CORS, custom audit middleware.
  - Study: `orchestrator.py` — `CORSMiddleware` configuration
  - Study: `core/audit.py` — `AuditMiddleware` class
- **App Initialization**: FastAPI app creation, router mounting.
  - Study: `orchestrator.py` — the entire file (<100 lines, thin entry point)

**Key Pattern — Thin Controllers:**
```python
# From api/learn.py — routes are thin, logic is in services
@router.post("/learn", response_model=OutputSchema)
async def learn(request: QueryRequest):
    result = await learn_service.process(request)
    return result
```

### Layered Architecture
- **`api/`** → Thin route controllers (HTTP handling only)
- **`services/`** → Business logic (orchestration, LLM calls)
- **`core/`** → Infrastructure (LLM client, caching, rate limiting, safety)
- **`models/`** → Pydantic schemas (request/response validation)
- **`validators/`** → Content validation (Tamil ratio, MCQ quality)
- **`parsers/`** → LLM output parsing (JSON extraction, normalization)
- **`utils/`** → Prompt construction, input preprocessing

  - Study: `orchestrator.py` — how routers mount
  - Study: `api/learn.py` → `services/learn_service.py` → `core/llm_client.py` — the request lifecycle

**Dependency Flow:**
```
api/ → services/ → core/ → models/
                ↘ parsers/
                ↘ validators/
```

**Mini-Project Ideas:**
1. Add a new endpoint (e.g., `/summarize`) following the layered pattern
2. Create a new Pydantic model with custom validators
3. Build a simple middleware that logs request timing

---

## Phase 3: LLM Integration & Prompt Engineering (Week 4–6)

### Google Gemini API
- **SDK**: `google-genai` for Python.
  - Study: `core/llm_client.py` — `GeminiClient` class
- **Async Calls**: Non-blocking LLM requests.
  - Study: `core/llm_client.py` — `generate()` method
- **Model Selection**: Primary (Flash) vs Secondary (Pro) models.
  - Study: `core/config.py` — `PRIMARY_MODEL`, `SECONDARY_MODEL`
- **Error Handling**: Quota exhaustion, timeouts, 5xx errors.
  - Study: `core/llm_client.py` — exception handling in `generate()`

**Code Example:**
```python
# From core/llm_client.py — simplified
async def generate(self, prompt: str, model: str = None) -> str:
    model = model or self.primary_model
    try:
        response = await self.client.aio.models.generate_content(
            model=model, contents=prompt
        )
        return response.text
    except Exception as e:
        self.circuit_breaker.record_failure()
        raise LLMError(f"Generation failed: {e}")
```

### Prompt Engineering
- **Structured Prompts**: System instructions + user context + output format.
  - Study: `utils/prompt_builder.py` — all prompt construction functions
- **Language Control**: Explicit instructions for bilingual output.
  - Study: `utils/prompt_builder.py` — learn prompt with Tamil/English instructions
- **Cultural Context**: Tamil Nadu education system grounding.
  - Study: `utils/prompt_builder.py` — cultural context injection
- **Negative Instructions**: "Do not invent numbers or URLs."
  - Study: `utils/prompt_builder.py` — fact-lock instructions in prompts

**Key Patterns:**
1. **Few-shot examples** in prompts for output format consistency
2. **Language-switching instructions** ("respond in Tamil for tamil_simple")
3. **Negative constraints** ("do not hallucinate numbers")
4. **Output schema templates** embedded in prompts

### JSON Extraction from LLM Text
- **Multi-strategy parsing**: Direct JSON → code block → object extraction.
  - Study: `parsers/json_extractor.py` — the extraction pipeline
- **Cleanup**: Regex for trailing commas, single quotes, comments.
  - Study: `parsers/json_extractor.py` — cleanup patterns
- **Fallback**: Valid schema with error message when parsing fails.
  - Study: `parsers/json_extractor.py` — fallback response

**Code Example:**
```python
# From parsers/json_extractor.py — simplified pipeline
def extract_json(text: str) -> dict:
    # Strategy 1: Direct parse
    try: return json.loads(text)
    except: pass
    # Strategy 2: Code block extraction
    match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
    if match: return json.loads(match.group(1))
    # Strategy 3: Object extraction
    start, end = text.find('{'), text.rfind('}')
    if start != -1 and end != -1:
        return json.loads(text[start:end+1])
    # Fallback
    return {"error": "Could not parse LLM response"}
```

---

## Phase 4: Safety & Quality System (Week 6–8)

### Fact-Lock (Hallucination Prevention)
- **Mechanism**: Extract numbers/URLs from input, verify they appear in output.
  - Study: `core/safety_guard.py` — `verify_fact_lock()` function
- **Detection**: New numbers in output = potential hallucination.
  - Study: `core/safety_guard.py` — `new_numbers` detection
- **Application**: Navigator data (government schemes) is most critical.
  - Study: `services/navigator_service.py` — fact-lock usage

**Code Example:**
```python
# From core/safety_guard.py — simplified
def verify_fact_lock(input_text: str, output_text: str) -> dict:
    input_numbers = set(re.findall(r'\d+\.?\d*', input_text))
    output_numbers = set(re.findall(r'\d+\.?\d*', output_text))
    new_numbers = output_numbers - input_numbers  # Potential hallucination
    return {"passed": len(new_numbers) == 0, "new_numbers": list(new_numbers)}
```

### Keyword-Lock (Semantic Preservation)
- **Mechanism**: Extract key phrases, verify they appear in translated output.
  - Study: `core/safety_guard.py` — `verify_keyword_lock()` function
- **Cross-language**: Ensures Tamil↔English semantic alignment.
  - Study: `validators/validators.py` — semantic alignment validation
- **Coverage Score**: `matched_keywords / total_keywords`.
  - Study: `core/safety_guard.py` — coverage computation

### Tamil Ratio Validation
- **Unicode Range**: Tamil characters are U+0B80–U+0BFF.
  - Study: `validators/validators.py` — `calculate_tamil_ratio()` function
- **Threshold**: 60% (0.6) — Tamil Unicode characters must be ≥60% of total.
  - Study: `validators/validators.py` — `TAMIL_RATIO_THRESHOLD`
- **Confidence Adjustment**: Ratio below threshold reduces confidence score.
  - Study: `validators/validators.py` — confidence computation

**Code Example:**
```python
# From validators/validators.py — simplified
TAMIL_RATIO_THRESHOLD = 0.6

def calculate_tamil_ratio(text: str) -> float:
    if not text: return 0.0
    tamil_chars = sum(1 for c in text if '\u0B80' <= c <= '\u0BFF')
    total_chars = sum(1 for c in text if not c.isspace())
    return tamil_chars / total_chars if total_chars > 0 else 0.0
```

### MCQ Quality Guards
- **Trivial Rejection**: Blocks Yes/No questions, single-word answers.
  - Study: `validators/validators.py` — MCQ validation functions
- **Duplicate Detection**: Fuzzy matching (Levenshtein distance).
  - Study: `validators/validators.py` — duplicate detection
- **Option Enforcement**: Exactly 4 unique options per question.
  - Study: `models/contracts.py` — `normalize_raw_llm_output()` MCQ cleanup
- **Correct Answer Validation**: Must match one of 4 options.
  - Study: `models/contracts.py` — `validate_correct_answer_in_options()`

### Generic Phrase Blocking
- **Blocklist**: "identify the concept", "explain briefly", "discuss the topic".
  - Study: `models/contracts.py` — `GENERIC_PHRASES` list
- **Application**: Catches low-quality LLM template responses.
  - Study: `models/contracts.py` — `block_generic_phrases()` function

### Circuit Breaker Pattern
- **3-State Machine**: CLOSED → OPEN → HALF_OPEN → CLOSED.
  - Study: `core/llm_client.py` — `CircuitBreaker` class
- **Threshold**: 3 consecutive failures → OPEN state.
  - Study: `core/config.py` — `CB_THRESHOLD`
- **Cooldown**: 60 seconds before HALF_OPEN recovery attempt.
  - Study: `core/config.py` — `CB_COOLDOWN`
- **Health Monitoring**: `/health` endpoint exposes circuit breaker state.
  - Study: `api/health.py` — health response structure

**State Diagram:**
```
CLOSED ──(3 failures)──→ OPEN ──(60s cooldown)──→ HALF_OPEN
  ↑                                                  │
  └──────────────(success)────────────────────────────┘
                                                     │
                                              (failure)→ OPEN
```

### Prompt Injection Protection
- **XML Delimiters**: User input wrapped in `<user_input>...</user_input>`.
  - Study: `core/sanitizer.py` — delimiter wrapping
- **Pattern Detection**: Regex for "ignore previous instructions", etc.
  - Study: `core/sanitizer.py` — injection pattern detection
- **Audit Logging**: Structured JSON logs with masked IPs.
  - Study: `core/audit.py` — `AuditMiddleware`

---

## Phase 5: Frontend Engineering (Week 8–10)

### Next.js 16 App Router
- **Pages**: `page.tsx` (main), `dashboard/page.tsx`, `command-center/page.tsx`.
  - Study: `src/app/page.tsx` — main learning dashboard
  - Study: `src/app/dashboard/page.tsx` — analytics dashboard
  - Study: `src/app/command-center/page.tsx` — operations center
- **Layout**: `layout.tsx` wraps all pages with providers.
  - Study: `src/app/layout.tsx` — provider configuration
- **API Proxy**: `next.config.ts` rewrites `/api/*` → backend.
  - Study: `next.config.ts` — rewrite rules

**Code Example:**
```typescript
// From next.config.ts
async rewrites() {
  return [
    { source: '/api/:path*', destination: 'http://localhost:8000/:path*' },
  ];
}
```

### React 19 Components
- **Cards**: Academic, Decoder, MCQ, Steps, Tamil cards.
  - Study: `src/components/cards/` — 5 card components
- **Coach**: TextArea, ImprovedAnswer, ScoreCard.
  - Study: `src/components/coach/` — 3 coach components
- **Navigator**: List, Detail views.
  - Study: `src/components/navigator/` — 2 navigator components
- **Learning**: ConceptCard, MCQSection, StepsList.
  - Study: `src/components/learning/` — 3 learning components
- **Command Center**: CoachingPanel, LearningPanel, NavigatorPanel, TopQueryBar.
  - Study: `src/components/command-center/` — 4 command center components

### TypeScript
- **Interfaces**: Request/response types, component props.
  - Study: `src/lib/api/coach.ts` — API client types
- **Generics**: Pydantic models map to TypeScript types.
  - Study: `src/lib/api/` — all API client files
- **Strict Mode**: `tsconfig.json` strict configuration.
  - Study: `tsconfig.json` — compiler options

### Tailwind CSS 4
- **Utility Classes**: Responsive design, spacing, typography.
  - Study: `src/app/globals.css` — custom CSS + Tailwind directives
- **Dark Mode**: Theme support.
  - Study: `src/app/globals.css` — dark mode configuration
- **Custom Properties**: CSS variables for theming.
  - Study: `src/app/globals.css` — CSS custom properties

### Zustand 5 (State Management)
- **Store**: Command center state with actions.
  - Study: `src/store/commandCenterStore.ts` — Zustand store definition
- **Slices**: Multiple state slices in one store.
  - Study: `src/store/commandCenterStore.ts` — state + actions

### React Context
- **LearningContext**: Current query, response, loading state.
  - Study: `src/context/LearningContext.tsx` — context provider

### Interactive Text (Hover Isolation)
- **React State**: `hoveredIndex` tracks which word is hovered.
  - Study: `src/components/InteractiveText.tsx` — the full component
- **Event Handlers**: `onMouseEnter`/`onMouseLeave` with timeout.
  - Study: `src/components/InteractiveText.tsx` — hover handling
- **Tooltip Positioning**: `bottom-full` for above-word tooltips.
  - Study: `src/components/InteractiveText.tsx` — tooltip rendering

**Key Pattern — Hover Isolation:**
```typescript
// From InteractiveText.tsx — simplified
const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);
const hoverTimeoutRef = useRef<NodeJS.Timeout | null>(null);

const handleMouseEnter = (index: number) => {
  if (hoverTimeoutRef.current) clearTimeout(hoverTimeoutRef.current);
  setHoveredIndex(index);
};

const handleMouseLeave = () => {
  hoverTimeoutRef.current = setTimeout(() => setHoveredIndex(null), 100);
};
```

### API Client Layer
- **Fetch-based**: Relative URLs (`/api/learn`) proxied to backend.
  - Study: `src/lib/api/coach.ts` — coach API client
  - Study: `src/lib/api/fullFlow.ts` — full-flow API client
  - Study: `src/lib/api/navigator.ts` — navigator API client
- **Error Handling**: HTTP error detection, response parsing.
  - Study: `src/lib/api/` — all API client files

---

## Phase 6: Data & Caching (Week 10–11)

### JSON Data Files
- **Entitlements**: 7 government schemes (Pudhumai Penn, First Graduate, etc.).
  - Study: `data/entitlements.json` — schema and content
- **Processes**: 3 university processes (Semester Registration, etc.).
  - Study: `data/processes.json` — schema and content
- **Data Loading**: Service layer loads and searches data.
  - Study: `services/retrieval_service.py` — data loading and keyword search

### In-Memory Caching
- **TTLCache**: `cachetools.TTLCache` with configurable TTL.
  - Study: `core/cache.py` — `LearnCache` class
- **Key Generation**: SHA-256 hash of normalized query + endpoint.
  - Study: `core/cache.py` — cache key computation
- **Eviction**: LRU when max size (100) is reached.
  - Study: `core/cache.py` — eviction policy

**Code Example:**
```python
# From core/cache.py — simplified
class LearnCache:
    def __init__(self, max_size=100, ttl=600):
        self._cache = TTLCache(maxsize=max_size, ttl=ttl)
        self._lock = threading.Lock()

    def get_or_compute(self, key: str, compute_fn):
        with self._lock:
            if key in self._cache:
                return self._cache[key]
            result = compute_fn()
            self._cache[key] = result
            return result
```

### Per-IP Rate Limiting
- **Sliding Window**: 20 requests per minute per IP.
  - Study: `core/rate_limiter.py` — `RateLimiter` class
- **Window Cleanup**: Automatic removal of stale entries.
  - Study: `core/rate_limiter.py` — cleanup logic
- **Response**: 429 Too Many Requests with `Retry-After` header.
  - Study: `core/rate_limiter.py` — rate limit exceeded response

---

## Phase 7: Testing & Quality (Week 11–12)

### Pytest
- **Unit Tests**: Test individual functions with mocked dependencies.
  - Study: `tests/test_contracts.py` — OutputSchema validation tests
  - Study: `tests/test_coach.py` — Coach endpoint tests
- **Integration Tests**: Test service layer with mocked LLM.
  - Study: `tests/test_retrieval.py` — data retrieval tests
- **End-to-End Tests**: Test with live Gemini API (skipped in CI).
  - Study: `tests/test_navigator_explain.py` — live API tests

### Test Categories (124 tests, 15 categories)
- **Coach Validator** (8): Score normalization, markdown stripping.
  - Study: `tests/test_coach.py`
- **Contract Validation** (13): OutputSchema field validation.
  - Study: `tests/test_contracts.py`
- **Circuit Breaker** (10): State transitions, timeout, recovery.
  - Study: `tests/test_contracts.py` — circuit breaker tests
- **Quality Guards** (13): Generic phrase detection, empty content.
  - Study: `tests/test_contracts.py`
- **Question Decoder** (15): Type mapping, template generation.
  - Study: `tests/test_contracts.py`
- **MCQ Normalization** (12): Option dedup, alias handling.
  - Study: `tests/test_contracts.py`
- **Injection Detection** (13): Prompt injection patterns.
  - Study: `tests/test_contracts.py`

### Mocking Strategy
- **LLM Mocking**: `unittest.mock.patch` for `core/llm_client.py`.
  - Study: `tests/test_contracts.py` — fixture-based mocking
- **Fixture Data**: Pre-defined LLM output dictionaries.
  - Study: `tests/` — test fixtures

**Running Tests:**
```bash
# All tests
python -m pytest tests/ -v --tb=short

# Specific category
python -m pytest tests/test_contracts.py -v

# With coverage
python -m pytest tests/ --cov=. --cov-report=html
```

---

## Phase 8: DevOps & Deployment (Week 12–13)

### Docker
- **Dockerfile**: Python 3.12, system deps, gunicorn.
  - Study: `Dockerfile` — container build configuration
- **Procfile**: Process manager configuration.
  - Study: `Procfile` — production process config

### Environment Configuration
- **`.env` Files**: API keys, model selection, rate limits.
  - Study: `.env.example` — all environment variables
- **pydantic-settings**: Type-safe config loading.
  - Study: `core/config.py` — `Settings` class

### CORS Configuration
- **Origins**: `ALLOWED_ORIGINS` from settings.
  - Study: `orchestrator.py` — `CORSMiddleware` setup
- **Methods/Headers**: Allow all for development.
  - Study: `orchestrator.py` — CORS configuration

### Health Monitoring
- **`/health` Endpoint**: Cache size, circuit breaker state, data status.
  - Study: `api/health.py` — health response structure
- **Structured Logging**: JSON logs with masked IPs.
  - Study: `core/audit.py` — `AuditMiddleware`

**Deployment Commands:**
```bash
# Docker build
docker build -t vernacular-bridge .

# Run container
docker run -p 8000:8000 -e GOOGLE_API_KEY=xxx vernacular-bridge

# Local development
pip install -r requirements.txt
python orchestrator.py
```

---

## Phase 9: Architecture Patterns (Ongoing)

### Layered Architecture
- **Separation of Concerns**: Each layer has a single responsibility.
  - Study: `api/` → `services/` → `core/` → `models/` — the full dependency chain
- **Thin Controllers**: `api/` files are <30 lines each.
  - Study: `api/learn.py` — minimal route logic
- **Service Abstraction**: Business logic isolated from HTTP handling.
  - Study: `services/learn_service.py` — orchestration logic

### Parallel Orchestration
- **asyncio.gather()**: Run multiple LLM calls concurrently.
  - Study: `services/` — all services use async patterns
- **Partial Failure**: `return_exceptions=True` for graceful degradation.
  - Study: `api/full_flow.py` — parallel execution with error handling

### Circuit Breaker
- **3-State Machine**: CLOSED → OPEN → HALF_OPEN.
  - Study: `core/llm_client.py` — `CircuitBreaker` class
- **Auto-Recovery**: Cooldown-based state transitions.
  - Study: `core/llm_client.py` — state machine logic

### Safety Pipeline
- **Multi-Layer Validation**: Fact-lock → keyword-lock → Tamil ratio → MCQ quality.
  - Study: `validators/validators.py` — all validation functions
- **Pre-Validation Normalization**: `@model_validator(mode='before')` cleans LLM output.
  - Study: `models/contracts.py` — `OutputSchema` normalization

### Prompt Builder Composition
- **Modular Prompts**: Separate prompt construction per endpoint.
  - Study: `utils/prompt_builder.py` — all prompt functions
- **Language Control**: Explicit bilingual instructions.
  - Study: `utils/prompt_builder.py` — Tamil/English prompt sections

### Concept Resolver Pipeline
- **Multi-Step Processing**: Normalize → detect → extract → resolve.
  - Study: `utils/concept_resolver.py` — the full pipeline
- **Script Detection**: Tamil Unicode vs Latin character analysis.
  - Study: `utils/concept_resolver.py` — script mix detection

### Error Handling Patterns
- **Graceful Degradation**: Partial failures don't crash the system.
  - Study: `services/` — fallback responses in all services
- **Structured Errors**: Consistent error response format.
  - Study: `api/` — error handling in routes

---

## Learning Project Ideas

### Project 1: Simple Concept Explainer
**Technologies:** FastAPI, Pydantic, basic LLM call
- Build a `/explain` endpoint that takes a concept and returns a bilingual explanation
- No safety system yet — just prompt → LLM → Pydantic validation
- Files to reference: `api/learn.py`, `models/request.py`, `models/contracts.py`

### Project 2: Adding Fact-Lock
**Technologies:** Regex, safety guards
- Add fact-lock to the concept explainer from Project 1
- Test with adversarial inputs that try to inject false numbers
- Files to reference: `core/safety_guard.py`, `validators/validators.py`

### Project 3: Circuit Breaker Implementation
**Technologies:** State machines, async error handling
- Implement a 3-state circuit breaker for any API client
- Test state transitions: CLOSED → OPEN → HALF_OPEN → CLOSED
- Files to reference: `core/llm_client.py`

### Project 4: TTL Cache
**Technologies:** cachetools, threading, hashing
- Build a TTL cache with LRU eviction and SHA-256 key generation
- Test TTL expiry, max size eviction, thread safety
- Files to reference: `core/cache.py`

### Project 5: React Interactive Text
**Technologies:** React, TypeScript, Tailwind CSS
- Build a component that shows tooltips on hover, one at a time
- Implement hover isolation with React state and timeout
- Files to reference: `src/components/InteractiveText.tsx`

### Project 6: Full-Stack Bilingual App
**Technologies:** FastAPI + Next.js + Gemini API
- Connect a FastAPI backend to a Next.js frontend
- Implement the full request lifecycle with proxy rewrites
- Files to reference: `orchestrator.py`, `next.config.ts`, `src/lib/api/`

### Project 7: Test Suite Builder
**Technologies:** Pytest, mocking, fixtures
- Write 20+ tests for a simple API endpoint
- Mock the LLM layer, test validators, test error handling
- Files to reference: `tests/test_contracts.py`, `tests/test_coach.py`

---

## Quick Reference

### Backend Commands
```bash
# Start server
python orchestrator.py

# Run tests
python -m pytest tests/ -v --tb=short

# Run specific test
python -m pytest tests/test_contracts.py -v

# Check health
curl http://localhost:8000/health
```

### Frontend Commands
```bash
# Install dependencies
cd vernacular-bridge-ui && npm install

# Start dev server
npm run dev

# Build for production
npm run build
```

### API Endpoints
```bash
# Learn
curl -X POST http://localhost:8000/learn -H "Content-Type: application/json" -d '{"query": "Photosynthesis"}'

# Coach
curl -X POST http://localhost:8000/coach -H "Content-Type: application/json" -d '{"question": "What is photosynthesis?", "student_answer": "Photosynthesis is how plants make food."}'

# Navigator
curl -X POST http://localhost:8000/navigator/explain -H "Content-Type: application/json" -d '{"query": "scholarship", "category": "entitlements"}'

# Full Flow
curl -X POST http://localhost:8000/full-flow -H "Content-Type: application/json" -d '{"query": "Photosynthesis"}'

# Health
curl http://localhost:8000/health
```

### Key Configuration (.env)
```bash
GOOGLE_API_KEY=your-gemini-api-key    # Required
PRIMARY_MODEL=gemini-2.5-flash        # Default
SECONDARY_MODEL=gemini-2.5-pro        # Fallback
RATE_LIMIT_RPM=20                     # Requests/min/IP
CACHE_TTL=600                         # Cache entry lifetime (seconds)
CB_THRESHOLD=3                        # Failures before circuit trips
CB_COOLDOWN=60                        # Seconds before recovery
ALLOWED_ORIGINS=localhost:3000        # CORS origins
```

---

## Progress Checklist

- [ ] Phase 1: Python foundations (type hints, async, Pydantic)
- [ ] Phase 2: Backend architecture (FastAPI, layered design, routers)
- [ ] Phase 3: LLM integration (Gemini API, prompt engineering, JSON extraction)
- [ ] Phase 4: Safety system (fact-lock, keyword-lock, Tamil ratio, circuit breaker)
- [ ] Phase 5: Frontend (Next.js, React, TypeScript, Tailwind, Zustand)
- [ ] Phase 6: Data & caching (JSON data, TTL cache, rate limiting)
- [ ] Phase 7: Testing (Pytest, mocking, 124-test suite)
- [ ] Phase 8: DevOps (Docker, environment config, health monitoring)
- [ ] Phase 9: Architecture patterns (layered design, parallel orchestration, safety pipeline)
- [ ] Build 1 mini-project from each phase
- [ ] Run the full test suite and understand every test
- [ ] Deploy locally (backend + frontend) and test end-to-end
- [ ] Read the Operations Center dashboard
- [ ] Review the 125 Q&A interview prep guide
- [ ] Contribute a new feature (endpoint, component, or test)

---

*Generated from codebase analysis — June 19, 2026.*
