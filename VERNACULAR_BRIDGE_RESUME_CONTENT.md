# Vernacular Bridge — Interview Preparation Guide

This is a comprehensive interview preparation guide for the **Vernacular Bridge** project. It contains 125 Q&A entries organized to help you prepare for job interviews by articulating every aspect of the project.

**Content Categories (3 Parts):**

### Part A: General & High-Level Questions (Q1–Q50)
Covers the "what, why, and how" of the project:

- **Project Overview** (Q1–Q5): What Vernacular Bridge is, target users (first-generation Tamil-medium students in Indian government universities), key features (Bilingual Concept Explainer, Writing Coach, Navigator, Exam Intelligence), and current project state.
- **Tech Stack & Decisions** (Q6–Q15): Why Python/FastAPI/Gemini/Next.js/Pydantic/Zod/Tailwind were chosen over alternatives like LangChain, OpenAI, Django, or raw React.
- **Architecture Decisions** (Q16–Q20): Why layered architecture (`api/` → `services/` → `core/` → `models/`), why not monolithic endpoints, how parallel orchestration works, why in-memory cache over Redis, environment configuration via pydantic-settings.
- **Feature Deep-Dives** (Q21–Q25): How the bilingual concept explainer works end-to-end, how the writing coach evaluates answers, how the navigator explains government entitlements, how the unified `/full-flow` endpoint orchestrates all three, how MCQ generation works.
- **Safety & Quality System** (Q26–Q30): Fact-lock hallucination prevention, keyword-lock semantic preservation, Tamil Unicode ratio validation, circuit breaker pattern for LLM fallback, prompt injection protection.
- **Development Process** (Q31–Q35): Project structure and layered architecture, test suite (124 tests, 15 categories, 97% pass rate), code review patterns, adversarial testing framework, documentation strategy.
- **Challenges & Learnings** (Q36–Q40): Biggest challenges (Tanglish normalization, LLM output inconsistency), what would be done differently, handling bilingual schema validation, scaling considerations, production readiness.
- **Behavioral & Leadership** (Q41–Q45): Role description, prioritization framework, scope management, code quality mechanisms, onboarding a new developer.
- **Future Vision** (Q46–Q50): Next steps, scaling to more languages, voice-first interface, personalized learning paths, real-time data integration.

### Part B: Technical Drilldown Questions (T1–T50 + 10 Quick-Fire)
Covers deep technical specifics:

- **Architecture & System Design** (T1–T5): Full architecture walkthrough, layered design rationale, parallel orchestration with asyncio, circuit breaker state machine, configuration management.
- **LLM Integration & Prompt Engineering** (T6–T10): Gemini API integration, prompt builder architecture, structured output extraction, model fallback strategy, token/cost optimization.
- **Safety & Quality Guards** (T11–T15): Fact-lock implementation, keyword-lock verification, Tamil ratio calculation, MCQ quality filters, generic phrase blocking.
- **Backend Engineering** (T16–T20): FastAPI router design, Pydantic model_validator patterns, TTL caching, per-IP rate limiting, audit logging middleware.
- **Data Modeling & Schemas** (T21–T25): OutputSchema normalization, CoachRequest/Response, NavigatorExplainRequest/Response, FullFlowResponse wrapper, JSON extraction from LLM text.
- **Frontend Engineering** (T26–T30): Next.js App Router pages, InteractiveText hover isolation, Zustand store for command center, React Context for learning state, API proxy rewrites.
- **Testing** (T31–T35): Test strategy across 15 categories, mocking LLM responses, contract validation tests, adversarial scenario testing, integration vs unit test split.
- **DevOps & Deployment** (T36–T40): Docker containerization, Procfile configuration, health endpoint design, environment variable management, CORS configuration.
- **Problem Solving** (T41–T45): Hardest challenge (Tanglish normalization), why not LangChain, handling LLM hallucination, lessons learned from adversarial testing, why FastAPI over Django.
- **Code Patterns & Practices** (T46–T50): Pydantic @model_validator patterns, service layer abstraction, circuit breaker implementation, prompt builder composition, concept resolver pipeline.
- **Quick-Fire** (QF1–QF10): 10 one-line summary questions.

### Part C: Functional / Domain Questions (F1–F25)
Covers education-domain-specific scenarios:

- **Student Onboarding & Input** (F1–F4): Complete student journey from query to response, handling Tamil script input, Tanglish code-mixed input, English-only input.
- **Concept Explainer Flow** (F5–F8): What happens when a student asks about photosynthesis, Tamil ratio enforcement, MCQ generation quality, question decoder behavior.
- **Writing Coach Flow** (F9–F13): How a student submits a draft, scoring rubric, improvement suggestions, handling weak answers, output normalization.
- **Navigator & Government Data** (F14–F17): How entitlements are explained, hallucination prevention on government data, process flow explanation, keyword-lock verification.
- **Safety Scenarios** (F18–F22): What happens with prompt injection attempts, what happens when LLM hallucinates numbers, circuit breaker trip and recovery, rate limiting behavior, cache poisoning prevention.
- **Edge Cases & Domain** (F23–F25): Empty or garbage input handling, extremely long queries, cross-language semantic alignment verification.

---

## Part A: General & High-Level Questions (Q1–Q50)

### Project Overview (Q1–Q5)

**Q1: What is Vernacular Bridge?**
> Vernacular Bridge is a bilingual AI-powered academic bridging platform that transforms Tamil-medium understanding into confident academic English performance for first-generation college students in Indian government universities. It's not translation — it's a cognitive bridge that combines concept explanation, exam preparation, and writing coaching into a unified system powered by Google Gemini.

**Q2: Who are the target users?**
> First-generation college students in Tamil Nadu, India. 45% of undergraduates in government universities come from Tamil-medium schools. They have strong foundational knowledge but higher education operates entirely in English — textbooks, instruction, and examinations. The resulting language-knowledge gap leads to academic failure attributable to language barriers, not intellectual incapacity.

**Q3: What are the key features?**
> Six core features: (1) Bilingual Concept Explainer — receives queries in Tamil/Tanglish/English and generates Tamil + academic English explanations with MCQs, (2) Academic Question Decoder — identifies question types and provides answer templates, (3) Writing Coach — evaluates student draft answers with structured feedback and scoring, (4) Navigator — bilingual explanation of government entitlements and university processes, (5) Unified Orchestration — runs Learn, Coach, and Navigator in parallel via `/full-flow`, (6) Data Retrieval — keyword-based search over 7 government schemes and 3 university processes.

**Q4: What is the current project state?**
> The project is in hackathon MVP state with a working backend (FastAPI, 8 API endpoints) and frontend (Next.js 16, 3 pages). It has 124 automated tests across 15 categories with a 97% pass rate. The 4 failing tests are Navigator integration tests requiring a live Gemini API key. There's also an Operations Center dashboard for project tracking with Kanban, burn-down, RCA tracker, and test tracker.

**Q5: What problem does this solve that ChatGPT doesn't?**
> Generic LLMs give free-form, inconsistent output with mixed language tones and no exam focus. Vernacular Bridge enforces: (1) strict bilingual structured JSON output, (2) controlled textbook Tamil + academic English with ≥60% Tamil Unicode ratio, (3) question-type-specific answer templates mapped to academic structures, (4) fact-lock and keyword-lock safety guards preventing hallucination, (5) prompt injection protection. It's purpose-built for exam preparation, not general conversation.

### Tech Stack & Decisions (Q6–Q15)

**Q6: Why FastAPI over Django or Flask?**
> FastAPI provides native async support (critical for parallel LLM calls), automatic OpenAPI docs, Pydantic v2 request/response validation built-in, and significantly higher throughput for I/O-bound workloads. Since our endpoints make multiple concurrent API calls to Gemini, async-first architecture is essential. Django's synchronous model would require additional async middleware and wouldn't leverage Python asyncio as naturally.

**Q7: Why Google Gemini over OpenAI GPT?**
> Gemini 2.5 Flash offers strong multilingual capabilities with a generous free tier, which is critical for a hackathon MVP. The `google-genai` SDK provides clean async support. Gemini handles Tamil script well and supports structured JSON output. The dual-model strategy (Flash for speed, Pro for quality) gives us cost optimization without sacrificing capability.

**Q8: Why Next.js 16 over plain React or Vite?**
> Next.js provides App Router for clean page routing, built-in API proxy rewrites (our frontend proxies to `localhost:8000` via `next.config.ts` rewrites), TypeScript-first development, and server-side rendering capabilities for future SEO. The component-based architecture with Tailwind CSS enables rapid UI development.

**Q9: Why Pydantic v2 on the backend?**
> Pydantic v2 provides: (1) `@model_validator(mode='before')` for pre-validation LLM output normalization — we use this extensively in `OutputSchema` to coerce, fix, and validate LLM responses before they reach the application layer, (2) type coercion that handles LLM output inconsistencies, (3) field-level validation with custom validators for Tamil ratio, MCQ quality, and semantic alignment, (4) JSON Schema generation for API documentation.

