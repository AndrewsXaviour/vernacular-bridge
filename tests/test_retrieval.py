"""
Integration tests for data retrieval endpoints.

Covers:
- Entitlements and processes count endpoints
- Case-insensitive category filtering
- Combined filter queries
- Keyword partial matching
- Empty result cases
- No-filter full retrieval
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from orchestrator import app

client = TestClient(app)


class TestCounts:
    """Test count endpoints return valid data."""

    def test_entitlements_count(self):
        response = client.get("/entitlements")
        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert data["count"] > 0

    def test_processes_count(self):
        response = client.get("/processes")
        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert data["count"] > 0


class TestEntitlementsFiltering:
    """Test entitlements query filters."""

    def test_case_insensitive_category(self):
        r = client.get("/entitlements?category=sc")
        data = r.json()
        assert data["count"] > 0
        for item in data["results"]:
            categories = [c.lower() for c in item["category"]]
            assert "sc" in categories

    def test_combined_filters(self):
        r = client.get("/entitlements?category=obc&applicable_for=ug")
        data = r.json()
        assert data["count"] > 0
        for item in data["results"]:
            categories = [c.lower() for c in item["category"]]
            assert "obc" in categories
            assert item["applicable_for"].lower() == "ug"

    def test_empty_result_for_unknown_category(self):
        r = client.get("/entitlements?category=random")
        data = r.json()
        assert data["count"] == 0
        assert data["results"] == []

    def test_no_filters_returns_all(self):
        r = client.get("/entitlements")
        data = r.json()
        assert data["count"] > 0


class TestProcessesFiltering:
    """Test processes query filters."""

    def test_keyword_partial_match(self):
        r = client.get("/processes?keyword=review")
        data = r.json()
        assert data["count"] > 0
        found = any(
            any("review" in kw.lower() for kw in item["search_keywords"])
            for item in data["results"]
        )
        assert found
