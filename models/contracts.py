from __future__ import annotations
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, field_validator, model_validator
from enum import Enum

class QuestionType(str, Enum):
    DEFINE = "define"
    EXPLAIN = "explain"
    COMPARE = "compare"
    ANALYZE = "analyze"
    DIAGRAM = "diagram"
    SHORT_NOTE = "short_note"

class Status(str, Enum):
    SUCCESS = "success"
    RETRY = "retry"
    FALLBACK = "fallback"

class QuestionDecoder(BaseModel):
    question_type: QuestionType
    expected_structure: str = Field(..., description="Logical structure for the exam answer")
    answer_template: str = Field(..., description="Pre-filled template for students to follow")

class MCQ(BaseModel):
    question: str
    options: List[str] = Field(..., min_length=4, max_length=4)
    correct_answer: str

    @model_validator(mode="after")
    def validate_correct_answer_in_options(self) -> MCQ:
        if self.correct_answer not in self.options:
            raise ValueError(f"Correct answer '{self.correct_answer}' must be one of the options: {self.options}")
        if len(set(self.options)) != 4:
            raise ValueError("MCQ options must be unique")
        return self

class OutputSchema(BaseModel):
    tamil_simple: str = Field(..., min_length=10, max_length=800)
    english_academic: str = Field(..., min_length=20, max_length=1200)
    steps: List[str] = Field(..., min_length=2, max_length=7)
    question_decoder: QuestionDecoder
    mcqs: List[MCQ] = Field(..., max_length=5)


class InputMetadata(BaseModel):
    language: Literal["ta", "en", "mixed"]
    grade_level: Literal["6-12", "UG"]
    subject: str

class InputSchema(BaseModel):
    query: str = Field(..., min_length=1)
    metadata: InputMetadata
