"""
Unit tests for OutputSchema Pydantic validators (normalize_raw_llm_output).

Tests the @model_validator(mode='before') on OutputSchema that handles:
- Text field stripping and type coercion
- Steps list normalization (string → list, empty → error)
- Quality guards (empty content, generic phrases, minimum steps)
- QuestionDecoder type mapping (free-form → canonical enum)
- MCQ option dedup, correct_answer key aliasing, option count fix

20+ test cases covering all branches of the normalization logic.
"""

import pytest
from pydantic import ValidationError
from models.contracts import OutputSchema, QuestionType


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_valid(**overrides) -> dict:
    """Return a valid OutputSchema dict with optional field overrides."""
    base = {
        "tamil_simple": "ஒளிச்சேர்க்கை என்பது தாவரங்கள் சூரிய ஒளியைப் "
                        "பயன்படுத்தி உணவைத் தயாரிக்கும் ஒரு செயல்முறையாகும்.",
        "english_academic": "Photosynthesis is the fundamental biological "
                            "process by which autotrophic organisms convert "
                            "light energy into chemical energy.",
        "steps": [
            "Step 1: Absorption of light",
            "Step 2: Water splitting",
            "Step 3: Carbon fixation",
        ],
        "question_decoder": {
            "question_type": "explain",
            "expected_structure": "Definition, Chemical Equation, Process Steps",
            "answer_template": "Photosynthesis is defined as...",
        },
        "mcqs": [
            {
                "question": "What pigment absorbs light in plants?",
                "options": ["Chlorophyll", "Hemoglobin", "Melanin", "Xanthophyll"],
                "correct_answer": "Chlorophyll",
            }
        ],
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# A. Text field normalization
# ---------------------------------------------------------------------------

class TestTextFieldNormalization:
    """Tests for tamil_simple and english_academic field normalization."""

    def test_strips_whitespace(self):
        """Leading/trailing whitespace is stripped from text fields."""
        data = _make_valid(
            tamil_simple="  வணக்கம் இது ஒரு சோதனை வாக்கியம் மிக நீளமாக உள்ளது.  ",
            english_academic="  This is a test sentence with enough characters to pass validation.  ",
        )
        model = OutputSchema.model_validate(data)
        assert model.tamil_simple == "வணக்கம் இது ஒரு சோதனை வாக்கியம் மிக நீளமாக உள்ளது."
        assert model.english_academic == "This is a test sentence with enough characters to pass validation."

    def test_empty_tamil_raises(self):
        """Empty tamil_simple after stripping raises ValueError."""
        data = _make_valid(tamil_simple="")
        with pytest.raises((ValidationError, ValueError), match="Empty content"):
            OutputSchema.model_validate(data)

    def test_empty_english_raises(self):
        """Empty english_academic after stripping raises ValueError."""
        data = _make_valid(english_academic="")
        with pytest.raises((ValidationError, ValueError), match="Empty content"):
            OutputSchema.model_validate(data)

    def test_non_dict_input_returns_empty(self):
        """Non-dict input is handled gracefully (normalized to empty dict → fails validation)."""
        with pytest.raises((ValidationError, ValueError)):
            OutputSchema.model_validate("not a dict")

    def test_missing_fields_get_defaults(self):
        """Missing fields get empty-string defaults, then fail min_length."""
        data = {"steps": ["a", "b"], "question_decoder": {}, "mcqs": []}
        with pytest.raises((ValidationError, ValueError)):
            OutputSchema.model_validate(data)


# ---------------------------------------------------------------------------
# B. Steps normalization
# ---------------------------------------------------------------------------

class TestStepsNormalization:
    """Tests for steps list normalization."""

    def test_string_step_becomes_single_item_list(self):
        """A single string step is wrapped in a list, but fails min_length=2."""
        data = _make_valid(steps="Single step as a string")
        with pytest.raises((ValidationError, ValueError), match="Insufficient steps"):
            OutputSchema.model_validate(data)

    def test_empty_steps_raises(self):
        """Empty steps list raises ValueError."""
        data = _make_valid(steps=[])
        with pytest.raises((ValidationError, ValueError), match="Insufficient steps"):
            OutputSchema.model_validate(data)

    def test_single_step_raises(self):
        """Fewer than 2 steps raises ValueError."""
        data = _make_valid(steps=["Only one step"])
        with pytest.raises((ValidationError, ValueError), match="Insufficient steps"):
            OutputSchema.model_validate(data)

    def test_none_steps_becomes_empty(self):
        """None steps becomes empty list → fails validation."""
        data = _make_valid(steps=None)
        with pytest.raises((ValidationError, ValueError)):
            OutputSchema.model_validate(data)

    def test_steps_with_falsy_values_filtered(self):
        """Falsy values (None, empty string) in steps list are filtered out."""
        data = _make_valid(steps=["Step 1", None, "", "Step 2", "Step 3"])
        model = OutputSchema.model_validate(data)
        assert len(model.steps) >= 2

    def test_steps_whitespace_stripped(self):
        """Leading/trailing whitespace in each step is stripped."""
        data = _make_valid(steps=["  Step 1  ", "  Step 2  "])
        model = OutputSchema.model_validate(data)
        assert model.steps[0] == "Step 1"
        assert model.steps[1] == "Step 2"


# ---------------------------------------------------------------------------
# C. Quality guards
# ---------------------------------------------------------------------------

class TestQualityGuards:
    """Tests for generic phrase detection and empty content guards."""

    @pytest.mark.parametrize("phrase", [
        "identify the concept",
        "break down",
        "core idea",
        "key components",
        "in simple terms",
    ])
    def test_generic_phrase_in_tamil_raises(self, phrase):
        """Generic phrases in tamil_simple raise ValueError."""
        tamil = f"இந்த கருத்தை {phrase} செய்ய வேண்டும் மிக முக்கியமானது."
        data = _make_valid(tamil_simple=tamil)
        with pytest.raises((ValidationError, ValueError), match="Generic content"):
            OutputSchema.model_validate(data)

    @pytest.mark.parametrize("phrase", [
        "identify the concept",
        "break down",
        "core idea",
        "key components",
        "in simple terms",
    ])
    def test_generic_phrase_in_english_raises(self, phrase):
        """Generic phrases in english_academic raise ValueError."""
        english = f"Please {phrase} the main topic. This is an important concept in biology."
        data = _make_valid(english_academic=english)
        with pytest.raises((ValidationError, ValueError), match="Generic content"):
            OutputSchema.model_validate(data)

    @pytest.mark.parametrize("phrase", [
        "identify the concept",
        "break down",
    ])
    def test_generic_phrase_in_steps_raises(self, phrase):
        """Generic phrases in steps raise ValueError."""
        data = _make_valid(steps=[
            "Step 1: Absorption of light",
            f"Step 2: {phrase.capitalize()} the process",
        ])
        with pytest.raises((ValidationError, ValueError), match="Generic content detected in steps"):
            OutputSchema.model_validate(data)

    def test_insufficient_steps_raises(self):
        """Fewer than 2 steps raises ValueError."""
        data = _make_valid(steps=["Only one step"])
        with pytest.raises((ValidationError, ValueError), match="Insufficient steps"):
            OutputSchema.model_validate(data)


# ---------------------------------------------------------------------------
# D. Question Decoder normalization
# ---------------------------------------------------------------------------

class TestQuestionDecoderNormalization:
    """Tests for question_type mapping and normalization."""

    @pytest.mark.parametrize("input_type,expected", [
        ("process explanation", "explain"),
        ("detailed explanation", "explain"),
        ("how it works", "explain"),
        ("definition", "define"),
        ("what is", "define"),
        ("comparison", "compare"),
        ("contrast", "compare"),
        ("difference", "compare"),
        ("analysis", "analyze"),
        ("evaluation", "analyze"),
        ("diagram", "diagram"),
        ("visual representation", "diagram"),
        ("short note", "short_note"),
    ])
    def test_question_type_mapping(self, input_type, expected):
        """Free-form question types are mapped to canonical enum values."""
        data = _make_valid(question_decoder={
            "question_type": input_type,
            "expected_structure": "Structure",
            "answer_template": "Template",
        })
        model = OutputSchema.model_validate(data)
        assert model.question_decoder.question_type.value == expected

    def test_invalid_question_type_defaults_to_explain(self):
        """Unknown question types default to 'explain'."""
        data = _make_valid(question_decoder={
            "question_type": "completely unknown type",
            "expected_structure": "Structure",
            "answer_template": "Template",
        })
        model = OutputSchema.model_validate(data)
        assert model.question_decoder.question_type == QuestionType.EXPLAIN

    def test_missing_question_decoder_defaults(self):
        """Missing question_decoder gets defaults and maps to 'explain'."""
        data = _make_valid(question_decoder={})
        model = OutputSchema.model_validate(data)
        assert model.question_decoder.question_type == QuestionType.EXPLAIN

    def test_question_type_case_insensitive(self):
        """Question type mapping is case-insensitive."""
        data = _make_valid(question_decoder={
            "question_type": "PROCESS EXPLANATION",
            "expected_structure": "Structure",
            "answer_template": "Template",
        })
        model = OutputSchema.model_validate(data)
        assert model.question_decoder.question_type == QuestionType.EXPLAIN


# ---------------------------------------------------------------------------
# E. MCQ normalization
# ---------------------------------------------------------------------------

class TestMCQNormalization:
    """Tests for MCQ option dedup, correct_answer aliasing, and option count fix."""

    def test_mcq_with_answer_key_alias(self):
        """MCQs using 'answer' key instead of 'correct_answer' are normalized."""
        data = _make_valid(mcqs=[{
            "question": "What is 2+2?",
            "options": ["3", "4", "5", "6"],
            "answer": "4",
        }])
        model = OutputSchema.model_validate(data)
        assert model.mcqs[0].correct_answer == "4"

    def test_mcq_with_correct_key_alias(self):
        """MCQs using 'correct' key instead of 'correct_answer' are normalized."""
        data = _make_valid(mcqs=[{
            "question": "What is 2+2?",
            "options": ["3", "4", "5", "6"],
            "correct": "4",
        }])
        model = OutputSchema.model_validate(data)
        assert model.mcqs[0].correct_answer == "4"

    def test_mcq_duplicate_options_reduced(self):
        """Duplicate MCQ options are removed; MCQ with < 4 unique options is skipped."""
        data = _make_valid(mcqs=[{
            "question": "What is 2+2?",
            "options": ["4", "4", "5", "6"],
            "correct_answer": "4",
        }])
        model = OutputSchema.model_validate(data)
        # After dedup: ["4", "5", "6"] = 3 options → skipped (< 4 required)
        assert len(model.mcqs) == 0

    def test_mcq_duplicate_options_with_enough_unique(self):
        """MCQ with enough unique options after dedup passes validation."""
        data = _make_valid(mcqs=[{
            "question": "What is 2+2?",
            "options": ["4", "4", "5", "6", "7"],
            "correct_answer": "4",
        }])
        model = OutputSchema.model_validate(data)
        # After dedup: ["4", "5", "6", "7"] = 4 unique → passes
        assert len(model.mcqs) == 1
        assert len(model.mcqs[0].options) == 4

    def test_mcq_correct_answer_not_in_options_replaced(self):
        """If correct_answer is not in options, last option is replaced with it."""
        data = _make_valid(mcqs=[{
            "question": "What is 2+2?",
            "options": ["3", "5", "6", "7"],
            "correct_answer": "4",
        }])
        model = OutputSchema.model_validate(data)
        assert len(model.mcqs) == 1
        # Last option ("7") was replaced with correct_answer ("4")
        assert model.mcqs[0].options == ["3", "5", "6", "4"]
        assert model.mcqs[0].correct_answer == "4"

    def test_mcq_string_options_split_by_pipe(self):
        """String options split by '|' are normalized to a list."""
        data = _make_valid(mcqs=[{
            "question": "What is 2+2?",
            "options": "3|4|5|6",
            "correct_answer": "4",
        }])
        model = OutputSchema.model_validate(data)
        assert model.mcqs[0].options == ["3", "4", "5", "6"]

    def test_mcq_fewer_than_4_options_skipped(self):
        """MCQs with fewer than 4 valid options are skipped."""
        data = _make_valid(mcqs=[{
            "question": "What is 2+2?",
            "options": ["3", "4"],
            "correct_answer": "4",
        }])
        model = OutputSchema.model_validate(data)
        assert len(model.mcqs) == 0

    def test_mcq_max_5_mcqs(self):
        """At most 5 MCQs are kept."""
        mcqs = [
            {
                "question": f"Question {i}?",
                "options": [f"opt{j}" for j in range(4)],
                "correct_answer": "opt0",
            }
            for i in range(10)
        ]
        data = _make_valid(mcqs=mcqs)
        model = OutputSchema.model_validate(data)
        assert len(model.mcqs) <= 5

    def test_mcq_empty_question_skipped(self):
        """MCQs with empty question text are skipped."""
        data = _make_valid(mcqs=[
            {
                "question": "",
                "options": ["a", "b", "c", "d"],
                "correct_answer": "a",
            },
            {
                "question": "Valid question?",
                "options": ["a", "b", "c", "d"],
                "correct_answer": "a",
            },
        ])
        model = OutputSchema.model_validate(data)
        assert len(model.mcqs) == 1
        assert model.mcqs[0].question == "Valid question?"

    def test_mcq_non_dict_entries_skipped(self):
        """Non-dict entries in mcqs list are skipped gracefully."""
        data = _make_valid(mcqs=[
            "not a dict",
            42,
            {
                "question": "Valid?",
                "options": ["a", "b", "c", "d"],
                "correct_answer": "a",
            },
        ])
        model = OutputSchema.model_validate(data)
        assert len(model.mcqs) == 1

    def test_mcq_empty_correct_answer_rejected(self):
        """MCQs with empty string correct_answer are rejected (correct stays None)."""
        data = _make_valid(mcqs=[{
            "question": "What is 2+2?",
            "options": ["3", "4", "5", "6"],
            "correct_answer": "",
        }])
        with pytest.raises((ValidationError, ValueError)):
            OutputSchema.model_validate(data)

    def test_mcq_none_correct_answer_rejected(self):
        """MCQs with None correct_answer are rejected (correct_answer: str is required)."""
        data = _make_valid(mcqs=[{
            "question": "What is 2+2?",
            "options": ["3", "4", "5", "6"],
            "correct_answer": None,
        }])
        with pytest.raises((ValidationError, ValueError)):
            OutputSchema.model_validate(data)