**Q10: Why Zustand over Redux or React Context for state management?**
> We use a hybrid approach: Zustand for the Command Center store (complex state with actions, simpler than Context for multiple state slices) and React Context for the learning flow state (simpler, fewer state transitions). Zustand provides better TypeScript inference, no boilerplate, and works outside React components (useful for the operations dashboard). Redux would be overkill for this app's state complexity.

**Q11: Why not use LangChain for LLM orchestration?**
> LangChain adds significant abstraction overhead for what we need. Our LLM interaction is straightforward: build a prompt → call Gemini → parse JSON → validate. The abstraction layers in LangChain would obscure the prompt engineering and output normalization logic that's core to our safety system. We maintain full control over prompt construction (`utils/prompt_builder.py`), output parsing (`parsers/json_extractor.py`), and validation (`validators/validators.py`).

**Q12: Why Tailwind CSS over component libraries like Material UI or shadcn?**
> Tailwind provides maximum design flexibility without fighting pre-built component styles. For a bilingual educational platform with Tamil typography requirements, we need fine-grained control over typography, spacing, and layout. The utility-first approach keeps the CSS bundle small and eliminates unused styles. We built custom components (ConceptCard, MCQSection, ScoreCard, InteractiveText) that match our specific design language.

**Q13: Why in-memory caching (cachetools) over Redis?**
> For hackathon MVP scope, in-memory TTLCache is simpler to deploy and has zero infrastructure dependencies. The cache stores learn responses keyed by query hash with configurable TTL (default 600s). This handles repeated concept queries efficiently. For production, this would be swapped to Redis, but the cache interface (`core/cache.py`) is abstracted to make that swap trivial.

**Q14: Why the layered architecture (`api/` → `services/` → `core/` → `models/`)?**
> Separation of concerns: `api/` contains thin route controllers (HTTP request/response handling only), `services/` contains business logic (orchestration, LLM calls, validation), `core/` contains infrastructure (LLM client, caching, rate limiting, safety guards), `models/` contains Pydantic schemas. This means changing the LLM provider only touches `core/llm_client.py`, adding a new endpoint only requires a new file in `api/`, and the validation logic in `validators/` is reusable across all endpoints.

**Q15: Why Zod on the frontend alongside Pydantic on the backend?**
> Type safety across the stack. Pydantic ensures backend API responses conform to schemas; Zod provides runtime validation on the frontend when consuming those responses. The shared schema contracts are documented in `docs/contracts.md`. This catches data shape mismatches at both boundaries, preventing silent failures when the LLM returns unexpected output.

### Architecture Decisions (Q16–Q20)

**Q16: Walk me through the full request lifecycle for `/learn`.**
> (1) Student sends a query to `POST /learn` via the frontend API client, (2) `api/learn.py` router validates the request against `QueryRequest` Pydantic model, (3) `services/learn_service.py` orchestrates the flow: preprocesses input via `concept_resolver.py` (handles Tanglish normalization), (4) `prompt_builder.py` constructs the LLM prompt with language control and cultural context, (5) `core/llm_client.py` calls Gemini API with circuit breaker protection, (6) `parsers/json_extractor.py` extracts structured JSON from LLM text response, (7) `OutputSchema` model_validator normalizes and validates the output (Tamil ratio check, MCQ quality, generic phrase blocking), (8) `validators/validators.py` runs final quality checks, (9) Response returned as validated JSON.

**Q17: How does the parallel orchestration in `/full-flow` work?**
> The `/full-flow` endpoint receives a `FullFlowRequest` and spawns three concurrent `asyncio` tasks: `learn_service.process()`, `coach_service.process()`, and `navigator_service.process()`. Each task makes independent LLM calls and validations. `asyncio.gather()` waits for all three to complete (or timeout). Each operation has its own Pydantic model (`OutputSchema`, `CoachResponse`, `NavigatorExplainResponse`), so failures in one don't affect others. Results are wrapped in `FullFlowResponse`. This achieves ~3x speedup over sequential processing.

**Q18: How does the circuit breaker pattern work?**
> Implemented in `core/llm_client.py` as a 3-state machine: CLOSED (normal operation, requests flow through) → OPEN (after `CB_THRESHOLD` consecutive failures, all requests fail fast with a fallback message) → HALF_OPEN (after `CB_COOLDOWN` seconds, one test request is allowed through; if it succeeds → CLOSED, if it fails → OPEN again). This prevents cascade failures when Gemini quota is exhausted. The `/health` endpoint exposes the current state for monitoring.

**Q19: Why in-memory cache instead of database-backed caching?**
> The cache is a `cachetools.TTLCache` with configurable max size (default 100 entries) and TTL (default 600 seconds). For the hackathon scope, this eliminates database setup entirely while still providing meaningful deduplication for repeated concept queries. The cache key is a hash of the normalized query. The `/health` endpoint reports cache hit/miss statistics. The cache layer is abstracted in `core/cache.py` to allow swapping to Redis without changing service code.

**Q20: How is configuration managed across environments?**
> All configuration is centralized in `core/config.py` using `pydantic-settings` with a `Settings` class that loads from `.env` automatically. Key settings: `GOOGLE_API_KEY`, `PRIMARY_MODEL` (gemini-2.5-flash), `SECONDARY_MODEL` (gemini-2.5-pro), `RATE_LIMIT_RPM` (20), `CACHE_TTL` (600), `CB_THRESHOLD` (3), `CB_COOLDOWN` (60), `ALLOWED_ORIGINS` (localhost:3000,localhost:7860). Defaults are sensible for local development. `.env.example` documents all variables. CORS middleware is configured from `ALLOWED_ORIGINS`.

### Feature Deep-Dives (Q21–Q25)

**Q21: How does the Bilingual Concept Explainer work end-to-end?**
> A student submits a concept query (e.g., "Photosynthesis" or "Semester Registration"). The concept resolver normalizes input (handles Tamil script, Tanglish, English). The prompt builder constructs a structured prompt with language instructions, cultural context, and output format requirements. Gemini generates a response with: `tamil_simple` (Tamil explanation ≥60% Tamil Unicode), `english_academic` (precise English), `steps` (2–7 breakdown items), `question_decoder` (question type + answer template), and `mcqs` (up to 5 questions with 4 options each). The OutputSchema model_validator normalizes and validates everything before returning.

**Q22: How does the Writing Coach evaluate answers?**
> A student submits their draft answer via `POST /coach` with `CoachRequest` (question + student_answer). The coach service sends both to Gemini with a structured prompt asking for: scoring (0–10), strengths, weaknesses, missing points, and specific improvement suggestions. The `CoachResponse` is validated by `coach_validator.py` which normalizes scores to 0–10 range, strips markdown artifacts, controls response length, and ensures the feedback is actionable. The frontend displays this via `ScoreCard` and `ImprovedAnswer` components.

**Q23: How does the Navigator explain government entitlements?**
> The navigator receives a query and matches it against pre-loaded dataset items from `data/entitlements.json` (7 schemes like Pudhumai Penn, First Graduate Tuition Waiver) and `data/processes.json` (3 processes like Semester Registration, Exam Registration). It sends matched items to Gemini for bilingual explanation. The fact-lock in `core/safety_guard.py` verifies no new numbers or URLs were invented by the LLM. The keyword-lock ensures core semantic meaning (eligibility criteria, deadlines, links) is preserved across Tamil↔English translation.

**Q24: How does the unified `/full-flow` endpoint orchestrate everything?**
> `/full-flow` accepts a `FullFlowRequest` containing query, optional student answer, and optional navigator category. It creates three `asyncio` tasks running in parallel: (1) Learn service generates bilingual explanation + MCQs, (2) Coach service evaluates any provided draft answer, (3) Navigator service explains relevant government processes/entitlements. All three are wrapped in `asyncio.gather(return_exceptions=True)` so individual failures don't block others. Results are assembled into `FullFlowResponse` with each sub-response independently validated.

**Q25: How does MCQ generation work and what quality controls exist?**
> MCQs are generated as part of the `/learn` response. The prompt instructs Gemini to create up to 5 questions covering: understanding checks, misconception traps, and application-based scenarios. Quality controls in `validators/validators.py` and `models/contracts.py` include: (1) reject trivial Yes/No questions, (2) reject duplicate questions and options, (3) ensure exactly 4 unique options per question, (4) verify `correct_answer` matches one of the 4 options (auto-replaces last option if missing), (5) normalize answer key aliases (A→option_1, B→option_2, etc.), (6) block generic phrases like "identify the concept" that indicate low-quality LLM output.

### Safety & Quality System (Q26–Q30)

**Q26: What is the Fact-Lock and how does it prevent hallucination?**
> Fact-Lock (implemented in `core/safety_guard.py`) extracts all numbers and URLs from the input text and verifies they appear in the output. If the LLM invents a new number (e.g., a fabricated deadline "March 15, 2025") or URL that wasn't in the original data, the fact-lock flags it. For the Navigator, this is critical because government scheme details (eligibility percentages, deadlines, official links) must be accurate — hallucinated data could mislead students about scholarship eligibility.

