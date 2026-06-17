# Vernacular Bridge: Contracts & Schema Specification

This document defines the interface between the LLM orchestration layer and the frontend. It ensures that all outputs are deterministic, validated, and optimized for academic bridging.

## 1. Input Schema

The input query and context required to trigger a generation.

| Field | Type | Description | Values |
| :--- | :--- | :--- | :--- |
| `query` | `string` | The student's question (Tamil/Tanglish). | e.g. "ஒளிச்சேர்க்கை explain பண்ணுங்க" |
| `metadata` | `object` | Contextual details. | |
| `metadata.language` | `enum` | Primary input language. | `["ta", "en", "mixed"]` |
| `metadata.grade_level`| `enum` | Target academic level. | `["6-12", "UG"]` |
| `metadata.subject` | `string` | Subject domain. | e.g. "Biology", "History" |

---

## 2. Output Schema (Strict)

The structured JSON response required from the LLM.

```json
{
  "schema_version": "1.0",
  "status": "success | retry | fallback",
  "confidence_score": 0.95,
  "failure_reasons": [],
  "tamil_simple": "...",
  "english_academic": "...",
  "steps": ["Step 1...", "Step 2...", "Step 3..."],
  "question_decoder": {
    "question_type": "define | explain | compare | analyze | diagram | short_note",
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

---

## 3. Mandatory Constraints

### A. Linguistic & Tone
- **Tamil Ratio**: `tamil_simple` must contain ≥60% Tamil Unicode characters.
- **English Tone**: `english_academic` must use formal vocabulary (e.g. *consequently*, *inherent*).
- **No Tanglish**: Simple Tamil explanation must be pure Tamil, not hybrid.

### B. Structural Rules
- **Steps**: Minimum 3, maximum 7. Must show logical progression (Step 1, Step 2...).
- **MCQs**: Exactly 4 options per question. Max 5 questions. Options must be unique.
- **Lengths**:
    - `tamil_simple`: 50 - 800 characters.
    - `english_academic`: 80 - 1200 characters.

### C. Failure Codes (`failure_reasons`)
- `LOW_TAMIL_RATIO`: Tamil character density below 0.6.
- `MCQ_INVALID`: Options count mismatch or duplicate options.
- `LOW_ALIGNMENT`: Tamil and English content logically decoupled.
- `LENGTH_VIOLATION`: Content too short or too long.

---

## 4. Lifecycle & Fallback Mode

### State: `fallback`
Triggered on major failures (e.g. total script mismatch).
- **Validation**: Strict ratio/length checks are relaxed.
- **Constraints**:
    - `tamil_simple`: Required (minimal explanation provided).
    - `mcqs`: Max 2 (if any).
    - `failure_reasons`: Populated with the cause of fallback.

---

## 5. Security & Determinism
- **No Additional Properties**: Any field not in the schema will trigger a validation error.
- **Schema Version**: Must strictly match "1.0".
