"""
Integration tests for /navigator/explain endpoint.

Covers:
- Basic explain response structure and fact preservation
- Hallucination prevention with missing fields
- Fact-Lock enforcement via SafetyGuard
- Length control enforcement
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from orchestrator import app

client = TestClient(app)

SAMPLE_ENTITLEMENT = {
    "name": "Pudhumai Penn Scheme",
    "eligibility": "Girl students who studied from Class 6 to 12 in Government schools in Tamil Nadu.",
    "deadline": "Rolling basis",
    "benefits": "₹1,000 per month",
    "official_link": "https://www.penkalvi.tn.gov.in/",
    "category": ["General", "OBC", "SC", "ST", "Minority"]
}


class TestNavigatorExplainBasic:
    """Test basic /navigator/explain response structure."""

    def test_returns_200(self):
        response = client.post("/navigator/explain", json={"item": SAMPLE_ENTITLEMENT})
        assert response.status_code == 200

    def test_has_required_fields(self):
        response = client.post("/navigator/explain", json={"item": SAMPLE_ENTITLEMENT})
        data = response.json()
        assert "explanation_primary" in data
        assert "summary_secondary" in data

    def test_preserves_numbers(self):
        response = client.post("/navigator/explain", json={"item": SAMPLE_ENTITLEMENT})
        data = response.json()
        combined = data["explanation_primary"] + data["summary_secondary"]
        assert "1,000" in combined or "1000" in combined


class TestNavigatorHallucinationPrevention:
    """Test that missing fields are not fabricated."""

    def test_no_invented_benefits(self):
        stripped_item = {
            "name": "Ghost Scholarship",
            "eligibility": "Only for students with zero family income.",
            "official_link": "https://ghost.gov.in/"
        }
        response = client.post("/navigator/explain", json={"item": stripped_item})
        assert response.status_code == 200
        data = response.json()
        combined = data["explanation_primary"] + data["summary_secondary"]
        assert "₹" not in combined
        assert "202" not in combined


class TestFactLockEnforcement:
    """Test SafetyGuard fact-lock validation."""

    def test_rejects_hallucinated_url_and_number(self):
        from core.safety_guard import SafetyGuard
        input_item = {"url": "https://real.com", "num": "500"}
        hallucinated_output = "This gives you 1000 rupees and go to https://fake.com"
        assert SafetyGuard.validate_fact_lock(input_item, hallucinated_output) is False

    def test_accepts_correct_facts(self):
        from core.safety_guard import SafetyGuard
        input_item = {"url": "https://real.com", "num": "500"}
        correct_output = "Go to https://real.com and you get 500 rupees."
        assert SafetyGuard.validate_fact_lock(input_item, correct_output) is True


class TestLengthControl:
    """Test SafetyGuard length enforcement."""

    def test_truncates_to_word_limit(self):
        from core.safety_guard import SafetyGuard
        long_text = "word " * 200
        truncated = SafetyGuard.enforce_length_control(long_text, 120)
        assert len(truncated.split()) == 120
