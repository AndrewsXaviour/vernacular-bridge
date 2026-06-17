import requests
import json
import re

def build_prompt(query: str) -> str:
    """
    Constructs a prompt for the Ollama Qwen model to generate a strict JSON response.
    """
    prompt = f"""
Analyze the following student query and provide a comprehensive educational response in STRICT JSON format.

Query: {query}

Constraints:
1. Output MUST be valid JSON.
2. Include these fields:
   - tamil_simple: A simple explanation in Tamil (min 50 chars).
   - english_academic: A formal academic explanation in English (min 80 chars).
   - steps: A list of 3-7 clear instructional steps.
   - question_decoder: Object with 'question_type' (one of: define, explain, compare, analyze, diagram, short_note), 'expected_structure', 'answer_template'.
   - mcqs: A list of 1-5 multiple choice questions, each with 'question', 'options' (exactly 4), and 'correct_answer'.

Do NOT include any text before or after the JSON block.
"""
    return prompt.strip()

def call_llm(prompt: str) -> str:
    """
    Calls the local Ollama API (qwen2.5:7b) and returns the text response.
    """
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "qwen2.5:7b",
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "")
    except requests.exceptions.RequestException as e:
        return json.dumps({
            "status": "error",
            "error_detail": str(e),
            "tamil_simple": "LLM connection failed."
        })
