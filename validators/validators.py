import re
import math
from typing import List, Dict, Any, Tuple
from difflib import SequenceMatcher

# Configuration
ALIGNMENT_THRESHOLD = 0.3
TAMIL_RATIO_THRESHOLD = 0.6
MIN_STEP_LENGTH = 10
STRUCTURAL_FAILURES = [
    "NO_TAMIL",
    "EMPTY_OUTPUT",
    "SCHEMA_INVALID",
    "MISSING_FIELDS"
]

def is_tamil(char: str) -> bool:
    """Check if a character belongs to the Tamil Unicode block."""
    return '\u0b80' <= char <= '\u0bff'

def calculate_tamil_ratio(text: str) -> float:
    """Calculate the ratio of Tamil characters to total characters (excluding whitespace)."""
    clean_text = "".join(text.split())
    if not clean_text:
        return 0.0
    tamil_chars = sum(1 for char in clean_text if is_tamil(char))
    return tamil_chars / len(clean_text)

def extract_keywords(text: str) -> set:
    """Extract significant keywords from English text for alignment checks."""
    # Simple stopword/noise filter for academic English
    noise = {'the', 'and', 'is', 'are', 'was', 'were', 'it', 'this', 'that', 'with', 'from', 'to', 'for', 'in', 'on', 'at', 'of', 'by', 'an', 'be', 'as'}
    words = re.findall(r'\b\w{4,}\b', text.lower())
    return {w for w in words if w not in noise}

def validate_semantic_alignment(english_text: str, mcqs: List[Dict]) -> float:
    """Compute an alignment score between the academic English content and the MCQs."""
    base_keywords = extract_keywords(english_text)
    
    mcq_text = " ".join([m.get('question', '') + " " + " ".join(m.get('options', [])) for m in mcqs])
    mcq_keywords = extract_keywords(mcq_text)
    
    total_keywords = base_keywords.union(mcq_keywords)
    if len(total_keywords) < 5:
        return 0.0 # Insufficient content for alignment
        
    overlap = base_keywords.intersection(mcq_keywords)
    score = len(overlap) / len(base_keywords) if base_keywords else 0.0
    return score

def validate_mcq_difficulty(mcqs: List[Dict]) -> bool:
    """Ensure MCQs are academic and not trivial."""
    if not mcqs:
        return True
        
    questions = [m.get('question', '') for m in mcqs]
    
    # Rule 1: Reject if all questions are "What is..." or "Define..."
    patterns = ["what is", "define", "what are"]
    if all(any(q.lower().startswith(p) for p in patterns) for q in questions):
        return False
        
    # Rule 2: Reject if any question is Yes/No type or excessively simple
    for q in questions:
        q_clean = q.lower().strip()
        if q_clean.endswith("?") and (
            any(q_clean.startswith(w) for w in ["is ", "are ", "do ", "does ", "can "]) or
            any(word in q_clean for word in ["yes or no", "true or false", "is it true"])
        ):
            return False
            
    # Rule 3: Options too similar
    for m in mcqs:
        opts = [o.lower().strip() for o in m.get('options', [])]
        for i in range(len(opts)):
            for j in range(i + 1, len(opts)):
                similarity = SequenceMatcher(None, opts[i], opts[j]).ratio()
                if similarity > 0.8:
                    return False
                    
    # Rule 4: Identical answer patterns (too simple to guess)
    answers = [m.get('correct_answer', '') for m in mcqs]
    if len(answers) > 2 and len(set(answers)) == 1:
        return False
        
    return True

def validate_mcq_diversity(mcqs: List[Dict]) -> bool:
    """Ensure MCQs are not too similar to each other."""
    questions = [m.get('question', '').lower() for m in mcqs]
    for i in range(len(questions)):
        for j in range(i + 1, len(questions)):
            similarity = SequenceMatcher(None, questions[i], questions[j]).ratio()
            if similarity > 0.7: # Threshold for near-duplicates
                return False
    return True

