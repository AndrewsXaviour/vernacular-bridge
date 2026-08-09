"""Full-flow route — POST /full-flow.

Thin controller that orchestrates Learn, Coach, and Navigator
in parallel with per-IP rate limiting and request tracking.

Routes:
    full_flow: POST /full-flow — unified orchestration endpoint.
"""

import asyncio
import uuid
import time
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from models.request import FullFlowRequest
from models.full_flow import FullFlowResponse
from services.learn_service import internal_learn
from services.coach_service import internal_coach
from services.navigator_service import internal_navigator_explain
from services.retrieval_service import retrieve_best_match
from core.rate_limiter import check_rate_limit
from core.llm_client import safe_call
from core.auth import verify_api_key
from core.sanitizer import check_injection_patterns

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/full-flow", response_model=FullFlowResponse)
async def full_flow(
    request: FullFlowRequest, fastapi_request: Request, response: Response,
    _key: str = Depends(verify_api_key),
):
    """Orchestrate Learn + Coach + Navigator in parallel.

    Applies per-IP rate limiting and tracks requests via short UUID.

    Args:
        request: FullFlowRequest with query, optional student_answer,
                 use_navigator flag, and language_config.
        fastapi_request: The raw FastAPI Request for IP extraction.
        response: The FastAPI Response object.

    Returns:
        FullFlowResponse with learning, evaluation, and navigator results.

    Raises:
        HTTPException: 422 if rate limit is exceeded.
    """
    # 0. Injection detection
    check_injection_patterns(request.query)
    if request.student_answer:
        check_injection_patterns(request.student_answer)

    # 1. Rate limit check
    client_ip = fastapi_request.client.host if fastapi_request.client else "unknown"
    if not check_rate_limit(client_ip):
        logger.warning("RATE_LIMIT_EXCEEDED | ip=%s", client_ip)
        raise HTTPException(
            status_code=422,
            detail="Too Many Requests from this IP. Please try again in a minute.",
        )

    # 2. Request tracking
    req_id = str(uuid.uuid4())[:8]
    logger.info(
        "[%s] FULL_FLOW_START | ip=%s | query=%s...", req_id, client_ip, request.query[:50]
    )

    def log(msg: str, level: str = "info") -> None:
        final_msg = f"[{req_id}] {msg}"
        getattr(logger, level)(final_msg)

    # 3. Prepare tasks
    tasks: list = []
    task_keys: list[str] = []

    # Learn (always)
    tasks.append(
        safe_call(internal_learn(request.query, request.language_config), "LEARN")
    )
    task_keys.append("learning")

    # Coach (conditional)
    if request.student_answer:
        tasks.append(
            safe_call(
                internal_coach(
                    request.query, request.student_answer, request.language_config
                ),
                "COACH",
            )
        )
        task_keys.append("evaluation")
    else:
        tasks.append(asyncio.sleep(0, result=None))
        task_keys.append("evaluation")

    # Navigator (conditional)
    if request.use_navigator:
        match = retrieve_best_match(request.query)
        if match:
            tasks.append(
                safe_call(
                    internal_navigator_explain(match, request.language_config),
                    "NAVIGATOR",
                )
            )
        else:
            log("NAVIGATOR_NO_MATCH_FOUND", "info")
            tasks.append(asyncio.sleep(0, result=None))
    else:
        tasks.append(asyncio.sleep(0, result=None))
    task_keys.append("navigator")

    # 4. Parallel execution
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # 5. Process results
    final_output = {"learning": None, "evaluation": None, "navigator": None}

    for key, result in zip(task_keys, results):
        if isinstance(result, Exception):
            log(f"MODULE_{key.upper()}_EXCEPTION | msg={str(result)}", "error")
            final_output[key] = None
        else:
            final_output[key] = result

    log("FULL_FLOW_COMPLETE")
    return FullFlowResponse(**final_output)