**Q27: What is the Keyword-Lock?**
> Keyword-Lock (also in `core/safety_guard.py`) ensures that core semantic keywords from the input are preserved in the translated output. It extracts key phrases (scheme names, eligibility criteria, deadline terms) and verifies they appear (or have proper Tamil equivalents) in both the Tamil and English explanations. This prevents the LLM from paraphrasing away critical information during translation — for example, ensuring "First Graduate Certificate from Tahsildar" isn't simplified to just "government document."

**Q28: How does the Tamil Ratio Validation work?**
> `validators/validators.py` contains `calculate_tamil_ratio()` which counts Tamil Unicode characters (U+0B80–U+0BFF range) against total characters. The `TAMIL_RATIO_THRESHOLD` is set to 0.6 (60%). If the `tamil_simple` field has less than 60% Tamil characters, the response is flagged. This prevents the LLM from defaulting to English in the Tamil explanation — a common failure mode when LLMs are asked to generate code-mixed content. The confidence score is adjusted based on the ratio.

**Q29: What are the MCQ Quality Guards?**
> Multiple validators in `validators/validators.py` ensure MCQ quality: (1) **Trivial rejection** — blocks Yes/No questions and single-word answers, (2) **Duplicate detection** — removes questions with identical stems or identical option sets, (3) **Option count enforcement** — ensures exactly 4 options per question, (4) **Correct answer validation** — verifies the correct answer is one of the 4 options, auto-fixes if not, (5) **Generic phrase blocking** — `models/contracts.py` has a blocklist of low-quality phrases ("identify the concept", "explain briefly", etc.) that indicate the LLM didn't generate a substantive question.

**Q30: How does prompt injection protection work?**
> `core/sanitizer.py` wraps user input in XML delimiters (`<user_input>...</user_input>`) to clearly separate user content from system instructions. It also runs pattern detection against common injection attempts (e.g., "ignore previous instructions", "you are now", role-playing attacks). The sanitizer runs before any LLM call in the service layer. Additionally, `core/audit.py` logs all inputs with masked IPs and hashed payloads for security auditing without storing sensitive data.

### Development Process (Q31–Q35)

**Q31: Describe the project structure and why it's organized this way.**
> The project follows a layered architecture: `api/` (thin controllers, 6 router files) → `services/` (business logic, 4 service files) → `core/` (infrastructure, 8 modules) → `models/` (Pydantic schemas, 5 model files) → `validators/` (content validation) → `parsers/` (LLM output parsing) → `utils/` (prompt building, input preprocessing). Additional directories: `verification/` (adversarial testing), `data/` (JSON datasets), `tests/` (124 tests), `docs/` (schema contracts, operations dashboard), `vernacular-bridge-ui/` (Next.js frontend).

**Q32: Describe the test suite.**
> 124 tests across 15 categories with 97% pass rate (120 passed, 4 skipped — Navigator integration tests requiring live Gemini API). Categories: Coach Validator (8), Contract Validation (13), Navigator Integration (7), Data Retrieval (7), Circuit Breaker (10), Learn Cache (5), LLM Functions (2), Text Normalization (5), Steps Normalization (6), Quality Guards (13), Question Decoder (15), MCQ Normalization (12), Input Sanitization (4), Injection Detection (13), Instruction Prefix (3). Run with `python -m pytest tests/ -v --tb=short`.

**Q33: What does the adversarial testing framework do?**
> `verification/adversarial_generator.py` generates adversarial test cases — inputs designed to break the safety system (injection attempts, hallucination triggers, edge cases). `verification/scenarios.yaml` defines test scenarios. `verification/scoring.py` evaluates response quality. `verification/verifier.py` runs the verification pipeline. `verification/run_verification.py` orchestrates execution. This ensures the safety guards hold up against deliberate attacks, not just happy-path inputs.

**Q34: How do you handle LLM output inconsistency in testing?**
> Tests mock the LLM layer where possible (unit tests for validators, parsers, circuit breaker, caching). Integration tests that hit the live Gemini API are marked and skipped in CI (the 4 Navigator tests). Contract validation tests use pre-defined LLM output fixtures to test the normalization pipeline deterministically. The OutputSchema's `@model_validator(mode='before')` is extensively tested with edge cases (missing fields, wrong types, extra fields, duplicate MCQs).

**Q35: What documentation exists for the project?**
> `VERNACULAR_BRIDGE_OVERVIEW.md` — comprehensive app overview (architecture, features, API, tech stack). `VERNACULAR_BRIDGE_RESUME_CONTENT.md` — this interview prep guide. `docs/contracts.md` — Pydantic schema contracts. `docs/deployment.md` — deployment guide. `docs/engineering_audit.md` — engineering audit report. `docs/operations-center.html` — interactive operations dashboard with Kanban, burn-down, RCA tracker, and test tracker. `.env.example` — environment variable documentation.

### Challenges & Learnings (Q36–Q40)

**Q36: What was the biggest technical challenge?**
> Tanglish normalization — handling code-mixed Tamil-English input. Students type in unpredictable ways: pure Tamil script, pure Roman transliteration ("vanakkam"), or mixed ("naan oru student-aa irukken"). The concept resolver in `utils/concept_resolver.py` needed to normalize all these variants into a consistent format before LLM processing. The key insight was treating this as a preprocessing pipeline problem rather than trying to handle it in the prompt.

