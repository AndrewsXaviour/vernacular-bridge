"""Retrieval routes — GET /entitlements, GET /processes.

Thin controllers for deterministic JSON-based filtering of
entitlement and process datasets.

Routes:
    get_entitlements: GET /entitlements — filtered entitlement list.
    get_processes: GET /processes — filtered process list.
"""

from typing import Optional

from fastapi import APIRouter
from services.retrieval_service import (
    get_entitlements_data,
    get_processes_data,
    normalize_value,
)

router = APIRouter()


@router.get("/entitlements")
def get_entitlements(
    category: Optional[str] = None,
    applicable_for: Optional[str] = None,
    keyword: Optional[str] = None,
):
    """Return entitlements filtered by category, applicability, and keyword.

    Args:
        category: Optional category filter (case-insensitive).
        applicable_for: Optional applicability filter (case-insensitive exact).
        keyword: Optional keyword filter (case-insensitive partial match).

    Returns:
        Dict with 'count' and 'results' keys.
    """
    results = get_entitlements_data()

    if category:
        q_cat = normalize_value(category)
        results = [
            item
            for item in results
            if q_cat in [normalize_value(c) for c in item.get("category", [])]
        ]

    if applicable_for:
        q_app = normalize_value(applicable_for)
        results = [
            item
            for item in results
            if normalize_value(item.get("applicable_for")) == q_app
        ]

    if keyword and normalize_value(keyword):
        q_key = normalize_value(keyword)
        results = [
            item
            for item in results
            if any(q_key in normalize_value(k) for k in item.get("search_keywords", []))
        ]

    results = list({item["name"]: item for item in results}.values())

    return {"count": len(results), "results": results}


@router.get("/processes")
def get_processes(keyword: Optional[str] = None):
    """Return processes filtered by keyword.

    Args:
        keyword: Optional keyword filter (case-insensitive partial match).

    Returns:
        Dict with 'count' and 'results' keys.
    """
    results = get_processes_data()

    if keyword and normalize_value(keyword):
        q_key = normalize_value(keyword)
        results = [
            item
            for item in results
            if any(q_key in normalize_value(k) for k in item.get("search_keywords", []))
        ]

    results = list({item["name"]: item for item in results}.values())

    return {"count": len(results), "results": results}
