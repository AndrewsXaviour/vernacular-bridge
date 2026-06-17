# Vernacular Bridge

**Bilingual Academic Bridging & Exam Preparation Intelligence**

> Not just translation. A Cognitive Bridge that turns Tamil-medium understanding into academic English mastery for first-generation students.

---

## 🎯 Problem

45% of undergraduate students in Indian government universities are first-generation college students. They arrive with strong foundational knowledge from Tamil-medium schools, but higher education operates entirely in English — textbooks, instruction, and examinations. The resulting language-knowledge gap leads to academic failure attributable to **language barriers, not intellectual incapacity**.

## 💡 Solution

Vernacular Bridge transforms a student's Tamil-medium understanding into confident academic English performance through:

1. **Bilingual Concept Explainer** — Simple Tamil explanation with culturally situated examples + precise academic English with clear steps
2. **Academic Question Decoder** — Identifies question type (define, explain, compare, analyze) and provides section-by-section answer templates
3. **Exam Preparation Intelligence** — Generates concept-based MCQs including understanding checks, misconception traps, and application-based questions
4. **Writing Coach** — Structured feedback on student draft answers with scoring and improvement suggestions
5. **Navigator** — Bilingual explanation of dataset items with strict fact-lock hallucination protection

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | FastAPI (Python) |
| **LLM** | Google Gemini API (2.5 Flash / 2.5 Pro) |
| **Frontend** | Next.js 15 + TypeScript + Tailwind CSS |
| **Schema Validation** | Pydantic v2 |
| **Architecture** | Parallel async orchestration with circuit breaker fallback |

## 🚀 Getting Started

### Backend

```bash
# Install dependencies
pip install -r requirements.txt

# Set your Google API key
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY

# Start the server
python orchestrator.py
```

The API will be available at `http://localhost:8000`

### Frontend

```bash
cd vernacular-bridge-ui

npm install
npm run dev
```

The UI will be available at `http://localhost:3000`

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/full-flow` | POST | Unified orchestration — runs Learn, Coach, and Navigator in parallel |
| `/learn` | POST | Bilingual concept explanation with MCQs |
| `/coach` | POST | Evaluate student answers with structured feedback |
| `/navigator/explain` | POST | Bilingual explanation of dataset items |
| `/entitlements` | GET | Query government entitlements/schemes |
| `/processes` | GET | Query government processes |
| `/health` | GET | Health check with cache and rate-limit stats |

## 📁 Project Structure

```
.
├── orchestrator.py          # FastAPI app with all endpoints
├── models/                  # Pydantic request/response schemas
│   ├── request.py           # Input models (QueryRequest, FullFlowRequest)
│   ├── contracts.py         # Output schema with validation
│   ├── coach.py             # Coach request/response models
│   ├── navigator.py         # Navigator models
│   └── full_flow.py         # Unified response model
├── utils/
│   ├── prompt_builder.py    # LLM prompt construction
│   ├── concept_resolver.py  # Tanglish/Tamil input normalization
│   └── preprocessing.py     # Input preprocessing utilities
├── validators/
│   ├── validators.py        # Content validation & confidence scoring
│   └── coach_validator.py   # Coach output normalization
├── llm/
│   └── llm_engine.py        # LLM engine abstraction
├── verification/            # Adversarial testing & scoring
├── data/                    # Pre-loaded datasets (entitlements, processes)
├── tests/                   # Unit & integration tests
├── docs/                    # Schema contracts documentation
└── vernacular-bridge-ui/    # Next.js frontend application
    └── src/
        ├── app/             # Next.js app router pages
        ├── components/      # React components (cards, coach, navigator)
        ├── context/         # React context providers
        ├── lib/api/         # API client functions
        ├── store/           # State management
        └── utils/           # Frontend utilities
```

## 🔒 Safety & Quality

- **Fact-Lock** — Prevents hallucination by verifying no new numbers/URLs appear in output
- **Keyword-Lock** — Ensures core semantic meaning is preserved across languages
- **Tamil Ratio Validation** — Enforces ≥60% Tamil Unicode in Tamil explanations
- **Circuit Breaker** — Automatic fallback from primary to secondary LLM on quota exhaustion
- **Per-IP Rate Limiting** — 20 requests/minute per client
- **Structured Output** — Strict Pydantic schema validation on all responses

## 📊 Output Schema

```json
{
  "schema_version": "1.0",
  "status": "success",
  "confidence_score": 0.95,
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

## 🌍 Why Not ChatGPT?

| Aspect | Generic LLMs | Vernacular Bridge |
|--------|-------------|-------------------|
| Output Structure | Free-form, inconsistent | Strict bilingual structured JSON |
| Language Control | Mixed tone, possible slang | Controlled textbook Tamil + academic English |
| Exam Focus | General answers | Question decoding + structured templates |
| Consistency | Varies widely | Quality checks + internal consistency |

## 🚧 Future Expansion

- Support for additional Indian languages (Hindi, Telugu, Kannada)
- Voice-first interface for low-literacy users
- Integration with university syllabus datasets
- Personalized learning paths based on student performance

## 📄 License

This project was built for the Hackathon.
