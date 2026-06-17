from __future__ import annotations
from typing import List
from pydantic import BaseModel, Field, field_validator
from .request import LanguageConfig

class CoachRequest(BaseModel):
    question: str = Field(..., min_length=10)
    student_answer: str = Field(..., min_length=5)
    language_config: LanguageConfig = Field(default_factory=LanguageConfig)

class CoachResponse(BaseModel):
    score: int = Field(..., ge=0, le=10)
    structure_feedback: str = Field(..., min_length=5)
    missing_points: List[str] = Field(..., min_length=0)
    language_feedback: str = Field(..., min_length=5)
    improved_answer: str = Field(..., min_length=30)

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
