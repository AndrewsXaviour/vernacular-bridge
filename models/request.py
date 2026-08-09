from typing import Optional
from pydantic import BaseModel, Field

class LanguageConfig(BaseModel):
    primary: str = Field("tamil", description="The primary language for simple explanations")
    secondary: str = Field("english", description="The secondary language for academic explanations")

class QueryRequest(BaseModel):
    """Request model for single-concept learn queries.

    Attributes:
        user_input: The student query in Tamil, Tanglish, or English.
        language_config: Primary and secondary language pair.

    Raises:
        ValidationError: If user_input is shorter than 3 or longer than 2000 chars.
    """
    user_input: str = Field(..., min_length=3, max_length=2000)
    language_config: LanguageConfig = Field(default_factory=LanguageConfig)

class FullFlowRequest(BaseModel):
    """Request model for the full-flow orchestration endpoint.

    Attributes:
        query: The student query in Tamil, Tanglish, or English.
        student_answer: Optional student draft for coaching evaluation.
        use_navigator: Whether to include entitlement/process navigation.
        language_config: Primary and secondary language pair.

    Raises:
        ValidationError: If query is shorter than 3 or longer than 2000 chars,
            or student_answer exceeds 10000 chars.
    """
    query: str = Field(..., min_length=3, max_length=2000)
    student_answer: Optional[str] = Field(None, max_length=10000)
    use_navigator: bool = False
    language_config: LanguageConfig = Field(default_factory=LanguageConfig)
