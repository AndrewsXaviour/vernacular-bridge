import pytest
from pydantic import ValidationError
from models.contracts import OutputSchema, Status, MCQ, QuestionDecoder
from validators.validators import (
    calculate_tamil_ratio, 
    validate_semantic_alignment, 
    validate_mcq_diversity, 
    validate_mcq_difficulty,
    compute_confidence_score,
    get_failure_reasons
)
from utils.preprocessing import normalize_input, handle_tanglish

# Mock Data
VALID_SUCCESS_DATA = {
    "schema_version": "1.0",
    "status": "success",
    "confidence_score": 0.95,
    "failure_reasons": [],
    "tamil_simple": "ஒளிச்சேர்க்கை என்பது தாவரங்கள் சூரிய ஒளியைப் பயன்படுத்தி உணவைத் தயாரிக்கும் ஒரு செயல்முறையாகும். இது மிகவும் முக்கியமானது.", # Length > 50
    "english_academic": "Photosynthesis is the fundamental biological process by which autotrophic organisms convert light energy into chemical energy, synthesising organic compounds like glucose. This is vital for life.", # Length > 80
    "steps": ["Step 1: Absorption of light", "Step 2: Water splitting", "Step 3: Carbon fixation"],
    "question_decoder": {
        "question_type": "explain",
        "expected_structure": "Definition, Chemical Equation, Process Steps",
        "answer_template": "Photosynthesis is defined as..."
    },
    "mcqs": [
        {
            "question": "What pigment absorbs light in plants?",
            "options": ["Chlorophyll", "Hemoglobin", "Melanin", "Xanthophyll"],
            "correct_answer": "Chlorophyll"
        }
    ]
}

def test_valid_success_output_passes():
    """Verify that a perfectly formed output passes Pydantic validation."""
    model = OutputSchema(**VALID_SUCCESS_DATA)
    assert model.status == Status.SUCCESS
    assert model.schema_version == "1.0"

def test_low_tamil_ratio_triggers_retry_logic():
    """Verify that low Tamil character density can be detected."""
    bad_data = VALID_SUCCESS_DATA.copy()
    bad_data["tamil_simple"] = "This is mostly English with only a little Tamil: வணக்கம்"
    
    ratio = calculate_tamil_ratio(bad_data["tamil_simple"])
    reasons = get_failure_reasons(bad_data)
    
    assert ratio < 0.6
    assert "LOW_TAMIL_RATIO" in reasons

def test_duplicate_mcqs_rejected():
    """Verify that near-duplicate MCQ questions are flagged."""
    duplicate_mcqs = [
        {
            "question": "What is photosynthesis?",
            "options": ["A", "B", "C", "D"],
            "correct_answer": "A"
        },
        {
            "question": "What is the process of photosynthesis?", # Very similar
            "options": ["A", "B", "C", "D"],
            "correct_answer": "A"
        }
    ]
    is_diverse = validate_mcq_diversity(duplicate_mcqs)
    assert is_diverse is False

def test_fallback_relaxes_constraints():
    """Verify that Pydantic allows valid fallback structures."""
    fallback_data = VALID_SUCCESS_DATA.copy()
    fallback_data["status"] = Status.FALLBACK
    fallback_data["mcqs"] = []
    fallback_data["steps"] = ["Reduced steps."]
    
    # We still need to satisfy Pydantic's min_length
    fallback_data["tamil_simple"] = "இந்த கருத்தை விளக்க முடியவில்லை. " * 5 
    fallback_data["english_academic"] = "Unable to explain content properly. " * 5
    
    model = OutputSchema(**fallback_data)
    assert model.status == Status.FALLBACK

def test_schema_version_mismatch_fails():
    """Verify that wrong schema versions are rejected."""
    bad_version = VALID_SUCCESS_DATA.copy()
    bad_version["schema_version"] = "2.0"
    with pytest.raises(ValidationError):
        OutputSchema(**bad_version)

def test_mcq_correct_answer_not_in_options_fails():
    """Verify that MCQs must have the correct answer in their options."""
    bad_mcq = VALID_SUCCESS_DATA.copy()
    bad_mcq["mcqs"][0]["correct_answer"] = "Not An Option"
    with pytest.raises(ValidationError):
        OutputSchema(**bad_mcq)

def test_repeated_character_normalization():
    """Verify that 'helloooo' is normalized to 'helloo' (max 2 allowed)."""
    assert normalize_input("helloooo") == "helloo"
    # Testing single code point repetition for simplicity in Tamil context
    assert normalize_input("அஅஅஅ") == "அஅ"

def test_script_boundary_splitting():
    """Verify that spaces are added between different scripts."""
    assert normalize_input("தமிழ்English") == "தமிழ் English"
    assert normalize_input("Englishதமிழ்") == "English தமிழ்"

def test_confidence_score_boundaries():
    """Verify that confidence score is clamped between 0 and 1."""
    score, _ = compute_confidence_score(VALID_SUCCESS_DATA)
    assert 0 <= score <= 1

def test_tanglish_normalization():
    """Verify that common Tanglish phrases are handled."""
    assert "explain" in handle_tanglish("இத explain pannunga")

def test_alignment_failure_detected():
    """Verify that low alignment between English and MCQs is flagged."""
    data = VALID_SUCCESS_DATA.copy()
    data["english_academic"] = "This is a text about photosynthesis and plants."
    data["mcqs"] = [
        {
            "question": "What is the capital of France?",
            "options": ["Paris", "London", "Berlin", "Madrid"],
            "correct_answer": "Paris"
        }
    ]
    reasons = get_failure_reasons(data)
    assert "LOW_ALIGNMENT" in reasons

def test_mcq_trivial_rejected():
    """Verify that trivial 'What is' or 'Define' questions are flagged."""
    data = VALID_SUCCESS_DATA.copy()
    data["mcqs"] = [
        {
            "question": "What is photosynthesis?",
            "options": ["A process", "A car", "A fruit", "A city"],
            "correct_answer": "A process"
        }
    ]
    # If we have only one question and it's 'What is', it might pass diversity but fail difficulty
    is_diverse = validate_mcq_diversity(data["mcqs"])
    is_difficult = validate_mcq_difficulty(data["mcqs"])
    assert is_difficult is False

def test_retry_not_fallback_for_mcq_issue():
    """Verify that MCQ issues trigger 'retry', not 'fallback' in verifier logic."""
    from verification.verifier import run_verification_case
    # We can use the adversarial generator to get a case
    result = run_verification_case("MCQ_TRIVIAL")
    assert result["triggered_status"] == "retry"
    assert "MCQ_TRIVIAL" in result["failure_reasons"]
