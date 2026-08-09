from __future__ import annotations
from typing import List
from pydantic import BaseModel, Field, field_validator
from .request import LanguageConfig

class CoachRequest(BaseModel):
    """Request model for the writing coach endpoint.

    Attributes:
        question: The exam question or concept being evaluated.
        student_answer: The student's draft answer to evaluate.
        language_config: Primary and secondary language pair.

    Raises:
        ValidationError: If question exceeds 2000 chars or student_answer
            exceeds 10000 chars.
    """
    question: str = Field(..., min_length=10, max_length=2000)
    student_answer: str = Field(..., min_length=5, max_length=10000)
    language_config: LanguageConfig = Field(default_factory=LanguageConfig)

class CoachResponse(BaseModel):
    """Response model for the writing coach endpoint.

    Attributes:
        score: Rubric score from 0 to 10.
        structure_feedback: Structural feedback on the answer.
        missing_points: Key points the student missed.
        language_feedback: Language quality feedback.
        improved_answer: A model improved version of the answer.

    Raises:
        ValidationError: If improved_answer exceeds 10000 chars, or
            missing_points count is insufficient for the given score.
    """
    score: int = Field(..., ge=0, le=10)
    structure_feedback: str = Field(..., min_length=5, max_length=5000)
    missing_points: List[str] = Field(..., min_length=0)
    language_feedback: str = Field(..., min_length=5, max_length=5000)
    improved_answer: str = Field(..., min_length=30, max_length=10000)

    @field_validator("missing_points")
    @classmethod
    def validate_missing_points(cls, v, info):
        score = info.data.get("score")
        if score is not None:
            if score < 8 and len(v) < 1:
                raise ValueError("missing_points must contain at least 1 item if score < 8")
            if score <= 5 and len(v) < 2:
                raise ValueError("missing_points must contain at least 2 items if score <= 5")
        return v
