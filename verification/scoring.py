def calculate_case_score(result: dict, expected: dict) -> dict:
    """
    Calculates the distribution of scores for a single verification case.
    """
    scores = {
        "schema_enforcement": 0.0,
        "validator_detection": 0.0,
        "trigger_correctness": 0.0,
        "reason_accuracy": 0.0
    }
    
    # 1. Schema enforcement
    # If expected reason is SCHEMA_VIOLATION, then we expect failure in pass_schema/pass_pydantic
    if expected["failure_reason"] == "SCHEMA_VIOLATION":
        if not result["pass_schema"] or not result["pass_pydantic"]:
            scores["schema_enforcement"] = 1.0
    else:
        # If not a schema violation, it should pass basic schema/pydantic checks
        if result["pass_schema"] and result["pass_pydantic"]:
            scores["schema_enforcement"] = 1.0

    # 2. Validator detection
    # Check if the specific expected failure reason was detected.
    # We do NOT penalize if other (correct) reasons were also found.
    expected_reason = expected["failure_reason"]
    
    # Map SCHEMA_VIOLATION to SCHEMA_INVALID for actual detection
    actual_reasons = result["failure_reasons"]
    search_reason = "SCHEMA_INVALID" if expected_reason == "SCHEMA_VIOLATION" else expected_reason
    
    if search_reason in actual_reasons:
        scores["validator_detection"] = 1.0
    elif expected_reason == "MCQ_INVALID" and any("MCQ" in r for r in actual_reasons):
        # Broad match for MCQ related issues if specific code not found
        scores["validator_detection"] = 1.0
    elif expected_reason == "STEPS_INVALID" and any("STEPS" in r for r in actual_reasons):
        scores["validator_detection"] = 1.0

    # 3. Trigger correctness
    # If status matches expected status
    if result["triggered_status"] == expected["status"]:
        scores["trigger_correctness"] = 1.0

    # 4. Reason accuracy
    # This specifically checks if the primary expected failure reason is present.
    # In Task 5, we are told NOT to penalize for extra correct detections.
    if scores["validator_detection"] == 1.0:
        scores["reason_accuracy"] = 1.0

    # Total score calculation
    scores["total_score"] = sum([v for k, v in scores.items() if k != "total_score"]) / 4.0
    return scores

def grade_system(total_score: float) -> str:
    if total_score >= 0.9:
        return "EXCELLENT"
    elif total_score >= 0.75:
        return "GOOD"
    else:
        return "WEAK"
