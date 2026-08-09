"""Robust JSON extraction from LLM response text.

Handles raw text that may contain preamble/trailing content around
a JSON object or array. Attempts direct parse first, then falls back
to boundary detection.

Functions:
    extract_json: Parse JSON from text, supporting both {} and [].
"""

import json


def extract_json(text: str):
    """Extract and parse JSON from potentially noisy LLM response text.

    Tries direct json.loads first. If that fails, locates the outermost
    JSON object ``{...}`` or array ``[...]`` boundaries and parses the slice.

    Args:
        text: The raw response text from the LLM.

    Returns:
        The parsed Python object (dict or list).

    Raises:
        ValueError: If no valid JSON can be found in the text.
        TypeError: If text is not a string.
    """
    if not isinstance(text, str):
        return text  # Already parsed or error dict

    # Attempt direct parse first
    try:
        return json.loads(text)
    except (json.JSONDecodeError, ValueError):
        pass

    # Detect JSON type boundaries
    first_curly = text.find("{")
    last_curly = text.rfind("}")
    first_square = text.find("[")
    last_square = text.rfind("]")

    # Choose whichever appears first as the root
    if first_curly != -1 and (first_square == -1 or first_curly < first_square):
        start, end = first_curly, last_curly
    elif first_square != -1:
        start, end = first_square, last_square
    else:
        raise ValueError("No JSON object or array found in response")

    if start != -1 and end != -1:
        try:
            return json.loads(text[start : end + 1])
        except Exception as e:
            raise ValueError(f"JSON extraction failed after slicing: {e}")

    raise ValueError("Invalid JSON boundaries")
