"""Data contracts for the Vernacular Bridge backend.

Defines Pydantic models for LLM output validation, including
OutputSchema with built-in normalization via @model_validator.

Classes:
    QuestionType: Enum of valid exam question types.
    Status: Enum for pipeline status codes.
    QuestionDecoder: Decoded question metadata.
    MCQ: Multiple-choice question with validation.
    OutputSchema: Main output model with before-validator normalization.
"""

from __future__ import annotations
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, field_validator, model_validator
from enum import Enum


class QuestionType(str, Enum):
    """Valid exam question types the system can decode."""
    DEFINE = "define"
    EXPLAIN = "explain"
    COMPARE = "compare"
    ANALYZE = "analyze"
    DIAGRAM = "diagram"
    SHORT_NOTE = "short_note"


class Status(str, Enum):
    """Pipeline status codes."""
    SUCCESS = "success"
    RETRY = "retry"
    FALLBACK = "fallback"


# ---------------------------------------------------------------------------
# Question Decoder
# ---------------------------------------------------------------------------

# Canonical mapping from free-form LLM strings → valid QuestionType values.
_QUESTION_TYPE_MAP: dict[str, str] = {
    "process explanation": "explain",
    "detailed explanation": "explain",
    "how it works": "explain",
    "definition": "define",
    "what is": "define",
    "comparison": "compare",
    "contrast": "compare",
    "difference": "compare",
    "analysis": "analyze",
    "evaluation": "analyze",
    "diagram": "diagram",
    "visual representation": "diagram",
    "short note": "short_note",
}

_VALID_QUESTION_TYPES: set[str] = {t.value for t in QuestionType}


class QuestionDecoder(BaseModel):
    """Decoded question metadata from the LLM."""
    question_type: QuestionType
    expected_structure: str = Field(
        ..., description="Logical structure for the exam answer"
    )
    answer_template: str = Field(
        ..., description="Pre-filled template for students to follow"
    )


# ---------------------------------------------------------------------------
# MCQ
# ---------------------------------------------------------------------------

class MCQ(BaseModel):
    """A single multiple-choice question with 4 options."""
    question: str
    options: List[str] = Field(..., min_length=4, max_length=4)
    correct_answer: str

    @model_validator(mode="after")
    def validate_correct_answer_in_options(self) -> MCQ:
        """Ensure correct_answer is one of the four options."""
        if self.correct_answer not in self.options:
            raise ValueError(
                f"Correct answer '{self.correct_answer}' must be one "
                f"of the options: {self.options}"
            )
        if len(set(self.options)) != 4:
            raise ValueError("MCQ options must be unique")
        return self


# ---------------------------------------------------------------------------
# Generic phrases that signal low-quality LLM output
# ---------------------------------------------------------------------------

_GENERIC_PHRASES: tuple[str, ...] = (
    "identify the concept",
    "break down",
    "core idea",
    "key components",
    "in simple terms",
)


# ---------------------------------------------------------------------------
# OutputSchema — main LLM output model with built-in normalization
# ---------------------------------------------------------------------------

