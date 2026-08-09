"""Navigator route — POST /navigator/explain.

Thin controller that parses the request, delegates to navigator_service,
and returns the validated bilingual explanation.

Routes:
    explain_item: POST /navigator/explain — explain a dataset item.
"""

from fastapi import APIRouter, Depends, HTTPException
from models.request import LanguageConfig
from models.navigator import NavigatorExplainRequest, NavigatorExplainResponse
from services.navigator_service import internal_navigator_explain
from core.auth import verify_api_key

router = APIRouter()


@router.post("/navigator/explain", response_model=NavigatorExplainResponse)
async def explain_item(request: NavigatorExplainRequest, _key: str = Depends(verify_api_key)):
    """Explain a dataset item with Fact-Lock hallucination protection.

    Args:
        request: NavigatorExplainRequest with the item dict.

    Returns:
        NavigatorExplainResponse with bilingual explanation.

    Raises:
        HTTPException: 422 if safety checks fail or LLM errors.
    """
    lang_config = LanguageConfig()

    result = await internal_navigator_explain(request.item, lang_config)
    if not result:
        raise HTTPException(
            status_code=422, detail="Safety check failed or LLM error."
        )

    return NavigatorExplainResponse(**result)
