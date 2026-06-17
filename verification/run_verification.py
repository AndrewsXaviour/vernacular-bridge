import yaml
import json
from verification.verifier import run_verification_case
from verification.scoring import calculate_case_score, grade_system

def run_all_verification():
    # 1. Load scenarios
    try:
        with open("verification/scenarios.yaml", "r") as f:
            scenarios = yaml.safe_load(f)
    except FileNotFoundError:
        print("Error: scenarios.yaml not found.")
        return
    except Exception as e:
        print(f"Error loading scenarios.yaml: {e}")
        return

    total_score = 0
    num_cases = len(scenarios)
    results_summary = []

    print("\n[STARTING ADVANCED VERIFICATION LAYER...]")
    print("=" * 60)

    for case in scenarios:
        name = case.get("name")
        case_type = case.get("type")
        expected = case.get("expected")

        # 2. Run Verification
        result = run_verification_case(case_type)
        
        # 3. Calculate Score
        scores = calculate_case_score(result, expected)
        total_score += scores["total_score"]
        
        # 4. Print detailed results
        print(f"CASE: {name}")
        print(f"Type: {case_type}")
        print(f"Status: {result['triggered_status']}")
        print(f"Score: {scores['total_score']:.2f}")
        print(f"Grade: {grade_system(scores['total_score'])}")
        print(f"Actual Reasons: {result['failure_reasons']}")
        print(f"Expected Status: {expected['status']}")
        print("-" * 60)
        
        results_summary.append({
            "name": name,
            "type": case_type,
            "status": result["triggered_status"],
            "score": scores["total_score"]
        })

    # 5. Print Final Summary
    final_score = total_score / num_cases if num_cases > 0 else 0
    final_grade = grade_system(final_score)

    print("\n" + "=" * 60)
    print("FINAL VERIFICATION SUMMARY")
    print("=" * 60)
    print(f"TOTAL CASES RUN: {num_cases}")
    print(f"TOTAL SCORE: {final_score:.2f}")
    print(f"FINAL GRADE: {final_grade}")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    run_all_verification()