class OutputSchema(BaseModel):
    """Validated bilingual learning output from the LLM.

    Includes a ``@model_validator(mode='before')`` that normalizes raw LLM
    dictionaries before Pydantic field validation runs.  This replaces the
    former standalone ``normalize_output()`` function with ~150 lines of
    ad-hoc logic.

    Normalisation covers:
        * Text field stripping and type coercion
        * Steps list normalisation (string → list, dedup)
        * Quality guards (empty content, generic phrases, minimum steps)
        * QuestionDecoder type mapping (free-form → canonical enum)
        * MCQ option dedup, correct_answer key aliasing, option count fix
    """

    tamil_simple: str = Field(..., min_length=10, max_length=800)
    english_academic: str = Field(..., min_length=20, max_length=1200)
    steps: List[str] = Field(..., min_length=2, max_length=7)
    question_decoder: QuestionDecoder
    mcqs: List[MCQ] = Field(..., max_length=5)

    # -----------------------------------------------------------------------
    # Before-validator: runs on the raw dict *before* field parsing
    # -----------------------------------------------------------------------

    @model_validator(mode="before")
    @classmethod
    def normalize_raw_llm_output(cls, data: dict) -> dict:
        """Normalize a raw LLM dict into OutputSchema-compatible form.

        Handles type coercion, missing fields, quality guards, question-type
        mapping, and MCQ option cleanup — all in one pass before Pydantic
        field validators execute.
        """
        if not isinstance(data, dict):
            data = {}

        result: dict = {}

        # --- A. TEXT FIELDS ------------------------------------------------
        result["tamil_simple"] = str(data.get("tamil_simple", "")).strip()
        result["english_academic"] = str(data.get("english_academic", "")).strip()

        # --- B. STEPS ------------------------------------------------------
        raw_steps = data.get("steps")
        if isinstance(raw_steps, list):
            steps = [str(s).strip() for s in raw_steps if s]
        elif isinstance(raw_steps, str) and raw_steps.strip():
            steps = [raw_steps.strip()]
        else:
            steps = []
        result["steps"] = steps

        # Quality Guard: Block Empty
        if not result["tamil_simple"] or not result["english_academic"]:
            raise ValueError("Empty content generated")

        # Quality Guard: Block Generic Phrases
        for phrase in _GENERIC_PHRASES:
            if phrase in result["tamil_simple"].lower():
                raise ValueError(f"Generic content detected: {phrase}")
            if phrase in result["english_academic"].lower():
                raise ValueError(f"Generic content detected: {phrase}")
            for step in result["steps"]:
                if phrase in step.lower():
                    raise ValueError(
                        f"Generic content detected in steps: {phrase}"
                    )

        if len(result["steps"]) < 2:
            raise ValueError("Insufficient steps generated")

        # --- C. QUESTION DECODER -------------------------------------------
        raw_qd = data.get("question_decoder")
        if not isinstance(raw_qd, dict):
            raw_qd = {}

        qt = str(raw_qd.get("question_type", "explain")).lower()
        qt = _QUESTION_TYPE_MAP.get(qt, qt)
        if qt not in _VALID_QUESTION_TYPES:
            qt = "explain"

        result["question_decoder"] = {
            "question_type": qt,
            "expected_structure": str(
                raw_qd.get("expected_structure", "")
            ).strip(),
            "answer_template": str(
                raw_qd.get("answer_template", "")
            ).strip(),
        }

        # --- D. MCQs -------------------------------------------------------
        raw_mcqs = data.get("mcqs")
        clean_mcqs: list[dict] = []

        if isinstance(raw_mcqs, list):
            for mcq in raw_mcqs:
                if not isinstance(mcq, dict):
                    continue

                # Normalize correct_answer from any key alias
                correct: str | None = None
                for key in ("correct_answer", "answer", "correct"):
                    if key in mcq and mcq[key]:
                        correct = str(mcq[key])
                        break

                question = str(mcq.get("question", "")).strip()
                if not question:
                    continue

                # Normalize options to list of strings
                raw_options = mcq.get("options")
                if isinstance(raw_options, list):
                    options = [
                        str(opt).strip() for opt in raw_options if opt
                    ]
                elif isinstance(raw_options, str):
                    options = [
                        opt.strip()
                        for opt in raw_options.split("|")
                        if opt.strip()
                    ]
                else:
                    options = []

                # Remove duplicates while preserving order
                seen: set[str] = set()
                unique_options: list[str] = []
                for opt in options:
                    if opt.lower() not in seen:
                        seen.add(opt.lower())
                        unique_options.append(opt)
                options = unique_options

                if len(options) < 4:
                    continue

                # If correct_answer not in options, replace last option
                if correct and correct not in options:
                    options[-1] = correct

                final_options = options[:4]

                clean_mcqs.append({
                    "question": question,
                    "options": final_options,
                    "correct_answer": correct,
                })

        result["mcqs"] = clean_mcqs[:5]

        return result
