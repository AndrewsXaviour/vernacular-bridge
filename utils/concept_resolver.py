from typing import Tuple, Optional

def resolve_concept(user_input: str) -> Tuple[str, Optional[str], str]:
    """
    Normalized concept resolver to map Tamil keywords to English academic terms.
    Returns: (english_concept, original_tamil_term, source)
    """
    text = user_input.strip().lower()

    mapping = {
        "ஒளிச்சேர்க்கை": "Photosynthesis",
        "விசை": "Force",
        "ஆற்றல்": "Energy",
        "அழுத்தம்": "Pressure",
        "செல்": "Cell",
        "உயிரணு": "Cell",
        "சுவாசம்": "Respiration",
        "ஈர்ப்பு விசை": "Gravity",
        "வேகம்": "Velocity",
        "வெப்பம்": "Heat",
        "முடுக்கம்": "Acceleration",
        "உராய்வு": "Friction",
        "அணு": "Atom",
        "மூலக்கூறு": "Molecule",
        "காந்தம்": "Magnet",
        "மின்சாரம்": "Electricity",
        "வேதியியல் வினை": "Chemical Reaction",
        "தசை": "Muscle",
        "நரம்பு": "Nerve",
        "செரிமானம்": "Digestion",
        "நிணநீர்": "Lymph",
        "ஒளி": "Light",
        "ஒலி": "Sound",
        "அலை": "Wave",
        "நிலைமின்": "Electrostatics"
    }

    for tamil, english in mapping.items():
        if tamil in text:
            return english, tamil, "resolver"

    return user_input, None, "llm"

