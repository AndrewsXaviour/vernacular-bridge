from typing import Optional
from pydantic import BaseModel, Field

class LanguageConfig(BaseModel):
    primary: str = Field("tamil", description="The primary language for simple explanations")
    secondary: str = Field("english", description="The secondary language for academic explanations")

class QueryRequest(BaseModel):
    user_input: str = Field(..., min_length=3)
    language_config: LanguageConfig = Field(default_factory=LanguageConfig)

class FullFlowRequest(BaseModel):
    query: str = Field(..., min_length=3)
    student_answer: Optional[str] = None
    use_navigator: bool = False
    language_config: LanguageConfig = Field(default_factory=LanguageConfig)
