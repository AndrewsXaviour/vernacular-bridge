import sys
import os
from fastapi.testclient import TestClient

# Add root to sys.path to import orchestrator
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestrator import app

client = TestClient(app)

def test_check_counts():
    print("\n--- Verifying Counts ---")
    response = client.get("/entitlements")
    assert response.status_code == 200
    print(f"Total Entitlements: {response.json()['count']}")
    
    response = client.get("/processes")
    assert response.status_code == 200
    print(f"Total Processes: {response.json()['count']}")

def test_checklist():
    print("\n--- Running User Checklist ---")
    
    # ✅ Test 1 — Case Insensitivity
    print("Test 1: Case Insensitivity (category=sc)")
    r1 = client.get("/entitlements?category=sc")
    data1 = r1.json()
    assert data1["count"] > 0
    # Check if all returned items have SC in category (case-insensitive)
    for item in data1["results"]:
        categories = [c.lower() for c in item["category"]]
        assert "sc" in categories
    print(f"  Passed! Count: {data1['count']}")

    # ✅ Test 2 — Combined Filters
    print("Test 2: Combined Filters (category=obc&applicable_for=ug)")
    r2 = client.get("/entitlements?category=obc&applicable_for=ug")
    data2 = r2.json()
    assert data2["count"] > 0
    for item in data2["results"]:
        categories = [c.lower() for c in item["category"]]
        assert "obc" in categories
        assert item["applicable_for"].lower() == "ug"
    print(f"  Passed! Count: {data2['count']}")

    # ✅ Test 3 — Keyword Partial Match
    print("Test 3: Keyword Partial Match (keyword=review)")
    r3 = client.get("/processes?keyword=review")
    data3 = r3.json()
    assert data3["count"] > 0
    # Revaluation Process contains "paper review" in keywords
    found = False
    for item in data3["results"]:
        if any("review" in kw.lower() for kw in item["search_keywords"]):
            found = True
    assert found
    print(f"  Passed! Count: {data3['count']}")

    # ✅ Test 4 — Empty Case
    print("Test 4: Empty Case (category=random)")
    r4 = client.get("/entitlements?category=random")
    data4 = r4.json()
    assert data4["count"] == 0
    assert data4["results"] == []
    print("  Passed! Count: 0")

    # ✅ Test 5 — No Filters
    print("Test 5: No Filters (GET /entitlements)")
    r5 = client.get("/entitlements")
    data5 = r5.json()
    assert data5["count"] > 0
    print(f"  Passed! Count: {data5['count']}")

if __name__ == "__main__":
    try:
        test_check_counts()
        test_checklist()
        print("\nALL RETRIEVAL TESTS PASSED! [OK]")
    except AssertionError as e:
        print(f"\nTEST FAILED! [FAIL]")
        raise e
    except Exception as e:
        print(f"\nAN ERROR OCCURRED: {e}")
        import traceback
        traceback.print_exc()
