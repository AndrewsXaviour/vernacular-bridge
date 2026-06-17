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

    result = {}
    result["score"] = int(data.get("score", 0))
    result["structure_feedback"] = str(data.get("structure_feedback", "")).strip()
    
    missing = data.get("missing_points", [])
    if isinstance(missing, list):
        result["missing_points"] = [str(p).strip() for p in missing if p]
    else:
        result["missing_points"] = []
        
    result["language_feedback"] = str(data.get("language_feedback", "")).strip()
    
    raw_improved = str(data.get("improved_answer", "")).strip()
    result["improved_answer"] = strip_markdown(raw_improved)
    
    return result

def validate_coach_logic(data: Dict[str, Any]):
    """
    Apply strict academic logic and safeguards to the coach output.
    """
    score = data["score"]
    improved_answer = data["improved_answer"]
    structure_feedback = data["structure_feedback"]
    missing_points = data["missing_points"]

    # 1. Score Range
    if not (0 <= score <= 10):
        raise ValueError(f"Score {score} out of bounds (0-10)")

    # 2. Missing Points vs Score Logic
    if score < 8 and len(missing_points) < 1:
        raise ValueError("Score < 8 requires at least 1 missing point")
    if score <= 5 and len(missing_points) < 2:
        raise ValueError("Score <= 5 requires at least 2 missing points")

    # 3. Safeguard 1: Answer Length Sanity Check
    words = improved_answer.split()
    if len(words) < 30:
        raise ValueError("Improved answer too short (< 30 words)")
    
    if len(words) > 300:
        # Truncate to 300 words
        data["improved_answer"] = " ".join(words[:300])

    # 4. Safeguard 2: Score–Tone Alignment Check
    if score <= 4:
        lower_feedback = structure_feedback.lower()
        if "improve" not in lower_feedback and "missing" not in lower_feedback:
            # Injecting critical feedback if LLM missed the tone
            data["structure_feedback"] = f"Needs significant improvement. {structure_feedback}"

    # 5. Language Handling (Primary feedback exists check)
    if not data["language_feedback"]:
         raise ValueError("Language feedback is empty")

    return data
