import pytest
from pydantic import ValidationError
from models.coach import CoachResponse
from validators.coach_validator import normalize_coach_output, validate_coach_logic

# Mock Data
VALID_COACH_DATA = {
    "score": 9,
    "structure_feedback": "The answer is well-structured with a clear introduction and conclusion.",
    "missing_points": ["Could expand more on the specific chemical reactions."],
    "language_feedback": "உங்களது நடை மிகவும் நன்றாக உள்ளது. Proper academic terms were used.",
    "improved_answer": "Photosynthesis is a process used by plants and other organisms to convert light energy into chemical energy that, through cellular respiration, can later be released to fuel the organism's activities. This chemical energy is stored in carbohydrate molecules, such as sugars and starches, which are synthesized from carbon dioxide and water. (This is over 30 words clearly)."
}

def test_valid_coach_response_passes():
    """Verify that a valid coach response passes model validation."""
    model = CoachResponse(**VALID_COACH_DATA)
    assert model.score == 9
    assert len(model.missing_points) == 1

def test_score_out_of_bounds():
    """Verify that scores outside 0-10 are rejected."""
    bad_data = VALID_COACH_DATA.copy()
    bad_data["score"] = 11
    with pytest.raises(ValidationError):
        CoachResponse(**bad_data)

def test_missing_points_constraint_low_score():
    """Verify that score <= 5 requires at least 2 missing points."""
    bad_data = VALID_COACH_DATA.copy()
    bad_data["score"] = 4
    bad_data["missing_points"] = ["Only one point"]
    # validate_coach_logic should catch it
    with pytest.raises(ValueError, match="Score <= 5 requires at least 2 missing points"):
        validate_coach_logic(bad_data)

def test_improved_answer_length_sanity():
    """Verify that improved_answer length is enforced."""
    short_data = VALID_COACH_DATA.copy()
    short_data["improved_answer"] = "Too short answer."
    with pytest.raises(ValueError, match="Improved answer too short"):
        validate_coach_logic(short_data)

def test_score_tone_alignment():
    """Verify that low score triggers structure feedback improvement if missing."""
    data = VALID_COACH_DATA.copy()
    data["score"] = 3
    data["structure_feedback"] = "Okay."
    data["missing_points"] = ["Point 1", "Point 2"]
    validated = validate_coach_logic(data)
    assert "Needs significant improvement" in validated["structure_feedback"]

def test_normalize_coach_output():
    """Verify that normalization handles raw LLM-like dicts."""
    raw_data = {
        "score": "8",
        "structure_feedback": " Good structure ",
        "missing_points": [" Point A ", None, ""],
        "language_feedback": "Tamil feedback",
        "improved_answer": "An academic answer that is definitely long enough to pass the word count check which is thirty words."
    }
    normalized = normalize_coach_output(raw_data)
    assert normalized["score"] == 8
    assert normalized["structure_feedback"] == "Good structure"
    assert normalized["missing_points"] == ["Point A"]

def test_language_behavior_requirement():
    """Verify that language_feedback is required."""
    data = VALID_COACH_DATA.copy()
    data["language_feedback"] = ""
    with pytest.raises(ValueError, match="Language feedback is empty"):
        validate_coach_logic(data)

def test_markdown_stripping():
    """Verify that markdown characters are removed from the improved_answer."""
    raw_data = {
        "score": 8,
        "structure_feedback": "Good.",
        "missing_points": ["Point A"],
        "language_feedback": "Passed",
        "improved_answer": "### Introduction\nThis is **bold** and *italic*.\n- Point 1\n- Point 2"
    }
    normalized = normalize_coach_output(raw_data)
    # Checks: removed ###, removed **, removed *, removed - 
    expected = "Introduction\nThis is bold and italic.\nPoint 1\nPoint 2"
    assert normalized["improved_answer"] == expected
