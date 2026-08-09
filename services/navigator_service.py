"""Navigator service — bilingual explanation of dataset items.

Handles the core /navigator/explain flow: prompt assembly, LLM call,
JSON parsing, and safety guard validation (Fact-Lock, Keyword-Lock).

Functions:
    internal_navigator_explain: Full navigator pipeline with safety guards.
"""

import json
import logging
from typing import Any, Optional

from core.llm_client import async_generate_from_llm
from core.safety_guard import SafetyGuard
from parsers.json_extractor import extract_json

logger = logging.getLogger(__name__)


async def internal_navigator_explain(
    item: dict, lang_config: Any
) -> Optional[dict]:
    """Execute the full navigator pipeline: prompt → LLM → safety guards.

    Steps:
        1. Build a bilingual explanation prompt from the dataset item.
        2. Call the LLM and parse the JSON response.
        3. Validate with Fact-Lock (no hallucinated numbers/URLs) and
           Keyword-Lock (core meaning preserved).
        4. Apply length control and return the result.

    Args:
        item: The dataset item dict (entitlement or process).
        lang_config: LanguageConfig with primary/secondary language pair.

    Returns:
        The validated explanation dict, or None if safety checks fail.
    """
    prompt = f"""EXPLAIN the following dataset item in TWO languages:
1. Primary: Simple {lang_config.primary} (explanation_primary)
2. Secondary: Academic {lang_config.secondary} (summary_secondary)

INPUT DATA:
{json.dumps(item, indent=2)}

STRICT RULES:
- You MUST ONLY use the information provided in the input JSON.
- Do NOT add any new facts, examples, or assumptions.
- Return ONLY a JSON object with keys: "explanation_primary", "summary_secondary".
"""
    raw_response = await async_generate_from_llm(prompt)
    parsed = extract_json(raw_response)
    if not parsed:
        return None

    primary = str(parsed.get("explanation_primary", ""))
    secondary = str(parsed.get("summary_secondary", ""))

    # Safety Guards
    combined_output = f"{primary} {secondary}"
    if not SafetyGuard.validate_fact_lock(item, combined_output):
        return None
    if not SafetyGuard.validate_keyword_lock(item, combined_output):
        return None

    return {
        "explanation_primary": SafetyGuard.enforce_length_control(primary, 120),
        "summary_secondary": SafetyGuard.enforce_length_control(secondary, 80),
    }
