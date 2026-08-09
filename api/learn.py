"""Learn route — POST /learn and POST /generate.

Thin controllers that parse the request, delegate to learn_service,
and return the result or a safe fallback.

Routes:
    learn_content: POST /learn — primary learn endpoint.
    generate_legacy: POST /generate — legacy alias for /learn.
"""

from fastapi import APIRouter, Depends
from models.request import QueryRequest
from services.learn_service import internal_learn
from core.llm_client import SAFE_FALLBACK_JSON
from core.auth import verify_api_key
from core.sanitizer import check_injection_patterns

router = APIRouter()


@router.post("/learn")
async def learn_content(request: QueryRequest, _key: str = Depends(verify_api_key)):
    """Handle a single-concept learn request.

    Args:
        request: QueryRequest with user_input and language_config.

    Returns:
        The validated bilingual explanation dict, or a fallback error.
    """
    check_injection_patterns(request.user_input)
    result = await internal_learn(request.user_input, request.language_config)
    if not result:
        return SAFE_FALLBACK_JSON
    return result


@router.post("/generate")
async def generate_legacy(request: QueryRequest, _key: str = Depends(verify_api_key)):
    """Legacy alias for the /learn endpoint.

    Args:
        request: QueryRequest with user_input and language_config.

    Returns:
        The validated bilingual explanation dict, or a fallback error.
    """
    check_injection_patterns(request.user_input)
    result = await internal_learn(request.user_input, request.language_config)
    if not result:
        return SAFE_FALLBACK_JSON
    return result
