"""Data loading and deterministic retrieval service.

Provides lazy-loaded JSON data access and keyword-based scored
retrieval for the navigator module. Data is loaded from disk on
first access and cached in memory.

Functions:
    get_entitlements_data: Return the loaded entitlements list.
    get_processes_data: Return the loaded processes list.
    retrieve_best_match: Score and rank items against a query.
    normalize_value: Strip and lowercase a string for matching.
    get_data_health: Return data loading status for /health endpoint.
"""

import os
import json
import logging
from typing import Optional

from core.config import settings

logger = logging.getLogger(__name__)

# Lazy-loaded data caches
_entitlements_data: Optional[list] = None
_processes_data: Optional[list] = None


def _get_data_dir() -> str:
    """Return the absolute path to the data directory.

    Uses settings.data_dir from environment, defaulting to 'data'.

    Returns:
        Absolute path to the data directory.
    """
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), settings.data_dir)


def load_json(path: str) -> list:
    """Safely load a JSON file, returning an empty list on error.

    Args:
        path: Absolute or relative path to the JSON file.

    Returns:
        The parsed list, or an empty list on missing file/parse error.
    """
    if not os.path.exists(path):
        logger.warning("DATA_FILE_MISSING | path=%s", path)
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, list):
                logger.error("DATA_FILE_INVALID_TYPE | path=%s | expected=list", path)
                return []
            return data
    except json.JSONDecodeError as e:
        logger.error("DATA_FILE_CORRUPT | path=%s | error=%s", path, e)
        return []
    except Exception as e:
        logger.error("DATA_FILE_ERROR | path=%s | error=%s", path, e)
        return []


def get_entitlements_data() -> list:
    """Return the loaded entitlements data, lazy-loading on first call.

    Returns:
        List of entitlement dictionaries from entitlements.json.
    """
    global _entitlements_data
    if _entitlements_data is None:
        path = os.path.join(_get_data_dir(), "entitlements.json")
        _entitlements_data = load_json(path)
    return _entitlements_data


def get_processes_data() -> list:
    """Return the loaded processes data, lazy-loading on first call.

    Returns:
        List of process dictionaries from processes.json.
    """
    global _processes_data
    if _processes_data is None:
        path = os.path.join(_get_data_dir(), "processes.json")
        _processes_data = load_json(path)
    return _processes_data


def get_data_health() -> dict:
    """Return data loading status for the /health endpoint.

    Provides visibility into whether data files were found and loaded,
    their item counts, and the data directory path.

    Returns:
        Dict with data_dir, entitlements, and processes health info.
    """
    data_dir = _get_data_dir()
    entitlements = get_entitlements_data()
    processes = get_processes_data()

    return {
        "data_dir": data_dir,
        "entitlements": {
            "count": len(entitlements),
            "loaded": _entitlements_data is not None,
        },
        "processes": {
            "count": len(processes),
            "loaded": _processes_data is not None,
        },
    }


def normalize_value(value: Optional[str]) -> str:
    """Strip whitespace and lowercase a string for matching.

    Args:
        value: The string to normalize, or None.

    Returns:
        The normalized string, or empty string if value is None.
    """
    return value.strip().lower() if value else ""


def retrieve_best_match(query: str) -> Optional[dict]:
    """Score and return the best-matching item from all datasets.

    Counts keyword overlap between the query and each item's
    search_keywords, with a name-match bonus.

    Args:
        query: The student query string.

    Returns:
        The highest-scoring item dict, or None if no match found.
    """
    if not query:
        return None

    query_words = set(normalize_value(query).split())
    best_item = None
    max_score = 0

    all_data = get_entitlements_data() + get_processes_data()

    for item in all_data:
        keywords = [normalize_value(k) for k in item.get("search_keywords", [])]
        score = sum(1 for word in query_words if any(word in kw for kw in keywords))

        if normalize_value(query) in normalize_value(item.get("name", "")):
            score += 2

        if score > max_score:
            max_score = score
            best_item = item

    return best_item if max_score > 0 else None
