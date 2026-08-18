import json
import re
from typing import Dict, Any

def strip_markdown(text: str) -> str:
    """
    Remove basic markdown formatting like headers (###), bold (**), and italics (_ or *).
    """
    # Remove headers
    text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
    # Remove bold/italics
    text = re.sub(r'[*_]{1,3}', '', text)
    # Remove lists
    text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)
    # Remove numbered lists
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
    return text.strip()

def normalize_coach_output(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize LLM output for the coach module to ensure schema compatibility.
    """
    if not isinstance(data, dict):
        data = {}

    def parse_list(key: str) -> list[str]:
        val = data.get(key, [])
        if isinstance(val, list):
            return [str(p).strip() for p in val if p][:5] # F13: max 5 items
        return []

    result = {}
    result["score"] = int(data.get("score", 0))
    result["strengths"] = parse_list("strengths")
    result["weaknesses"] = parse_list("weaknesses")
    result["missing_points"] = parse_list("missing_points")
    result["improvement_suggestions"] = parse_list("improvement_suggestions")
    
    raw_improved = str(data.get("improved_answer", "")).strip()
    result["improved_answer"] = strip_markdown(raw_improved)[:500] # F13: max 500 chars
    
    return result

def validate_coach_logic(data: Dict[str, Any]):
    """
    Apply strict academic logic and safeguards to the coach output.
    """
    score = data["score"]
    improved_answer = data["improved_answer"]
    missing_points = data["missing_points"]
    strengths = data["strengths"]
    weaknesses = data["weaknesses"]

    # 1. Score Range
    if not (0 <= score <= 10):
        raise ValueError(f"Score {score} out of bounds (0-10)")

    # 2. Missing Points vs Score Logic
    if score < 8 and len(missing_points) < 1:
        raise ValueError("Score < 8 requires at least 1 missing point")
    if score <= 5 and len(missing_points) < 2:
        raise ValueError("Score <= 5 requires at least 2 missing points")

    # 3. Safeguard 1: Answer Length Sanity Check
    if len(improved_answer) < 30:
        raise ValueError("Improved answer too short (< 30 chars)")

    # 4. Safeguard 2: Score–Tone Alignment Check
    if score <= 4 and len(weaknesses) == 0:
        data["weaknesses"].append("Needs significant improvement.")

    return data