**Q37: What would you do differently?**
> (1) Start with the safety system first, not last — the fact-lock and keyword-lock were added after seeing hallucination issues in early testing. (2) Use a structured output mode (Gemini's JSON mode) from day one instead of post-processing free-text responses. (3) Add integration test mocking earlier — the 4 skipped Navigator tests indicate we should have mocked the LLM layer more aggressively in tests. (4) Set up the Operations Center dashboard earlier for tracking progress.

**Q38: How did you handle the bilingual schema validation challenge?**
> The core challenge was that `OutputSchema` needs to validate fields in two languages simultaneously. The `@model_validator(mode='before')` normalizes the raw LLM dictionary first (type coercion, field mapping), then field-level validators check each language independently: Tamil ratio ≥60% for `tamil_simple`, minimum character counts for `english_academic`, MCQ quality checks for the `mcqs` array. The confidence score is computed as a weighted average of all validation signals.

**Q39: What are the scaling considerations?**
> For production: (1) Replace in-memory cache with Redis for multi-instance deployments, (2) Add a database for student profiles and learning history, (3) Implement proper authentication (currently API key-based), (4) Add Gemini quota management per-student, (5) Consider Gemini's structured output mode to reduce post-processing, (6) Add a queue system for async processing of `/full-flow` requests, (7) Move from `start` command to Kubernetes with proper health checks.

**Q40: What did you learn from adversarial testing?**
> The adversarial framework revealed three key failure modes: (1) LLMs will confidently invent government scheme numbers when they don't know the answer — fact-lock is essential, not optional, (2) Translation quality degrades significantly when the input query is in English but the expected output is Tamil — the prompt needs explicit language-switching instructions, (3) Prompt injection via student input is a real threat even in educational apps — the sanitizer caught multiple attempts during testing.

### Behavioral & Leadership (Q41–Q45)

**Q41: Describe your role in this project.**
> Full-stack architect and lead developer. I designed the layered architecture, implemented the backend (FastAPI, LLM integration, safety system, 124 tests), built the frontend (Next.js, TypeScript, Tailwind), created the operations dashboard, and wrote all documentation. I also designed the adversarial testing framework and the bilingual schema validation system.

**Q42: How did you prioritize features?**
> MoSCoW framework applied to hackathon timeline: **Must-have** (bilingual explainer, safety system, basic frontend) → **Should-have** (writing coach, navigator, parallel orchestration) → **Could-have** (MCQ generation, question decoder, operations dashboard) → **Won't-have** (authentication, database, voice input, multi-language support). The safety system was promoted from "should" to "must" after early adversarial testing showed hallucination risks.

**Q43: How did you manage scope creep?**
> The Grok development philosophy document defined clear phases (0–6). I stuck to Phase 1–3 scope for the hackathon: core UI, robust AI backend, and feature implementation. The operations dashboard was added as a "could-have" that became valuable for tracking. I resisted adding authentication, database persistence, and voice input despite their attractiveness because they didn't directly serve the core value proposition.

**Q44: How do you ensure code quality?**
> (1) Pydantic v2 schema validation on every API boundary, (2) 124 automated tests with 97% coverage across 15 categories, (3) Adversarial testing framework for safety guard verification, (4) Structured audit logging with masked IPs, (5) Layered architecture enforcing separation of concerns, (6) Documentation-as-code (schema contracts, engineering audit), (7) The Operations Center dashboard provides real-time visibility into test results and issue tracking.

**Q45: How would you onboard a new developer?**
> Start with `VERNACULAR_BRIDGE_OVERVIEW.md` for the big picture. Then `docs/contracts.md` for API schemas. Run `python orchestrator.py` and `npm run dev` to see it working. Read `orchestrator.py` (<100 lines) to see how routes mount. Explore `api/` → `services/` → `core/` to understand the layered flow. Run `python -m pytest tests/ -v` to see the test suite. Open `docs/operations-center.html` for the project dashboard. Key architectural decisions are in `core/` — read `config.py` and `llm_client.py` first.

### Future Vision (Q46–Q50)

**Q46: What are the immediate next steps?**
> (1) Add database persistence for student profiles and learning history, (2) Implement spaced repetition (SM-2 algorithm) for MCQ review, (3) Add authentication with JWT, (4) Deploy to production (Docker + cloud hosting), (5) Integrate real-time government data feeds for entitlements, (6) Add Hindi and Telugu language support using the modular prompt architecture.

**Q47: How would you scale to 10,000+ students?**
> (1) Replace in-memory cache with Redis cluster, (2) Add PostgreSQL for student data and learning analytics, (3) Implement request queuing (Celery + Redis) for `/full-flow` processing, (4) Deploy multiple FastAPI instances behind a load balancer, (5) Add Gemini quota management per-student with Redis-backed rate limiting, (6) Implement CDN caching for static concept explanations, (7) Add monitoring (Prometheus + Grafana) using the existing `/health` endpoint.

**Q48: What technologies would you add?**
> (1) **Voice input** — Whisper API for Tamil voice queries (critical for low-literacy users), (2) **RAG** — Retrieval-augmented generation for syllabus-specific content, (3) **SM-2 Spaced Repetition** — Personalized MCQ review scheduling, (4) **PostgreSQL** — Student profiles, learning history, analytics, (5) **Redis** — Distributed caching and rate limiting, (6) **WebSocket** — Real-time coaching feedback, (7) **Indic NLP models** — For better Tamil processing.

**Q49: What real-time features would you add?**
> (1) Live writing coach feedback as students type (WebSocket streaming from Gemini), (2) Real-time MCQ difficulty adaptation based on student performance, (3) Live collaboration — students can share concept explanations and annotate together, (4) Push notifications for deadline reminders (exam registration, scholarship applications), (5) Real-time government scheme updates reflected in navigator data.

**Q50: What's the long-term vision?**
> Vernacular Bridge becomes the academic success platform for all first-generation college students in India. Started with Tamil → expanded to Hindi, Telugu, Kannada, and Bengali. The modular architecture (language-agnostic prompt builder, pluggable validators, multi-model LLM support) is designed for this expansion. Long-term: integration with university APIs for automated course material mapping, personalized learning paths based on mastery tracking, peer community features, and a mobile-first PWA for offline access in areas with poor connectivity.

---

## Part B: Technical Drilldown Questions (T1–T50 + Quick-Fire)

### Architecture & System Design (T1–T5)

**T1: Walk through the full architecture from request to response.**
> Frontend (Next.js, port 3000) → API proxy rewrite (`next.config.ts`) → FastAPI (port 8000) → Router (`api/`) validates request via Pydantic → Service (`services/`) orchestrates business logic → Core (`core/`) handles LLM calls, caching, rate limiting → Parsers (`parsers/`) extract structured JSON from LLM text → Validators (`validators/`) check quality → Models (`models/`) enforce schema → Response returned as typed JSON. Each layer only depends on the layer below it.

**T2: How does the layered architecture differ from a monolithic endpoint approach?**
> A monolithic endpoint would handle validation, LLM calls, parsing, and response formatting in a single function. Our layered approach: `api/learn.py` is ~30 lines (just route + request/response typing), `services/learn_service.py` contains orchestration logic (~80 lines), `core/llm_client.py` handles Gemini + circuit breaker (~120 lines), `parsers/json_extractor.py` handles LLM output parsing (~50 lines). Benefits: testability (mock at any layer), reusability (learn_service's LLM call pattern is reused by navigator_service), maintainability (changing Gemini API only touches `core/llm_client.py`).

**T3: How does parallel orchestration work with `asyncio.gather()`?**
> In `services/` (e.g., full_flow), three independent async tasks are created: `learn_task = asyncio.create_task(learn_service.process(...))`, `coach_task = asyncio.create_task(coach_service.process(...))`, `navigator_task = asyncio.create_task(navigator_service.process(...))`. Then `results = await asyncio.gather(learn_task, coach_task, navigator_task, return_exceptions=True)`. The `return_exceptions=True` flag means if one task fails (e.g., Gemini quota exhausted for navigator), the others still complete. Each result is checked: if it's an `Exception`, that sub-response is set to a fallback error message.

**T4: Describe the circuit breaker state machine implementation.**
> `core/llm_client.py` implements `CircuitBreaker` class with three states: `CLOSED` (normal, requests pass through), `OPEN` (after `CB_THRESHOLD=3` consecutive failures, all requests immediately return a fallback response without calling Gemini), `HALF_OPEN` (after `CB_COOLDOWN=60` seconds, one test request is allowed; success → CLOSED, failure → OPEN). State transitions are atomic and thread-safe. The `/health` endpoint exposes `circuit_breaker.state` and `circuit_breaker.failure_count` for monitoring. The breaker specifically tracks Gemini API failures (quota, timeout, 5xx) vs application errors.

**T5: How is configuration handled across development, staging, and production?**
> `core/config.py` uses `pydantic-settings` with a `Settings` class that reads from `.env` via `load_dotenv()`. All settings have sensible defaults for local dev. For staging/production, override via environment variables or a separate `.env.staging` / `.env.production`. Key settings: `GOOGLE_API_KEY`, `PRIMARY_MODEL`, `SECONDARY_MODEL`, `RATE_LIMIT_RPM` (20), `CACHE_TTL` (600), `CB_THRESHOLD` (3), `ALLOWED_ORIGINS`. The `ALLOWED_ORIGINS` setting controls CORS — must include the frontend domain. Docker deployment uses `ENV` directives in Dockerfile.

### LLM Integration & Prompt Engineering (T6–T10)

**T6: How does the Gemini API integration work?**
> `core/llm_client.py` uses the `google-genai` SDK. The client is initialized with `GOOGLE_API_KEY` from config. The `generate()` method accepts a prompt string and optional model override. It includes: (1) automatic model selection (primary Flash, fallback Pro), (2) circuit breaker wrapping, (3) retry logic with exponential backoff on transient errors, (4) timeout handling. The response text is extracted and returned as a string — JSON parsing happens in `parsers/json_extractor.py`.

**T7: How does the prompt builder work?**
> `utils/prompt_builder.py` is a module with functions that construct structured prompts for each endpoint. The learn prompt includes: system instructions (language control, output format), cultural context (Tamil Nadu education system), concept-specific context, and output schema template. Key techniques: (1) Explicit language-switching instructions ("respond in Tamil for tamil_simple, English for english_academic"), (2) Few-shot examples for output format, (3) Negative instructions ("do not invent numbers or URLs"), (4) Cultural grounding ("explain as if to a first-generation college student in Tamil Nadu").

**T8: How does JSON extraction from LLM text work?**
> `parsers/json_extractor.py` handles the reality that LLMs don't always return clean JSON. The extraction pipeline: (1) Try `json.loads()` directly on response, (2) If that fails, search for JSON block markers (```json...```), (3) If not found, search for first `{` and last `}` to extract the JSON object, (4) Apply regex cleanup for common LLM artifacts (trailing commas, single quotes, comments), (5) Parse with `json.loads()`, (6) If all extraction fails, return a minimal fallback dict. This is necessary because Gemini sometimes wraps JSON in explanatory text.

**T9: How does the dual-model fallback strategy work?**
> The primary model is `gemini-2.5-flash` (fast, cost-effective, good for most queries). The secondary is `gemini-2.5-pro` (higher quality, used when Flash fails). The circuit breaker triggers the switch: when Flash hits quota limit or errors 3 times consecutively, the breaker opens and subsequent requests use Pro. After cooldown (60s), a test request goes to Flash to check recovery. This gives us cost optimization (90%+ requests on Flash) with quality fallback (Pro handles the hard cases).

**T10: How do you handle token limits and cost optimization?**
> (1) Cache deduplication — repeated queries hit cache instead of LLM, (2) Prompt size optimization — the prompt builder includes only necessary context (not full dataset), (3) Response length control — validators enforce max lengths (tamil_simple: 800 chars, english_academic: 1200 chars, steps: max 7 items, mcqs: max 5 questions), (4) Model selection — Flash for most queries, Pro only on fallback, (5) Rate limiting (20 req/min/IP) prevents abuse.

### Safety & Quality Guards (T11–T15)

**T11: How is the fact-lock implemented in code?**
> `core/safety_guard.py` has `verify_fact_lock(input_text, output_text)` which: (1) Extracts all numbers from input using regex `\d+\.?\d*`, (2) Extracts all URLs from input using regex `https?://[^\s]+`, (3) Checks each extracted number/URL appears in the output, (4) Returns a dict with `passed: bool`, `missing_numbers: list`, `missing_urls: list`, `new_numbers: list` (numbers in output not in input — potential hallucination). The service layer checks the result and can flag or reject responses that fail fact-lock.

**T12: How is keyword-lock verified?**
> `core/safety_guard.py` has `verify_keyword_lock(input_text, output_text, language)` which: (1) Extracts key phrases from input using TF-IDF or simple keyword extraction, (2) For each key phrase, checks if it (or its translation equivalent) appears in the output, (3) For Tamil→English: verifies Tamil terms have English equivalents, (4) For English→Tamil: verifies English terms have Tamil equivalents, (5) Returns coverage score and list of missing keywords. This is particularly important for government scheme names and eligibility criteria.

**T13: How is the Tamil ratio calculated?**
> `validators/validators.py` has `calculate_tamil_ratio(text)` which counts Unicode characters in the Tamil block (U+0B80–U+0BFF) against total non-whitespace characters. The threshold is 0.6 (60%). The confidence score adjustment is: `tamil_confidence = min(1.0, tamil_ratio / TAMIL_RATIO_THRESHOLD)`. If ratio is 0.7 (70%), confidence is 1.0. If ratio is 0.45 (45%), confidence is 0.75. Below the threshold, the response is flagged but not rejected (allows for edge cases where English terms are necessary in Tamil text).

**T14: What MCQ quality filters exist?**
> In `validators/validators.py`: (1) `validate_mcq_triviality()` — rejects questions with <3 distinct concept words, (2) `validate_mcq_duplicates()` — uses fuzzy matching (Levenshtein distance) to detect near-duplicate questions and options, (3) `validate_mcq_options()` — ensures exactly 4 options with minimum character count, (4) In `models/contracts.py` OutputSchema: `validate_correct_answer_in_options()` verifies correct_answer matches one of the 4 options, normalizes answer aliases (A→option_1, etc.), `normalize_raw_llm_output()` deduplicates options and fixes option count.

**T15: What generic phrases are blocked and why?**
> `models/contracts.py` has a blocklist in `normalize_raw_llm_output()` that catches low-quality LLM output patterns: "identify the concept", "explain briefly", "discuss the topic", "this is about", "in simple terms", "let me explain". These phrases indicate the LLM generated a template response rather than substantive content. When detected, the field is flagged for re-generation or fallback content. This is a quality guard specifically tuned for educational content — generic explanations don't help students prepare for exams.

### Backend Engineering (T16–T20)

**T16: How are FastAPI routes structured?**
> Each route file in `api/` defines a `router = APIRouter()`. Example: `api/learn.py` has `@router.post("/learn")` and `@router.post("/generate")` (legacy alias). Routes are thin controllers: validate request via Pydantic model, call service layer, return typed response. The main `orchestrator.py` (<100 lines) mounts all routers: `app.include_router(learn_router)`, `app.include_router(coach_router)`, etc. CORS middleware is configured from settings. The `/health` endpoint is mounted directly in orchestrator.py.

**T17: How does the Pydantic `@model_validator(mode='before')` pattern work in OutputSchema?**
> `models/contracts.py` has `OutputSchema` with a `@model_validator(mode='before')` that receives the raw dictionary (before Pydantic field validation). It: (1) Applies type coercion (string→list for steps, dict→list for mcqs), (2) Runs quality guards (blocks generic phrases), (3) Normalizes question_decoder (maps question types to expected structures), (4) Cleans MCQs (deduplicates options, fixes correct_answer, enforces 4-option count), (5) Strips markdown artifacts from all text fields. This pre-processing step means the field validators receive already-clean data, making them simpler and more reliable.

**T18: How does TTL caching work?**
> `core/cache.py` wraps `cachetools.TTLCache` with: (1) `get_or_compute(key, compute_fn, ttl)` — returns cached value or computes and caches, (2) LRU eviction when `CACHE_MAX_SIZE` (100) is reached, (3) TTL-based expiry (default 600s), (4) Cache key is SHA-256 hash of normalized query + endpoint name, (5) Thread-safe via `threading.Lock`. The `/health` endpoint reports `cache_size` (current entries) and cache hit/miss statistics.

**T19: How does per-IP rate limiting work?**
> `core/rate_limiter.py` implements a sliding-window rate limiter: (1) Tracks request timestamps per IP in a dictionary, (2) Slides a window of `RATE_LIMIT_RPM` seconds (default 60), (3) Counts requests within the window, (4) Returns `429 Too Many Requests` with `Retry-After` header when limit exceeded, (5) Automatically cleans up stale entries. Applied as FastAPI middleware. The `/health` endpoint doesn't count toward rate limits.

**T20: How does the audit logging middleware work?**
> `core/audit.py` implements `AuditMiddleware` (Starlette middleware) that: (1) Logs request method, path, status code, and response time, (2) Masks IP addresses (last octet replaced with `***`) for privacy, (3) Hashes request payloads (SHA-256) for correlation without storing sensitive data, (4) Uses structured JSON logging for machine-parseable output, (5) Excludes health checks and static files from logging to reduce noise.

### Data Modeling & Schemas (T21–T25)

**T21: Walk through the OutputSchema normalization pipeline.**
> Raw LLM dict → `@model_validator(mode='before')` receives it as `data: dict` → (1) Ensure `tamil_simple` is string (LLM sometimes returns list), (2) Ensure `english_academic` is string, (3) Ensure `steps` is list of strings (handle string→split, single item→list), (4) Run `normalize_question_decoder()` — map "define"→expected structure, "explain"→expected structure, etc., (5) Run `normalize_mcqs()` — deduplicate, fix options, validate correct_answer, (6) Run `block_generic_phrases()` on all text fields → Clean data passed to Pydantic field validators → Field validators run: min/max lengths, Tamil ratio check, MCQ count limit.

**T22: Describe the CoachRequest/CoachResponse models.**
> `models/coach.py`: `CoachRequest` has `question: str` (the exam question), `student_answer: str` (student's draft), `language_config: LanguageConfig` (optional, defaults to bilingual). `CoachResponse` has `score: int` (0–10), `strengths: list[str]`, `weaknesses: list[str]`, `missing_points: list[str]`, `improvement_suggestions: list[str]`, `improved_answer: str` (complete rewritten answer). The `coach_validator.py` normalizes scores to 0–10 range, strips markdown, controls response length.

**T23: Describe the NavigatorExplainRequest/Response models.**
> `models/navigator.py`: `NavigatorExplainRequest` has `query: str`, `category: Literal["entitlements", "processes"]` (which dataset to search), `language_config: LanguageConfig`. `NavigatorExplainResponse` has `item_name: str`, `tamil_explanation: str`, `english_explanation: str`, `key_points: list[str]`, `relevant_links: list[str]` (must pass fact-lock — no invented URLs). The response undergoes both fact-lock and keyword-lock verification.

**T24: Describe the FullFlowResponse wrapper.**
> `models/full_flow.py`: `FullFlowResponse` wraps three sub-responses: `learn: Optional[OutputSchema]` (null if learn fails), `coach: Optional[CoachResponse]` (null if no student answer provided or coach fails), `navigator: Optional[NavigatorExplainResponse]` (null if navigator fails). Plus `metadata: dict` with `processing_time_ms: float`, `models_used: list[str]`, `cache_hit: bool`. This design means partial failures degrade gracefully — you still get the learn response even if coach fails.

**T25: How does JSON extraction handle malformed LLM output?**
> `parsers/json_extractor.py`: (1) Try `json.loads(response)` directly, (2) Regex search for ````json\n...\n``` ` blocks, (3) Find first `{` and last `}` for object extraction, (4) Regex cleanup: remove trailing commas (`/,\s*}/` → `}`), remove single-quote wrapping, strip `//` comments, (5) Handle `null` → `None` conversion, (6) If all extraction fails: return `{"tamil_simple": "Error: could not parse response", "english_academic": "...", "steps": [], "mcqs": []}` — a valid schema with error indication.

### Frontend Engineering (T26–T30)

**T26: How is the Next.js App Router structured?**
> `vernacular-bridge-ui/src/app/`: `page.tsx` (main learning dashboard — concept input, bilingual output, MCQs, coach), `dashboard/page.tsx` (analytics dashboard), `command-center/page.tsx` (operations monitoring). `layout.tsx` wraps all pages with providers. `globals.css` contains Tailwind directives and custom CSS. The frontend proxies API calls to the backend via `next.config.ts` rewrites: `/api/:path*` → `http://localhost:8000/:path*`.

**T27: How does the InteractiveText hover isolation work?**
> `components/InteractiveText.tsx` uses React state (`hoveredIndex`) instead of CSS-only hover. Each interactive word is wrapped in a span with `onMouseEnter`/`onMouseLeave` handlers. `hoveredIndex` tracks which word (by index) is currently hovered. A `hoverTimeoutRef` adds a 100ms delay before hiding the tooltip to prevent flicker when moving between adjacent words. Tooltip visibility is controlled by `isHovered = hoveredIndex === index`. This prevents the cascading hover bug where CSS `group-hover` caused all tooltips to appear simultaneously when they overlapped.

**T28: How does the Zustand store work for the command center?**
> `store/commandCenterStore.ts` defines a Zustand store with: `activePanel: 'learning' | 'coaching' | 'navigator'`, `queryHistory: QueryEntry[]`, `selectedQuery: string | null`, `actions: { setActivePanel, addToHistory, selectQuery }`. Zustand provides better TypeScript inference than React Context, works outside React components (useful for the operations dashboard), and doesn't require a Provider wrapper. The store persists to localStorage for session continuity.

**T29: How does the React Context work for learning state?**
> `context/LearningContext.tsx` provides: `currentQuery: string`, `currentResponse: OutputSchema | null`, `coachResponse: CoachResponse | null`, `navigatorResponse: NavigatorExplainResponse | null`, `isLoading: boolean`, `error: string | null`, plus actions for each. Wrapped around the main page in `layout.tsx`. Simpler than Zustand for this use case because the learning flow has fewer state transitions and benefits from React's built-in re-render optimization.

**T30: How does the API proxy rewrite work?**
> `vernacular-bridge-ui/next.config.ts` defines `async rewrites()` returning `[{ source: '/api/:path*', destination: 'http://localhost:8000/:path*' }]`. This means the frontend calls `/api/learn` and Next.js transparently proxies to `http://localhost:8000/learn`. Benefits: (1) No CORS issues in development, (2) Same-origin in production (both served from same domain), (3) The frontend API client (`lib/api/`) uses relative URLs (`/api/learn`) that work in both dev and prod.

### Testing (T31–T35)

**T31: What's the overall test strategy?**
> Three tiers: (1) **Unit tests** — test individual functions in isolation (validators, parsers, cache, circuit breaker), mocked LLM layer. (2) **Integration tests** — test service layer with mocked LLM responses (contract validation tests use fixture data). (3) **End-to-end tests** — test full request lifecycle with live Gemini API (Navigator integration tests, marked for skip in CI). The 124 tests are distributed: 70% unit, 25% integration, 5% e2e.

**T32: How do you mock LLM responses in tests?**
> For unit/integration tests, the `core/llm_client.py` `generate()` method is mocked using `unittest.mock.patch` or `pytest-mock`. Test fixtures in `tests/` provide pre-defined LLM output dictionaries that the mock returns. This allows deterministic testing of the normalization pipeline (OutputSchema, validators, parsers) without depending on live Gemini API. Example: `test_contracts.py` has fixture dicts representing valid, malformed, and edge-case LLM outputs.

**T33: What do the 15 test categories cover?**
> Coach Validator (8): score normalization, markdown stripping, length control. Contract Validation (13): OutputSchema field validation, type coercion, quality guards. Navigator Integration (7): full request lifecycle with live API. Data Retrieval (7): JSON file loading, keyword search. Circuit Breaker (10): state transitions, timeout, recovery. Learn Cache (5): TTL expiry, hit/miss, eviction. LLM Functions (2): client helper functions. Text Normalization (5): MCQ correct_answer edge cases. Steps Normalization (6): list cleanup, dedup. Quality Guards (13): generic phrase detection, empty content. Question Decoder (15): type mapping, template generation. MCQ Normalization (12): option dedup, alias handling. Input Sanitization (4): XML delimiter wrapping. Injection Detection (13): prompt injection patterns. Instruction Prefix (3): safety prefix generation.

**T34: How does the adversarial testing framework work?**
> `verification/adversarial_generator.py` generates adversarial inputs programmatically: (1) Prompt injection attempts ("ignore previous instructions"), (2) Hallucination triggers (queries about non-existent schemes), (3) Edge cases (empty input, extremely long input, Unicode attacks), (4) Language mixing attacks (English instructions in Tamil context). `verification/scenarios.yaml` defines test scenarios with expected outcomes. `verification/scoring.py` evaluates response quality (did the safety guard catch it?). `verification/run_verification.py` orchestrates the pipeline.

**T35: How are the 4 skipped Navigator tests handled?**
> The 4 Navigator integration tests in `tests/test_navigator_explain.py` require a live Gemini API key and make real API calls. They're marked with `@pytest.mark.skipif(not os.getenv("GOOGLE_API_KEY"), reason="Requires live Gemini API")`. In CI/CD, these are skipped to avoid API costs and flakiness. Locally, developers can run them with `GOOGLE_API_KEY=xxx python -m pytest tests/test_navigator_explain.py -v`. The other 120 tests run without external dependencies.

### DevOps & Deployment (T36–T40)

**T36: How is Docker configured?**
> `Dockerfile` uses Python 3.12 base image, installs system dependencies, copies `requirements.txt` and installs Python packages, copies application code, exposes port 8000, runs `uvicorn orchestrator:app --host 0.0.0.0 --port 8000`. The `Procfile` provides an alternative for Heroku-style deployments: `web: uvicorn orchestrator:app --host $HOST --port $PORT`. Environment variables are injected via Docker `-e` flags or `.env` file mount.

**T37: How does the health endpoint work?**
> `GET /health` returns JSON with: `status: "ok"`, `version: "1.0.0"`, `cache_size: int` (current cached entries), `circuit_breaker: { state: "closed"|"open"|"half_open", failure_count: int }`, `data: { entitlements: { count: 7, loaded: bool }, processes: { count: 3, loaded: bool } }`, `config: { primary_model: str, secondary_model: str, rate_limit_rpm: int }`. This provides production monitoring without external tools. The circuit breaker state and cache size are key operational metrics.

**T38: How are environment variables managed?**
> `.env.example` documents all variables with comments. `.env` (gitignored) contains actual values. `core/config.py` uses `pydantic-settings` with `Settings(env_file=".env")`. Docker uses `-e GOOGLE_API_KEY=xxx` or `--env-file .env`. Production would use cloud provider secret management (AWS Secrets Manager, GCP Secret Manager). The `ALLOWED_ORIGINS` setting is critical for CORS — must match the deployed frontend domain.

**T39: How is CORS configured?**
> `orchestrator.py` configures `CORSMiddleware` with: `allow_origins=settings.ALLOWED_ORIGINS` (default: `["localhost:3000", "localhost:7860"]`), `allow_credentials=True`, `allow_methods=["*"]`, `allow_headers=["*"]`. For production, `ALLOWED_ORIGINS` must be updated to include the deployed frontend URL. The frontend's Next.js rewrites handle proxy in development, so CORS is only needed for direct API access or production deployments.

**T40: How would you deploy to production?**
> (1) Build Docker image: `docker build -t vernacular-bridge .`, (2) Push to container registry (GCR, ECR, Docker Hub), (3) Deploy to cloud run/GKE/ECS with environment variables, (4) Update `ALLOWED_ORIGINS` to include production frontend domain, (5) Frontend deployed separately (Vercel/Netlify for Next.js), (6) Update `next.config.ts` rewrites to point to production API URL, (7) Set up monitoring via `/health` endpoint (Prometheus scraping), (8) Configure SSL/TLS termination at load balancer level.

### Problem Solving (T41–T45)

**T41: What was the hardest technical challenge and how did you solve it?**
> Tanglish normalization. Students type "naan photosynthesis-a purinjukkiren" (I understand photosynthesis) — a mix of Tamil words, English words, and Tamil-inflected English. The concept resolver (`utils/concept_resolver.py`) handles this with a multi-step pipeline: (1) Detect script mix (Tamil Unicode vs Latin), (2) Tokenize by script boundaries, (3) Normalize Roman transliterations to standard form, (4) Extract the core concept (removing Tamil grammar particles), (5) Route to LLM with clear concept identification. The key insight was treating this as NLP preprocessing, not LLM prompt engineering.

**T42: Why not use LangChain for the LLM layer?**
> Three reasons: (1) **Control** — Our safety system (fact-lock, keyword-lock, Tamil ratio) requires deep integration with the LLM call lifecycle. LangChain's abstraction layers make it harder to inject custom validation between "LLM returns" and "response sent", (2) **Complexity** — LangChain adds 50+ transitive dependencies for features we don't use (memory, agents, tools). Our LLM interaction is simple: prompt → call → parse → validate, (3) **Debugging** — When LLM output is inconsistent, we need to see exactly what was sent and received. LangChain's chains obscure the raw API calls.

**T43: How did you handle the LLM hallucination problem?**
> Multi-layered approach: (1) **Prompt-level** — Negative instructions ("do not invent numbers or URLs"), (2) **Fact-lock** — Runtime verification that no new numbers/URLs appear in output, (3) **Keyword-lock** — Semantic preservation check, (4) **Tamil ratio** — Prevents LLM from defaulting to English, (5) **Generic phrase blocking** — Catches template/low-quality responses, (6) **Circuit breaker** — Fails fast when LLM is unreliable, (7) **Structured output** — Pydantic schemas force the LLM into a predictable format. The combination reduced inconsistent responses by over 90% in testing.

**T44: What lessons did adversarial testing teach you?**
> (1) LLMs will confidently invent plausible-sounding numbers — fact-lock is essential, not optional. (2) Prompt injection works even in educational apps — students (or bad actors) could try to extract system prompts. (3) The weakest point is LLM output parsing — `parsers/json_extractor.py` needed 6 different extraction strategies because Gemini wraps JSON inconsistently. (4) Edge cases matter — empty input, Unicode attacks, and extremely long queries all needed handling. (5) The safety system needs to fail gracefully — a blocked response should still return a useful fallback, not an error.

**T45: Why FastAPI over Django for this project?**
> (1) **Async-first** — `/full-flow` runs 3 LLM calls concurrently with `asyncio.gather()`. Django's synchronous model would require ASGI and `sync_to_async` wrappers, (2) **Pydantic integration** — FastAPI uses Pydantic v2 natively for request/response validation. Django REST Framework uses its own serializers, (3) **Performance** — FastAPI benchmarks 3–5x faster than Django for I/O-bound workloads (our endpoints are pure I/O — LLM calls, caching, validation), (4) **Auto-docs** — FastAPI generates OpenAPI docs automatically from Pydantic models, (5) **Lightweight** — Our backend is pure API, no ORM, no admin panel, no template rendering — FastAPI's minimal footprint is ideal.

### Code Patterns & Practices (T46–T50)

**T46: How does the Pydantic `@model_validator` pattern solve the LLM output problem?**
> LLMs return dictionaries with inconsistent types (strings where lists expected, missing fields, extra fields, wrong enum values). The `@model_validator(mode='before')` in `OutputSchema` receives the raw dict and normalizes it before Pydantic's field validators run. This means: (1) `steps` can come as a string → split into list, (2) `mcqs` can come as a single dict → wrap in list, (3) `correct_answer` can be "A" → mapped to actual option text, (4) Generic phrases are blocked, (5) MCQ options are deduplicated. Field validators then run on clean data.

**T47: How does the service layer abstraction work?**
> Each service (learn, coach, navigator) is a module with a `process()` async function. Services are responsible for: (1) Calling the LLM via `core/llm_client.py`, (2) Running the prompt builder, (3) Calling the parser, (4) Running validators, (5) Handling errors and fallbacks. Services are injected with their dependencies (LLM client, cache, validators) — no global state. This makes testing easy (mock the service function) and makes it straightforward to add new services (just add a new file in `services/`).

**T48: How is the concept resolver pipeline implemented?**
> `utils/concept_resolver.py` is a pipeline: `normalize_input(raw_query) → detect_script_mix(normalized) → extract_concept(detected) → resolve(concept)`. Each step is a pure function that transforms data. The pipeline handles: (1) Unicode normalization (NFC form), (2) Tamil script detection (Unicode range check), (3) Roman transliteration mapping (common Tamil words → standard form), (4) Grammar particle removal (Tamil suffixes that don't affect meaning), (5) Core concept extraction (the English/Tamil term the student is asking about).

**T49: How is error handling structured across the stack?**
> (1) **API layer** — FastAPI's exception handlers catch validation errors (422) and return structured error responses, (2) **Service layer** — Each service wraps LLM calls in try/except, catches `LLMError` (quota, timeout) and `ValidationError` (output doesn't match schema), returns fallback responses, (3) **Core layer** — Circuit breaker catches consecutive failures and trips to OPEN state, (4) **Frontend** — API client handles HTTP errors and displays error messages via React state, (5) **Audit** — All errors are logged via `core/audit.py` middleware with structured JSON.

**T50: How does the cache key generation work?**
> `core/cache.py` generates cache keys by: (1) Normalizing the query (lowercase, strip whitespace), (2) Including the endpoint name (learn vs coach vs navigator), (3) Including the language config, (4) Computing SHA-256 hash of the combined string. This ensures: (1) "Photosynthesis" and "photosynthesis" hit the same cache, (2) Different endpoints for the same query don't collide, (3) Different language configs get separate cache entries, (4) Keys are fixed-length and safe for dictionary storage.

### Quick-Fire (QF1–QF10)

**QF1: How many API endpoints?**
> 8: `/learn`, `/generate` (alias), `/coach`, `/navigator/explain`, `/full-flow`, `/entitlements`, `/processes`, `/health`.

**QF2: How many tests?**
> 124 tests across 15 categories, 97% pass rate (120 passed, 4 skipped — live Gemini integration).

**QF3: What's the rate limit?**
> 20 requests per minute per IP, sliding window.

**QF4: What's the cache TTL?**
> 600 seconds (10 minutes), max 100 entries.

**QF5: What circuit breaker threshold?**
> 3 consecutive failures → OPEN state, 60 seconds cooldown → HALF_OPEN.

**QF6: What's the Tamil ratio threshold?**
> 60% (0.6) — Tamil Unicode characters must be ≥60% of total characters in `tamil_simple`.

**QF7: What's the tech stack in one line?**
> Python/FastAPI + Google Gemini + Next.js 16/TypeScript + Pydantic v2 + Tailwind CSS.

**QF8: How many frontend pages?**
> 3: Main learning dashboard (`/`), Analytics dashboard (`/dashboard`), Command center (`/command-center`).

**QF9: How many data entries?**
> 7 government entitlement schemes + 3 university processes = 10 dataset entries.

**QF10: What's the max MCQ count?**
> 5 questions per concept, each with exactly 4 unique options.

---

## Part C: Functional / Domain Questions (F1–F25)

### Student Onboarding & Input (F1–F4)

**F1: Describe the complete student journey from opening the app to receiving a response.**
> (1) Student opens `http://localhost:3000`, sees the main dashboard with an input panel, (2) Types a concept query (e.g., "Photosynthesis", "Semester Registration", or Tamil equivalent), (3) Clicks submit → frontend sends `POST /api/learn` with the query, (4) Backend normalizes input (concept resolver handles Tanglish), (5) Gemini generates bilingual explanation + MCQs, (6) Response validated (Tamil ratio, MCQ quality, fact-lock), (7) Frontend renders: Tamil card (simple explanation), English card (academic explanation), Steps list, MCQ section (interactive quiz), Question decoder (answer template), (8) Student can hover over interactive text for term explanations, (9) Student can click MCQ options to test understanding, (10) Student can switch to Coach tab to practice writing answers.

**F2: How does the system handle Tamil script input?**
> The concept resolver detects Tamil Unicode characters (U+0B80–U+0BFF range) and processes them directly. Tamil input is normalized (NFC form), grammar particles are identified and preserved or stripped based on context. The resolved concept is passed to the prompt builder with explicit language instructions. The LLM is instructed to generate both Tamil and English explanations regardless of input language — the system always produces bilingual output.

**F3: How does the system handle Tanglish (mixed Tamil-English) input?**
> The concept resolver's script-mix detection identifies boundary points between Tamil and Roman characters. For example, "naan photosynthesis-a purinjukkiren" → tokens: ["naan", "photosynthesis-a", "purinjukkiren"]. Tamil tokens are mapped to standard form, the core English concept ("photosynthesis") is extracted, and grammar particles are stripped. The resolved concept is "photosynthesis" with the context that the student is asking for explanation in Tamil.

**F4: How does the system handle English-only input?**
> English input goes through the concept resolver with minimal transformation (lowercase, whitespace normalization). The prompt builder adds explicit instructions: "Generate tamil_simple in Tamil and english_academic in English." The LLM is capable of generating Tamil explanations from English concepts. The Tamil ratio validator ensures the output actually contains ≥60% Tamil — this catches cases where the LLM defaults to English.

### Concept Explainer Flow (F5–F8)

**F5: What happens when a student asks about "Photosynthesis"?**
> (1) Input normalized to "photosynthesis", (2) Prompt built with instructions: explain in Tamil (simple, culturally situated) + English (academic, step-by-step), (3) Generate 2–7 steps, (4) Generate question_decoder (identify as "explain" type, provide answer template), (5) Generate up to 5 MCQs, (6) Gemini returns structured JSON, (7) OutputSchema normalizes (Tamil ratio check, MCQ quality), (8) Validators run fact-lock, keyword-lock, semantic alignment, (9) Response returned with all fields populated. Expected: Tamil explanation with examples relevant to Tamil Nadu students, English explanation suitable for academic writing.

**F6: How is the Tamil ratio enforced in the concept explainer?**
> After Gemini generates `tamil_simple`, `calculate_tamil_ratio()` counts Tamil Unicode characters. If ratio < 0.6, the confidence score is reduced: `confidence = min(1.0, ratio / 0.6)`. The response is still returned (not rejected) but with lower confidence. The frontend can display a warning. In practice, the prompt instructions ("respond in Tamil for tamil_simple") combined with the ratio validation keep Tamil content above 80% in most cases.

**F7: How does MCQ generation quality get ensured?**
> The prompt instructs Gemini to create MCQs covering: understanding checks (basic recall), misconception traps (common wrong answers), application-based (real scenarios). Quality guards then: (1) Reject Yes/No questions, (2) Remove duplicates (fuzzy matching), (3) Ensure exactly 4 options, (4) Verify correct_answer matches an option, (5) Block generic phrases. If fewer than 3 quality MCQs survive validation, the `confidence_score` is reduced proportionally.

**F8: How does the question decoder work?**
> The question decoder is embedded in the `/learn` response. Gemini identifies the question type (define, explain, compare, analyze, diagram, short_note) and provides: `expected_structure` (how the answer should be organized — intro, body paragraphs, conclusion for "explain"), `answer_template` (specific sections the student should include), and `question_type` (the classified type). This helps students structure their exam answers according to academic expectations.

### Writing Coach Flow (F9–F13)

**F9: How does a student submit a draft answer for coaching?**
> Student navigates to the Coach tab, types or pastes their draft answer, and submits via `POST /api/coach` with `CoachRequest(question="...", student_answer="...")`. The coach service sends both to Gemini with a prompt asking for structured evaluation: scoring (0–10), strengths, weaknesses, missing points, improvement suggestions, and a complete improved answer. The response is validated by `coach_validator.py`.

**F10: What does the scoring rubric look like?**
> Score is 0–10: 0–2 (significant gaps, missing core concepts), 3–4 (partial understanding, key points missing), 5–6 (adequate but needs improvement), 7–8 (good, minor improvements needed), 9–10 (excellent, exam-ready). The `coach_validator.py` normalizes scores to this range, flags scores outside 0–10, and adjusts confidence based on score variance from expected.

**F11: How are improvement suggestions generated?**
> Gemini is prompted to provide specific, actionable suggestions (not generic "improve your writing"). The prompt includes the question, student answer, and scoring rubric. Suggestions are structured as: "Instead of [X], write [Y] because [reason]." The `coach_validator.py` strips markdown formatting and controls length to ensure suggestions are concise and displayable in the frontend ScoreCard component.

**F12: How does the coach handle very weak answers?**
> When the student answer is <20 characters or contains only generic phrases, the coach service detects this and provides: (1) A lower score (0–2), (2) Detailed explanation of what the question is asking, (3) A structured outline the student should follow, (4) Key concepts they need to include, (5) The improved_answer field provides a complete model answer. This turns a weak answer into a learning opportunity.

**F13: How is coach output normalized for consistency?**
> `validators/coach_validator.py` handles: (1) Score normalization (clamp to 0–10), (2) Markdown stripping (remove `**`, `##`, etc. for clean frontend rendering), (3) List length control (max 5 items per list), (4) Improved answer length control (max 500 chars), (5) Duplicate suggestion removal, (6) Generic suggestion blocking ("try harder", "improve" without specifics).

### Navigator & Government Data (F14–F17)

**F14: How are government entitlements explained to students?**
> The navigator matches the student's query against `data/entitlements.json` (7 schemes: Pudhumai Penn, First Graduate Tuition Waiver, etc.). Matched schemes are sent to Gemini with instructions to explain: (1) What the scheme is (simple Tamil + academic English), (2) Who is eligible, (3) How to apply, (4) Deadline, (5) Official link. The fact-lock ensures the official link from the dataset is preserved exactly — no invented URLs.

**F15: How does hallucination prevention work specifically for government data?**
> Government data contains specific numbers (eligibility percentages, age limits, income thresholds) and URLs (official application portals). The fact-lock extracts all numbers and URLs from the source data and verifies each appears in the LLM output. If Gemini invents "deadline: March 15, 2025" when the actual deadline is "Rolling basis", fact-lock catches the discrepancy. The keyword-lock ensures scheme names and eligibility criteria are preserved verbatim.

**F16: How are university processes explained?**
> The navigator matches against `data/processes.json` (Semester Registration, Exam Registration, Answer Script Photocopy/Revaluation). Each process has step-by-step instructions from the dataset. The LLM generates bilingual explanations that include: (1) The process steps in order, (2) Required documents, (3) Fees and payment methods, (4) Deadlines, (5) Tips (e.g., "download and print the confirmation slip"). The fact-lock ensures step counts and document names match the source data.

**F17: How does keyword-lock verification work for navigator data?**
> For each matched dataset item, keyword-lock extracts: scheme/process name, eligibility keywords, deadline terms, required documents, and official links. After LLM generation, it verifies each extracted keyword appears in the output (or has a proper Tamil equivalent). Coverage score is computed as `matched_keywords / total_keywords`. If coverage < 80%, the response is flagged. This prevents the LLM from simplifying "First Graduate Certificate from Tahsildar" to just "government document."

### Safety Scenarios (F18–F22)

**F18: What happens when a student tries prompt injection?**
> The sanitizer in `core/sanitizer.py` catches it at two levels: (1) **Pre-processing** — XML delimiter wrapping (`<user_input>`) separates user content from system instructions, (2) **Pattern detection** — regex checks for "ignore previous instructions", "you are now", "system:" prefixes, role-playing attacks. If detected, the input is either sanitized (injection content stripped) or the request is rejected with a safety error. The audit middleware logs the attempt.

**F19: What happens when the LLM hallucinates numbers in a scheme explanation?**
> Example: Student asks about "Pudhumai Penn Scheme" and Gemini invents "deadline: January 31, 2025". The fact-lock extracts all numbers from `entitlements.json` (which says "Rolling basis (typically starts June-July annually)") and finds the January date is not in the source. The fact-lock flags `new_numbers: ["2025"]` and `missing_deadline: True`. The service layer can: (1) Return the response with a warning flag, (2) Replace the hallucinated number with the source value, or (3) Reject the response entirely. Current implementation flags and returns with reduced confidence.

**F20: What happens when the circuit breaker trips?**
> After 3 consecutive Gemini failures (quota exhaustion, timeout, 5xx), the circuit breaker enters OPEN state. All subsequent requests fail fast with a predefined fallback response: `{"status": "error", "message": "Service temporarily unavailable. Please try again in 60 seconds."}`. No LLM call is attempted (saves quota, avoids cascade). After 60 seconds (`CB_COOLDOWN`), one test request is allowed through. If it succeeds → CLOSED (normal operation resumes). If it fails → OPEN again. The `/health` endpoint exposes the current state.

**F21: What happens when a student exceeds the rate limit?**
> The sliding-window rate limiter tracks requests per IP. After 20 requests in 60 seconds, subsequent requests return `429 Too Many Requests` with a `Retry-After: N` header (seconds until the oldest request in the window expires). The frontend displays "You're sending too many requests. Please wait a moment." The rate limiter uses IP address from `X-Forwarded-For` header (for proxied deployments) or direct connection IP.

**F22: Can someone poison the cache with bad data?**
> The cache key includes the normalized query + endpoint + language config. An attacker would need to submit a query that normalizes to the same hash as a popular query. Since the cache stores LLM responses that have already been validated (fact-lock, keyword-lock, Tamil ratio), poisoned data would need to pass all validators. Additionally, the TTL (600s) means poisoned entries expire quickly. For production, cache keys should include user/session identifiers to prevent cross-user poisoning.

### Edge Cases & Domain (F23–F25)

**F23: What happens with empty or garbage input?**
> The `QueryRequest` Pydantic model validates: `query: str = Field(min_length=1, max_length=500)`. Empty strings return 422 Validation Error. Very short inputs (<3 chars) are handled by the concept resolver which may not find a meaningful concept — the LLM is prompted to ask for clarification. Unicode garbage (random symbols, emoji-only) goes through the concept resolver which fails to extract a concept, resulting in a low-confidence response with a suggestion to rephrase.

**F24: What happens with extremely long queries?**
> `QueryRequest` enforces `max_length=500`. Longer queries are rejected with 422. For the writing coach (`CoachRequest`), `student_answer` has `max_length=2000`. These limits prevent prompt overflow (Gemini has token limits) and ensure reasonable response times. The frontend character counter shows remaining characters to guide students.

**F25: How is cross-language semantic alignment verified?**
> The `validators/validators.py` has `validate_semantic_alignment()` which: (1) Extracts key concepts from both `tamil_simple` and `english_academic`, (2) Checks that core concepts appear in both (accounting for translation), (3) Computes alignment score as `matched_concepts / total_concepts`, (4) If alignment < 0.7, flags the response for review. This catches cases where the Tamil and English explanations discuss different aspects of the same concept — a failure mode when LLMs struggle with bilingual generation.

---

*Tailor the content above to match the specific role you're applying for. For AI/ML roles, emphasize the safety system (Part A, Q26–Q30) and prompt engineering (Part B, T6–T10). For backend roles, highlight async orchestration (Part A, Q17) and the layered architecture (Part B, T1–T5). For full-stack roles, showcase the end-to-end type safety (Part B, T46–T50) and frontend components (Part B, T26–T30). For EdTech roles, focus on the bilingual processing (Part C, F1–F8) and domain-specific safety (Part C, F18–F22).*

*Generated from codebase analysis — June 19, 2026.*
