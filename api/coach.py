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

    # F12: Weak Answer Edge Case
    if len(request.student_answer.strip()) < 20:
        return {
            "score": 1,
            "strengths": [],
            "weaknesses": ["Answer is too short to evaluate properly.", "Lacks fundamental details."],
            "missing_points": ["Almost all key concepts are missing."],
            "improvement_suggestions": ["Instead of a single sentence, write a full paragraph explaining the concept.", "Ensure you cover the 'how' and 'why'."],
            "improved_answer": "Your answer is too short for the AI to refine without hallucinating. Please elaborate on your points and try again.",
        }

    result = await internal_coach(
        request.question, request.student_answer, request.language_config
    )
    if not result:
        return {
            "score": 0,
            "strengths": [],
            "weaknesses": ["Unable to evaluate answer due to a system error."],
            "missing_points": ["System Error"],
            "improvement_suggestions": ["Please try again."],
            "improved_answer": "System encountered an error during evaluation. Please try again.",
        }
    return result