def compute_confidence_score(data: Dict[str, Any]) -> Tuple[float, Dict[str, float]]:
    """
    Compute a confidence score based on multiple heuristics.
    Returns (total_score, breakdown).
    """
    tamil_ratio = calculate_tamil_ratio(data.get('tamil_simple', ''))
    alignment_score = validate_semantic_alignment(data.get('english_academic', ''), data.get('mcqs', []))
    
    # Internal breakdown for explainability
    breakdown = {
        "tamil": min(1.0, tamil_ratio / TAMIL_RATIO_THRESHOLD),
        "alignment": min(1.0, alignment_score / ALIGNMENT_THRESHOLD),
        "mcq_quality": 1.0 if validate_mcq_diversity(data.get('mcqs', [])) and validate_mcq_difficulty(data.get('mcqs', [])) else 0.5
    }
    
    # Final score starting from 1.0 with deductions
    score = 1.0
    if tamil_ratio < TAMIL_RATIO_THRESHOLD:
        score -= 0.2
    if alignment_score < ALIGNMENT_THRESHOLD:
        score -= 0.2
    if len(data.get('steps', [])) < 3:
        score -= 0.2
    if breakdown["mcq_quality"] < 1.0:
        score -= 0.2
        
    return max(0.0, min(1.0, score)), breakdown

def log_validation_errors(errors: List[str], output: Dict[str, Any]):
    """Print structured logs for validation failures."""
    if not errors:
        return
    print("\n--- VALIDATION LOGS ---")
    for err in errors:
        print(f"[ERROR] {err}")
    print(f"[STATE] Final Status: {output.get('status')}")
    print("-----------------------\n")

def get_failure_reasons(data: Dict[str, Any]) -> List[str]:
    """Identify specific failure reasons for the output."""
    reasons = []
    
    if not data:
        reasons.append("EMPTY_OUTPUT")
        return reasons

    t_ratio = calculate_tamil_ratio(data.get('tamil_simple', ''))
    if t_ratio == 0:
        reasons.append("NO_TAMIL")
    elif t_ratio < TAMIL_RATIO_THRESHOLD:
        reasons.append("LOW_TAMIL_RATIO")
        
    if validate_semantic_alignment(data.get('english_academic', ''), data.get('mcqs', [])) < ALIGNMENT_THRESHOLD:
        reasons.append("LOW_ALIGNMENT")
        
    if not validate_mcq_diversity(data.get('mcqs', [])):
        reasons.append("MCQ_DUPLICATE")
        
    if not validate_mcq_difficulty(data.get('mcqs', [])):
        reasons.append("MCQ_TRIVIAL")
        
    if len(data.get('steps', [])) < 3:
        reasons.append("STEPS_INVALID")
    
    return sorted(list(set(reasons)))

def is_content_valid(data: Dict[str, Any]) -> bool:
    """
    Production-grade content validity guard.
    Checks minimum string lengths and step counts.
    """
    tamil_simple = data.get("tamil_simple", "").strip()
    english_academic = data.get("english_academic", "").strip()
    steps = data.get("steps", [])
    
    return (
        len(tamil_simple) > 10 and
        len(english_academic) > 20 and
        len(steps) >= 2
    )

def get_cold_start_fallback() -> Dict[str, Any]:

    """Returns a safe, minimal fallback response."""
    return {
        "schema_version": "1.0",
        "status": "fallback",
        "confidence_score": 0.0,
        "failure_reasons": ["TOTAL_GENERATION_FAILURE"],
        "tamil_simple": "இந்த கருத்தை எளிமையாக விளக்க முடியவில்லை. தயவுசெய்து மீண்டும் முயற்சிக்கவும்.",
        "english_academic": "I am unable to explain this concept clearly at the moment. Please try again.",
        "steps": ["No steps available."],
        "question_decoder": {
            "question_type": "explain",
            "expected_structure": "N/A",
            "answer_template": "N/A"
        },
        "mcqs": []
    }
