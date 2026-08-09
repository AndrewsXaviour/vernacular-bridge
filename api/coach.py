"""Coach route — POST /coach.

Thin controller that parses the request, delegates to coach_service,
and returns the validated coaching response.

Routes:
    coach_answer: POST /coach — evaluate a student's draft answer.
"""

from fastapi import APIRouter, Depends
from models.coach import CoachRequest
from services.coach_service import internal_coach
from core.auth import verify_api_key
from core.sanitizer import check_injection_patterns

router = APIRouter()


@router.post("/coach")
async def coach_answer(request: CoachRequest, _key: str = Depends(verify_api_key)):
    """Evaluate a student's answer using a strict academic rubric.

    Args:
        request: CoachRequest with question, student_answer, and language_config.

    Returns:
        The validated coaching response dict, or an error fallback.
    """
    check_injection_patterns(request.question)
    check_injection_patterns(request.student_answer)
    result = await internal_coach(
        request.question, request.student_answer, request.language_config
    )
    if not result:
        return {
            "score": 0,
            "structure_feedback": "Unable to evaluate answer due to a system error.",
            "missing_points": ["System Error"],
            "language_feedback": "Error processing request.",
            "improved_answer": "System encountered an error during evaluation. Please try again.",
        }
    return result
