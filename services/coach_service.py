"""Coach service — writing coach evaluation.

Handles the core /coach flow: prompt assembly, LLM call, JSON parsing,
coach-specific normalization, and Pydantic validation.

Functions:
    internal_coach: Full coach pipeline from question+answer to validated output.
"""

import logging
from typing import Any, Optional

from core.llm_client import async_generate_from_llm
from parsers.json_extractor import extract_json
from models.coach import CoachResponse
from utils.prompt_builder import build_coach_prompt
from validators.coach_validator import normalize_coach_output, validate_coach_logic

logger = logging.getLogger(__name__)


async def internal_coach(
    question: str, student_answer: str, lang_config: Any
) -> Optional[dict]:
    """Execute the full coach pipeline: prompt → LLM → validate.

    Steps:
        1. Build the coach prompt from question and student answer.
        2. Call the LLM and parse the JSON response.
        3. Normalize and validate through coach-specific validators.
        4. Return the validated CoachResponse dict.

    Args:
        question: The exam question or concept being evaluated.
        student_answer: The student's draft answer.
        lang_config: LanguageConfig with primary/secondary language pair.

    Returns:
        The validated coach output dict, or None on failure.
    """
    prompt = build_coach_prompt(
        question=question,
        student_answer=student_answer,
        primary_lang=lang_config.primary,
        secondary_lang=lang_config.secondary,
    )

    raw_response = await async_generate_from_llm(prompt)
    parsed = extract_json(raw_response)
    if not parsed:
        return None

    normalized = normalize_coach_output(parsed)
    validated_logic = validate_coach_logic(normalized)
    validated = CoachResponse.model_validate(validated_logic)
    return validated.model_dump()
