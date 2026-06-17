from typing import Optional
from pydantic import BaseModel
from .contracts import OutputSchema
from .coach import CoachResponse
from .navigator import NavigatorExplainResponse

class FullFlowResponse(BaseModel):
    learning: Optional[OutputSchema] = None
    evaluation: Optional[CoachResponse] = None
    navigator: Optional[NavigatorExplainResponse] = None
