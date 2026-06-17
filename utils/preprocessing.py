import re

# Tanglish mapping for academic context
TANGLISH_MAP = {
    "pannunga": "explain",
    "explain pannunga": "explain",
    "solunga": "tell",
    "puriya vainga": "make understand",
    "kaatunga": "show",
    "vazhi": "way",
    "eppadi": "how",
    "enna": "what",
}

def handle_tanglish(text: str) -> str:
    """Normalize common Tanglish words/phrases to English or standardized Tamil."""
    processed = text.lower()
    for tanglish, replacement in TANGLISH_MAP.items():
        processed = re.sub(rf'\b{tanglish}\b', replacement, processed)
    
    # Handle common suffixes like -unga, -pa
    processed = re.sub(r'(\w+)unga\b', r'\1', processed)
    return processed

def normalize_input(text: str) -> str:
    """
    Robust normalization for hackathon-grade inputs.
    - Fixes repeated characters (helloooo).
    - Normalizes punctuation.
    - Splits script boundaries (TamilEnglish -> Tamil English).
    """
    if not text:
        return ""

    # 1. Repeated characters (e.g., helloooo -> hello)
    # We allow up to 2 repeated chars for legitimate words (e.g., "tool")
    text = re.sub(r'(.)\1{2,}', r'\1\1', text)

    # 2. Punctuation normalization
    text = re.sub(r'\s+([?.!,])', r'\1', text) # Remove space before punct
    text = re.sub(r'([?.!,])(?!\s)', r'\1 ', text) # Ensure space after punct

    # 3. Script boundary splitting (ensure space between Tamil and English)
    # Range for Tamil: \u0b80-\u0bff
    # Tamil followed by English
    text = re.sub(r'([\u0b80-\u0bff])([a-zA-Z])', r'\1 \2', text)
    # English followed by Tamil
    text = re.sub(r'([a-zA-Z])([\u0b80-\u0bff])', r'\1 \2', text)

    # 4. Standard cleanup
    text = " ".join(text.split())
    
    return text

def preprocess_query(query: str) -> str:
    """Full preprocessing pipeline for a student query."""
    text = normalize_input(query)
    text = handle_tanglish(text)
    return text
