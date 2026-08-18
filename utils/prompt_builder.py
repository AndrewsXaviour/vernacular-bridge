def build_concept_block(concept: str, domain: str, primary_lang: str, secondary_lang: str) -> str:
    """
    CONCEPT BLOCK CONTRACT:
    - Must produce primary language explanation in 'tamil_simple' slot.
    - Must produce secondary academic explanation in 'english_academic' slot.
    - Must produce at least 2 steps (target 4-6).
    - Must maintain strict focus on the concept.
    """
    from core.sanitizer import sanitize_user_input, get_instruction_prefix
    safe_concept = sanitize_user_input(concept)
    return f"""
{get_instruction_prefix()}
[CONCEPT_BLOCK_START]
🎯 INPUT:
CONCEPT: {safe_concept}
DOMAIN: {domain}

🌐 LANGUAGE CONFIG:
Primary (Simple): {primary_lang}
Secondary (Academic): {secondary_lang}

🔒 RULE: CONCEPT FOCUS
* Identify the MAIN CONCEPT from the input.
* The ENTIRE response MUST stay ONLY on that concept.

📘 OUTPUT REQUIREMENTS:
1. tamil_simple:
   * Write in {primary_lang}.
   * 3–5 lines of simple, school-level explanation.
2. english_academic:
   * Write in {secondary_lang}.
   * 1 strong paragraph of formal academic tone.
3. steps:
   * 4–6 logical steps breaking down the concept.
[CONCEPT_BLOCK_END]
"""

def build_decoder_block() -> str:
    """
    DECODER BLOCK CONTRACT:
    - Must return a valid question_type from the allowed enum.
    - Must provide a structured answer template.
    """
    return """
[DECODER_BLOCK_START]
📘 QUESTION DECODER REQUIREMENTS:
1. question_type: Choose from (define, explain, compare, analyze, diagram, short_note).
2. expected_structure: Logical structure for an exam answer.
3. answer_template: Pre-filled template for students to follow.
[DECODER_BLOCK_END]
"""

def build_mcq_block() -> str:
    """
    MCQ BLOCK CONTRACT:
    - Must produce 3-5 MCQs.
    - Each MCQ must have exactly 4 options.
    - Each MCQ must have 1 correct answer that matches one option exactly.
    """
    return """
[MCQ_BLOCK_START]
📘 MCQ REQUIREMENTS:
* Generate exactly 3 concept-based MCQs.
* Include: 1 Concept check, 1 Application, 1 Misconception trap.
* Each MCQ must have:
  - question (string)
  - options (exactly 4 unique strings)
  - answer (must match one option exactly)
[MCQ_BLOCK_END]
"""

def build_footer(primary_lang: str, secondary_lang: str) -> str:
    """
    FOOTER CONTRACT:
    - Enforce strict JSON output and no extra text.
    """
    return f"""
[STRICT_JSON_FOOTER_START]
📦 OUTPUT FORMAT (STRICT JSON):
{{
  "tamil_simple": "...",
  "english_academic": "...",
  "steps": ["...", "..."],
  "question_decoder": {{
    "question_type": "...",
    "expected_structure": "...",
    "answer_template": "..."
  }},
  "mcqs": [
    {{
      "question": "...",
      "options": ["...", "...", "...", "..."],
      "answer": "..."
    }}
  ]
}}

FINAL INSTRUCTION:
Return ONLY valid JSON.
Do NOT include markdown (e.g., ```json), explanations, or extra text.
Follow the schema and language mapping strictly:
- 'tamil_simple' = Primary Language ({primary_lang})
- 'english_academic' = Secondary Language ({secondary_lang})
[STRICT_JSON_FOOTER_END]
"""

def build_coach_block(question: str, student_answer: str, primary_lang: str, secondary_lang: str) -> str:
    """
    COACH BLOCK CONTRACT:
    - Evaluate academic writing based on a strict rubric.
    - Rubric: Accuracy (0-4), Structure (0-2), Completeness (0-2), Quality (0-2).
    - Feedback in primary language (Tamil + English terms).
    - Improved answer in secondary language (English academic).
    - Hidden reasoning: Evaluation performed internally but not outputted.
    """
    from core.sanitizer import sanitize_user_input, get_instruction_prefix
    safe_question = sanitize_user_input(question)
    safe_answer = sanitize_user_input(student_answer)
    return f"""
{get_instruction_prefix()}
[COACH_BLOCK_START]
🎯 INPUT:
QUESTION: {safe_question}
STUDENT_ANSWER: {safe_answer}

🌐 LANGUAGE CONFIG:
Feedback Language: {primary_lang} (Tamil + English academic terms allowed)
Academic Output Language: {secondary_lang} (Formal English)

⚖️ EVALUATION RUBRIC (STRICT):
1. Concept Accuracy (0–4): Is the scientific/academic fact correct?
2. Structure (0–2): Does it have Intro → Body → Conclusion?
3. Completeness (0–2): Are all critical points from the question covered?
4. Language Quality (0–2): Is the academic vocabulary appropriate?
Total Score = 10

🧠 HIDDEN REASONING RULE:
* Internally evaluate step-by-step using the rubric.
* DO NOT output any reasoning, justification, or rubric breakdown in the final JSON.
* Final JSON must only contain the required fields.

📘 IMPROVED_ANSWER REQUIREMENTS:
* Follow academic structure (Introduction, Body, Conclusion).
* Include all missing key points.
* Must be significantly more complete and clearer than student_answer.
* DO NOT exceed 500 characters.

📘 FEEDBACK LIST REQUIREMENTS:
* Keep strengths, weaknesses, missing_points, and improvement_suggestions strictly under 5 items each.
* Format improvement_suggestions exactly like: "Instead of [X], write [Y] because [reason]".
[COACH_BLOCK_END]
"""

def build_coach_footer(primary_lang: str, secondary_lang: str) -> str:
    """
    COACH FOOTER CONTRACT:
    - Enforce strict JSON output for the coach module.
    """
    return f"""
[STRICT_JSON_FOOTER_START]
📦 OUTPUT FORMAT (STRICT JSON):
{{
  "score": integer (0-10),
  "strengths": ["...", "..."],
  "weaknesses": ["...", "..."],
  "missing_points": ["...", "..."],
  "improvement_suggestions": ["Instead of X, write Y because Z", "..."],
  "improved_answer": "..."
}}

FINAL INSTRUCTION:
Return ONLY valid JSON.
Do NOT include markdown (e.g., ```json), explanations, or extra text.
Follow the schema and language mapping strictly:
- Feedback fields = {primary_lang}
- 'improved_answer' = {secondary_lang} (Academic)
[STRICT_JSON_FOOTER_END]
"""

def build_coach_prompt(question: str, student_answer: str, primary_lang: str = "tamil", secondary_lang: str = "english") -> str:
    """
    Assembles the coach modular prompt blocks.
    """
    prompt = (
        "You are an ELITE ACADEMIC WRITING COACH. Your job is to evaluate student answers with high rigor.\n"
        + build_coach_block(question, student_answer, primary_lang, secondary_lang)
        + build_coach_footer(primary_lang, secondary_lang)
    )
    return prompt

def build_prompt(concept: str, domain: str = "Science", primary_lang: str = "tamil", secondary_lang: str = "english") -> str:
    """
    Assembles the modular prompt blocks into a single string.
    """
    prompt = (
        "You are a STRICT bilingual academic tutor for first-generation learners.\n"
        + build_concept_block(concept, domain, primary_lang, secondary_lang)
        + build_decoder_block()
        + build_mcq_block()
        + build_footer(primary_lang, secondary_lang)
    )
    return prompt
