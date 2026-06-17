import sys
import os
import json
from fastapi.testclient import TestClient

# Add root to sys.path to import orchestrator
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestrator import app

client = TestClient(app)

SAMPLE_ENTITLEMENT = {
    "name": "Pudhumai Penn Scheme",
    "eligibility": "Girl students who studied from Class 6 to 12 in Government schools in Tamil Nadu.",
    "deadline": "Rolling basis",
    "benefits": "\u20b91,000 per month",
    "official_link": "https://www.penkalvi.tn.gov.in/",
    "category": ["General", "OBC", "SC", "ST", "Minority"]
}

def test_navigator_explain_basic():
    print("\n--- Testing Navigator Explain: Basic Success ---")
    response = client.post("/navigator/explain", json={"item": SAMPLE_ENTITLEMENT})
    assert response.status_code == 200
    data = response.json()
    assert "explanation_primary" in data
    assert "summary_secondary" in data
    print(f"DEBUG Response Primary (fixed): {data['explanation_primary'][:100].encode('ascii', 'backslashreplace').decode('ascii')}...")
    print(f"DEBUG Response Secondary (fixed): {data['summary_secondary'][:100].encode('ascii', 'backslashreplace').decode('ascii')}...")
    
    # Check Fact-Lock preserved numbers (usually Benefit amounts)
    combined = data["explanation_primary"] + data["summary_secondary"]
    assert "1,000" in combined or "1000" in combined
    
    # URL might be rephrased or omitted in prose, but shouldn't be halluncinated.
    # We rely on Fact-Lock test for hallucination prevention.
    print("  Passed! Basic structure and key numbers preserved.")

def test_navigator_hallucination_prevention():
    print("\n--- Testing Navigator Explain: Hallucination Prevention (Missing Field) ---")
    # Item with NO deadline and NO benefits listed
    stripped_item = {
        "name": "Ghost Scholarship",
        "eligibility": "Only for students with zero family income.",
        "official_link": "https://ghost.gov.in/"
    }
    response = client.post("/navigator/explain", json={"item": stripped_item})
    assert response.status_code == 200
    data = response.json()
    
    # Check that LLM didn't invent a price or date
    combined = data["explanation_primary"] + data["summary_secondary"]
    # Check for common hallucinated numbers or strings
    assert "\u20b9" not in combined # Should not invent a benefit amount
    assert "202" not in combined # Should not invent a year
    print("  Passed! No invented facts found.")

def test_fact_lock_violation():
    print("\n--- Testing Fact-Lock Enforcement ---")
    # This test is hard without mocking the LLM, but we can verify the validator logic directly
    from orchestrator import SafetyGuard
    
    input_item = {"url": "https://real.com", "num": "500"}
    hallucinated_output = "This gives you 1000 rupees and go to https://fake.com"
    
    # Should fail Fact-Lock
    assert SafetyGuard.validate_fact_lock(input_item, hallucinated_output) is False
    print("  Validator correctly rejected hallucinated URL and number!")

def test_length_control():
    print("\n--- Testing Length Control ---")
    long_text = "word " * 200
    from orchestrator import SafetyGuard
    truncated = SafetyGuard.enforce_length_control(long_text, 120)
    assert len(truncated.split()) == 120
    print("  Length control correctly truncated long text.")

if __name__ == "__main__":
    try:
        test_navigator_explain_basic()
        test_navigator_hallucination_prevention()
        test_fact_lock_violation()
        test_length_control()
        print("\nALL NAVIGATOR EXPLAIN TESTS PASSED! [OK]")
    except AssertionError as e:
        print(f"\nTEST FAILED! [FAIL]")
        raise e
    except Exception as e:
        print(f"\nAN ERROR OCCURRED: {e}")
        import traceback
        traceback.print_exc()
