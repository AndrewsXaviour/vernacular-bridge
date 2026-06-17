import random
import string

def get_base_valid_output():
    """Returns a baseline valid output dictionary."""
    return {
        "schema_version": "1.0",
        "status": "success",
        "confidence_score": 0.95,
        "failure_reasons": [],
        "tamil_simple": "இது ஒரு சாதாரண தமிழ் உரை, இது ஐம்பது எழுத்துக்களுக்கு மேல் இருக்க வேண்டும். சமூக அறிவியலில் இது முக்கியமானது.",
        "english_academic": "This is a standard academic English text that must be over eighty characters long to pass the basic constraints. It discusses fundamental concepts.",
        "steps": [
            "Step 1: Introduction to the core concept.",
            "Step 2: Detailed explanation of the process.",
            "Step 3: Conclusion and summary of findings."
        ],
        "question_decoder": {
            "question_type": "explain",
            "expected_structure": "Standard logical flow",
            "answer_template": "Identify the [concept] and explain its [impact]."
        },
        "mcqs": [
            {
                "question": "What is the primary focus of this concept?",
                "options": ["A: Focus X", "B: Focus Y", "C: Focus Z", "D: All of the above"],
                "correct_answer": "D: All of the above"
            }
        ]
    }

def generate_adversarial(case_type: str) -> dict:
    output = get_base_valid_output()
    
    if case_type == "LOW_TAMIL":
        # Tamil ratio < 0.6 (Threshold is 0.6 in validators.py)
        output["tamil_simple"] = "This text is mostly English with only a bit of தமிழ் mixed in to fail the ratio check."
        
    elif case_type == "NO_TAMIL":
        output["tamil_simple"] = "This is a fully English output which should definitely fail the Tamil ratio check."
        
    elif case_type == "MCQ_INVALID_COUNT":
        output["mcqs"][0]["options"] = ["Only one", "Only two"]
        
    elif case_type == "MCQ_DUPLICATE_OPTIONS":
        output["mcqs"][0]["options"] = ["A", "A", "B", "C"]
        
    elif case_type == "MCQ_WRONG_CORRECT":
        output["mcqs"][0]["correct_answer"] = "Option E"
        
    elif case_type == "MCQ_TRIVIAL":
        output["mcqs"] = [
            {
                "question": "Is this true?",
                "options": ["Yes", "No", "Maybe", "I don't know"],
                "correct_answer": "Yes"
            }
        ]
        
    elif case_type == "LOW_ALIGNMENT":
        output["english_academic"] = "The solar system consists of the Sun and the objects that orbit it, including eight planets."
        output["mcqs"] = [
            {
                "question": "What is the capital of France?",
                "options": ["London", "Paris", "Berlin", "Madrid"],
                "correct_answer": "Paris"
            }
        ]
        
    elif case_type == "STEPS_INVALID_COUNT":
        output["steps"] = ["Only one step."]
        
    elif case_type == "STEPS_DUPLICATE":
        output["steps"] = ["Initial step.", "Initial step.", "Final step."]
        
    elif case_type == "EXTRA_FIELDS":
        output["unauthorized_field"] = "This field should not be here."
        
    elif case_type == "RANDOM_NOISE":
        output["tamil_simple"] = "".join(random.choices(string.ascii_letters + string.punctuation, k=100))
        output["english_academic"] = "".join(random.choices(string.printable, k=200))

    elif case_type == "EMPTY_OUTPUT":
        return {}

    elif case_type == "PARTIAL_FIELDS":
        del output["tamil_simple"]
        del output["english_academic"]

    elif case_type == "WRONG_SCHEMA_VERSION":
        output["schema_version"] = "2.0"

    elif case_type == "EXTREMELY_LONG_TEXT":
        output["english_academic"] = "Word " * 2000

    elif case_type == "MIXED_SCRIPT_CORRUPTION":
        # Corrupt strings with mojibake or mixed scripts
        output["tamil_simple"] = "தமிழ் " + "ÃfÂ§Ã¢Â€Â" * 20
        
    return output
