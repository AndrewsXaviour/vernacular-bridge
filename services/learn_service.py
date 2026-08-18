"""Learn service — bilingual concept explanation generation.

Handles the core /learn flow: concept resolution, prompt assembly,
LLM call, JSON parsing, output normalization, Pydantic validation,
and caching.

Functions:
    internal_learn: Full learn pipeline from query to validated output.
"""

import logging
from typing import Any, Optional

from core.llm_client import async_generate_from_llm
from core.cache import LearnCache
from core.config import settings
from parsers.json_extractor import extract_json
from models.contracts import OutputSchema
from utils.prompt_builder import build_prompt
from utils.concept_resolver import resolve_concept

logger = logging.getLogger(__name__)

# Module-level cache instance
_learn_cache = LearnCache(max_size=settings.cache_max_size, ttl=settings.cache_ttl)


def get_learn_cache_size() -> int:
    """Return the current number of entries in the learn cache.

    Used by the health endpoint to report cache utilization.

    Returns:
        Count of cached entries.
    """
    return _learn_cache.size()


async def internal_learn(query: str, lang_config: Any) -> Optional[dict]:
    """Execute the full learn pipeline: cache → concept → LLM → validate.

    Steps:
        1. Check cache with TTL for an existing response.
        2. Resolve concept from query, build prompt, call LLM.
        3. Parse JSON, validate with Pydantic (normalization is built-in).
        4. Cache and return the validated result.

    Args:
        query: The student query in Tamil, Tanglish, or English.
        lang_config: LanguageConfig with primary/secondary language pair.

    Returns:
        The validated output dict, or None on failure.
    """
    # 1. Cache check
    cache_key = f"{query}_{lang_config.primary}_{lang_config.secondary}".lower()
    cached = _learn_cache.get(cache_key)
    if cached is not None:
        return cached

    # 2. LLM call
    concept, tamil_anchor, source = resolve_concept(query)
    prompt = build_prompt(
        concept=concept,
        domain="Academic",
        primary_lang=lang_config.primary,
        secondary_lang=lang_config.secondary,
    )

    raw_response = await async_generate_from_llm(prompt)
    parsed = extract_json(raw_response)
    if not parsed:
        return None

    if parsed.get("status") == "error":
        return parsed

    # 3. Pydantic validates AND normalizes via @model_validator(mode='before')
    validated = OutputSchema.model_validate(parsed)
    result = validated.model_dump()

    # 4. Cache the result
    _learn_cache.put(cache_key, result)
    return result
