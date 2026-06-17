from pydantic import BaseModel, ConfigDict
from typing import Dict, Any

class NavigatorExplainRequest(BaseModel):
    item: Dict[str, Any]
    
    model_config = ConfigDict(extra="ignore")

class NavigatorExplainResponse(BaseModel):
    explanation_primary: str
    summary_secondary: str
    
    model_config = ConfigDict(extra="ignore")
